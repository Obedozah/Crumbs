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



def pipeline_orders(ordersJSON):
    """
    Function Name: pipeline_orders
    Programmer: Jerry Ochoa
            
    This function is used to filter and organize the important data from
    the JSON information given to us by the Toast API call. After this data
    is orgainized it can then be added into our database.
    """
    print("Creating Dictionary . . . .")

    order_dictionary = {}

    for order in ordersJSON:
        orderDate = socal_date(None, order["checks"][0]["createdDate"])
        ## As long as the order is not voided
        if order["voided"] == False: 
            ## If the date is not in the dictionary yet
            # todayDate = order["openedDate"]
            if orderDate not in order_dictionary:
                order_dictionary[orderDate] = {
                    "orders": {},
                    # "labor": [],                
                }

            # One Order - Level#1
            orderItem = {
                        "businessDate": order["businessDate"],
                        "checks": [
                            {
                                "amount": order["checks"][0]["amount"], # check ammount
                                "appliedDiscounts": order["checks"][0]["appliedDiscounts"],
                                "createDate": order["checks"][0]["createdDate"],
                                "customer": order["checks"][0]["customer"], # prob wont need
                                "payments": [],
                                "selections": [],
                                "tabName": order["checks"][0]["tabName"],
                                "taxAmount": order["checks"][0]["taxAmount"],
                                "taxExempt": order["checks"][0]["taxExempt"],
                                "totalAmount": order["checks"][0]["totalAmount"]
                            }
                        ],
                        "closedDate": order["checks"][0]["closedDate"],
                        "createdDate": orderDate,
                        "guid": order["guid"],
                        "modifiedDate": order["modifiedDate"],
                        "openedDate": order["openedDate"],
                        "server": {"guid": order["server"]["guid"]},
                        "source": order["source"],
            }

            # Array of payments in a orders - Level#3 (Orders->checks->payments)
            for payment in order["checks"][0].get("payments") or []:
                
                paymentItem = {
                    "guid": payment["guid"],
                    "amount": payment["amount"],
                    "surchargeAmount": payment["surchargeAmount"],
                    "tipAmount": payment["tipAmount"],
                    "checkGuid": payment["checkGuid"],
                    "orderGuid": payment["orderGuid"],
                    "originalProcessingFee": payment["originalProcessingFee"],
                    "paymentStatus": payment["paymentStatus"],
                    "refund": payment["refund"],
                    "refundStatus": payment["refundStatus"],
                    # "server": {"guid": payment["server"]["guid"]}, 'NoneType' object is not subscriptable
                    "type": payment["type"]
                }
                orderItem["checks"][0]["payments"].append(paymentItem)

            for select in order["checks"][0].get("selections") or []:

                # to fix this error: 'NoneType' object is not subscriptable
                item = select.get("item") or {}
                item_group = select.get("itemGroup") or {}
                ##############

                selectItems = {
                    # You need to make sure these are the right data first befor finnishing
                    "appliedDiscounts": select["appliedDiscounts"],
                    "appliedTaxes": select["appliedTaxes"],
                    "displayName": select["displayName"],
                    "item": {
                        "guid": item.get("guid"), #select["item"]["guid"],
                        "multiLocationId": item.get("multiLocationId") #select["item"]["multiLocationId"]
                        },
                    "itemGroup": {
                        "guid": item_group.get("guid"),
                        "multiLocationId": item_group.get("multiLocationId")
                    },
                    "modifiers": [], # Need to append data to this as well,
                    "preDiscountPrice": select["preDiscountPrice"],
                    "price": select["price"],
                    "quantity": select["quantity"],
                    "receiptLinePrice": select["receiptLinePrice"],
                    "tax": select["tax"]                        
                    }

                for mods in select.get("modifiers") or []:

                    # to fix this error: 'NoneType' object is not subscriptable
                    item = mods.get("item") or {}
                    optionGroup = mods.get("optionGroup") or {}
                    ##############
                    
                    modItems = {
                    "guid": mods["guid"],
                    "displayName": mods["displayName"],
                    "item": {
                        "guid": item.get("guid"), #select["mods"]["item"]["guid"],
                        "multiLocationId": item.get("multiLocationId") #select["mods"]["item"]["multiLocationId"]
                    },
                    "optionGroup": {
                        "guid": optionGroup.get("guid"), # mods["optionGroup"]["guid"], 'NoneType' object is not subscriptable
                        "multiLocationId": optionGroup.get("multiLocationId")  # mods["optionGroup"]["multiLocationId"] 'NoneType' object is not subscriptable
                    },
                    "price": mods["price"],
                    "quantity": mods["quantity"],
                    "receiptLinePrice": mods["receiptLinePrice"],
                    "modifiers": [],
                    }

                    for innerMods in mods["modifiers"]:
                        #1 Adding sub mods to mods
                        modItems["modifiers"].append(innerMods)

                    #2 Adding mods to selections[]
                    selectItems["modifiers"].append(modItems)

                #3 Adding to selections to check[]     
                orderItem["checks"][0]["selections"].append(selectItems)

            #4 Adding the orders to the main Dictionary
            # order_dictionary[socal_date()]["orders"].append(orderItem)
            order_dictionary[orderDate]["orders"][orderItem["guid"]] = orderItem

    return order_dictionary


def pipeline_menu(menuJSON):
    """Turns a Toast menu response into a dictionary of menu items keyed by GUID.

    Args:
        menuJSON (dict): Toast menu response containing a menus list.
            Items must include guid and name.

    Returns:s
        dict: Menu items grouped by GUID, with each item's Toast ID, name,
            category, price, and active status.
    """
    menu_dictionary = {"menuItems": {}}

    def add_group(group):
        """Recursively add a group's items and subgroups to menu_dictionary."""
        for item in group.get("menuItems") or []:
            itemId = item["guid"]
            active = bool(item.get("visibility"))
            if itemId in menu_dictionary["menuItems"]:
                menu_dictionary["menuItems"][itemId]["active"] |= active
                continue

            salesCategory = item.get("salesCategory") or {}
            menu_dictionary["menuItems"][itemId] = {
                "toastItemId": itemId,
                "name": item["name"],
                "category": salesCategory.get("name") or group.get("name"),
                "price": item.get("price"),
                "active": active,
            }

        for subgroup in group.get("menuGroups") or []:
            add_group(subgroup)

    for menu in menuJSON["menus"]:
        add_group(menu)

    return menu_dictionary


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
