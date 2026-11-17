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
import requests
import bcrypt
import json
from flask import Flask, request, jsonify
from datetime import datetime, date, timezone, timedelta
import json
from zoneinfo import ZoneInfo

import bcrypt
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, request
from flask_cors import CORS
# from firebase_admin import credentials, initialize_app, firestore
import requests

from pipelines import *
from dotenv import load_dotenv
from google.cloud.firestore_v1.base_query import FieldFilter

# API Keys
load_dotenv()
clientID = os.getenv('clientID')
clientSecret = os.getenv('clientSecret')

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


# firebase connection
# cred = credentials.Certificate("serviceAccountKey.json") # Add Key
# firebase_admin.initialize_app(cred)

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

    order_dictionary = pipeline_orders( toastAPI_orders() )
    upload_orders(order_dictionary, "business_abc123")
    # upload_orders(order_dictionary, "business_abc123")
    return order_dictionary

    menu_dictionary = pipeline_menu(toastAPI_menu())

@app.route('/getmenu')
def get_menu():
    data = pipeline_menu(toastAPI_menu())
    return data["menuItems"]


@app.route('/pushsales')
def push_sales():
    data = pipeline_orders( toastAPI_orders() )
    return data["sales"]


@app.route('/getSales')
def get_sales():
    start = datetime(2026,10,3, tzinfo=timezone.utc)
    end = datetime(2026,11,9, tzinfo=timezone.utc)


    query = firestore.client().collection("businesses/business_abc123/orders")
    query = query.where(
        filter=FieldFilter("createdDate", ">=", start)
    )
    query = query.where(
        filter=FieldFilter("createdDate", "<", end)
    )
    docs = query.stream()

    return jsonify([
        {"id": doc.id, **doc.to_dict()}
        for doc in docs
    ])


if __name__ == '__main__':
    print(app.url_map)
    app.run(port=5000, debug=True)