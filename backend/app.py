"""
Module Name: app.py
Date: 11/13/2026
Programmers: Jerry Ochoa, Eric Davoodi, Victor Perez

This module contains the functions api calls for the firebase database and POS data.
main functions include: Retrieving raw data from POS endpoints, Running extraction
pipelines to filter and format relevant records, and Managing database connections
to push and fetch records in Firebase.

"""
import os
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin import credentials, initialize_app, firestore
import firebase_admin
from datetime import datetime, date, time, timezone, timedelta
from datetime import date, datetime
from zoneinfo import ZoneInfo
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import bcrypt
import json
from pathlib import Path

from firebase_config import db
from toastAPI import socal_date, toastAPI_menu, toastAPI_orders
from pipelines import *
from dotenv import load_dotenv
from google.cloud.firestore_v1.base_query import FieldFilter

# API Keys
load_dotenv()
clientID = os.getenv('clientID')
clientSecret = os.getenv('clientSecret')

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

@app.route('/test')
def test():
    return "sup"


def API_token():
    """
    Function Name: API_token
    Programmer: Jerry Ochoa
    
    This function is used to retrieve the login token for the Toast POS.
    This token is needed when calling the POS API.

    """
    
    token_url = "https://ws-api.toasttab.com/authentication/v1/authentication/login" #to get the token

    payload = { ## Secret Keys from toast
        "clientId": clientID,
        "clientSecret": clientSecret,
        "userAccessType": "TOAST_MACHINE_CLIENT"
    }

    auth_response = requests.post(token_url, json=payload) #API Call
    print()
    print("Login status:", auth_response.status_code)

    if auth_response.status_code != 200:
        print(auth_response.text)
        exit()
    data = auth_response.json()
    token = data["token"]["accessToken"]
    print("-"*5 + "> Order API Successfully authenticated")

    return(token) #return this token for other functions
    
def toastAPI_menu():
    """Get the restaurant's menu data from the Toast API.

    Returns:
        dict: The Toast menu response, including menus, groups, and items.

    """
    token = API_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Toast-Restaurant-External-ID": "f8510642-286e-49c4-a5f9-31b00dd0433b" # Restaurant GUID
    }

    menu_url = "https://ws-api.toasttab.com/menus/v2/menus"
    menu_response = requests.get(menu_url, headers=headers, timeout=30)
    menu_response.raise_for_status()
    all_menu = menu_response.json()

    return all_menu

def toastAPI_labor():
    """
    Function Name: toastAPI_labor
    Programmer: Jerry Ochoa
       
    This function is used to retrieve labor data from a given date range.    
    """
    ######################################
    token = API_token()
    ######################################

    # we got the token now we can move on to the orders_URL
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Toast-Restaurant-External-ID": "f8510642-286e-49c4-a5f9-31b00dd0433b" #Restaurant GUID
    }
#########################################################################################################################################
    
    # Labor Entries
    labor_url = "https://ws-api.toasttab.com/labor/v1/timeEntries"

    ## so we can loops through the pages
    params = {
        "startDate": socal_date("start"),
        "endDate": socal_date("end"),
    }

    labor_response = requests.get(labor_url, headers=headers,params=params) #API Call
    all_labor = labor_response.json()

    return all_labor

def toastAPI_orders():
    """
    Function Name: toastAPI_orders
    Programmer: Jerry Ochoa
        
    This function is used to retrieve sales data from a given date range.
    The JSON only returns a page of 100 orders at a time so this function
    loops through page by page putting all the orders into an array.
    This is so we can later extract the needed information through a pipeline.
    """
    ######################################
    token = API_token()
    ######################################

    # with token we can login and use orders_URL
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Toast-Restaurant-External-ID": "f8510642-286e-49c4-a5f9-31b00dd0433b" #Restaurant GUID
    }

    ############################################################
    all_orders = [] # gets orders from all pages
    ############################################################

    ## so we can loops through the pages
    pageNumber = 1
    while True:            
        params = {
            "startDate": socal_date("start"),
            "endDate": socal_date("end"),
            "pageSize": 100,
            "page": pageNumber
        }
    
        orders_url = "https://ws-api.toasttab.com/orders/v2/ordersBulk"
        orders_response = requests.get(orders_url, headers=headers,params=params) #API Call
        orders = orders_response.json()
        all_orders.extend(orders)

        nextPage_Check = orders_response.headers.get("link", "")
        if 'rel="next"' not in nextPage_Check:
            break
        pageNumber += 1

    # Returns JSON
    return all_orders


@app.route('/synicdata')
def API_SYNC_Button():
    # Get the last date that was added to the DB
    # Add all days till the current Day
    # If Date exist update date by adding the new orders to it(last date added == today) - if we missed some data before store close

    # test = toastAPI_orders("2026-09-01", "2026-10-01")

    # order_dictionary = pipeline_orders( toastAPI_orders("2026-11-12", "2026-11-12") ) #gunicorn is not keeping up with long date ranges
    order_dictionary = pipeline_orders( toastAPI_orders() )
    upload_orders(order_dictionary, "business_abc123")
    print("data added to firebase DB !")

    return order_dictionary

    menu_dictionary = pipeline_menu(toastAPI_menu())

@app.route('/getmenu')
def get_menu():
    data = pipeline_menu(toastAPI_menu())
    return data["menuItems"]


# @app.route('/pushsales')
# def push_sales():
#     data = pipeline_orders( toastAPI_orders() )
#     return data["sales"]


def graph_data_totals(firebase_data, group_by=None):
    """Return sales, tips, and tax for every check in the order data.

    Toast order records can contain multiple checks, so each check is returned
    as its own result. Sales comes from the check amount, tips are summed from
    its payments, and tax is summed from its selections.
    """
    order_totals = []
    grouped_totals = {}

    for order in firebase_data:
        for check in order.get("checks", []):
            sales = check.get("amount") or 0
            tips = sum(
                payment.get("tipAmount") or 0
                for payment in check.get("payments", [])
            )
            tax = sum(
                selection.get("tax") or 0
                for selection in check.get("selections", [])
            )

            check_totals = {
                "sales": round(sales, 2),
                "tips": round(tips, 2),
                "tax": round(tax, 2),
            }

            if group_by is None:
                order_totals.append(check_totals)
                continue

            if group_by not in {"month", "week", "weekday"}:
                raise ValueError("group_by must be 'month', 'week', or 'weekday'")

            opened_date = order.get("openedDate") or order.get("businessDate")
            if not opened_date:
                raise ValueError("Orders need openedDate or businessDate to group by date")
            order_date = datetime.fromisoformat(opened_date.replace("Z", "+00:00")).date()

            if group_by == "month":
                key = order_date.strftime("%Y-%m")
            elif group_by == "week":
                key = (order_date - timedelta(days=order_date.weekday())).isoformat()
            else:
                key = order_date.strftime("%A")

            group = grouped_totals.setdefault(
                key, {"orders": 0, "sales": 0.0, "tips": 0.0, "tax": 0.0}
            )
            group["orders"] += 1
            for field in ("sales", "tips", "tax"):
                group[field] = round(group[field] + check_totals[field], 2)

    return grouped_totals if group_by is not None else order_totals


def load_firebase_data():
    """Load the checked-in Firebase export used by the sales endpoint."""
    data_path = Path(__file__).resolve().with_name("firebase_data_jerry.json")
    with data_path.open("r", encoding="utf-8") as file:
        return json.load(file)

@app.route('/getSales')
def get_sales(group_by=None):
    """ 
    this function will take in a range of dates from the DB(Y) and how to group the information(X).

    (Y) - sales, taxes, tips ...
    (X) - Month, day or date, week, weekday

        
    """
    # start = date(2026,11,9).isoformat()
    # end = date(2026,11,10).isoformat()

    # query = firestore.client().collection("businesses/business_abc123/orders")
    # query = query.where(
    #     filter=FieldFilter("createdDate", ">=", start)
    # )
    # query = query.where(
    #     filter=FieldFilter("createdDate", "<", end)
    # )
    # firebaseData = query.stream()

    # Flask supplies query parameters through request.args. The optional
    # argument keeps the function convenient to call directly as well.
    group_by = group_by or request.args.get("group_by")
    firebase_data = load_firebase_data()
    return jsonify(graph_data_totals(firebase_data, group_by))


def upload_orders(order_dictionary, business_id):

    orders_ref = (
        db.collection("businesses")
          .document(business_id)
          .collection("orders")
    )

    for date_data in order_dictionary.values():
        for order_id, order_data in date_data["orders"].items():

            orders_ref.document(order_id).set(order_data)



if __name__ == '__main__':
    print(app.url_map)
    app.run(port=5000, debug=True)
