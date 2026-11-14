from datetime import date, datetime
import json
from zoneinfo import ZoneInfo

import bcrypt
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

from firebase_config import db
import os
from dotenv import load_dotenv

# API Keys
load_dotenv()
clientID = os.getenv('clientID')
clientSecret = os.getenv('clientSecret')

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

@app.route('/test')
def test():
    return "sup"


def socalDate(startend=None):
    socal_tz = ZoneInfo("America/Los_Angeles")
    today = datetime.now(socal_tz)

    if startend is None:
        return today.strftime("%Y-%m-%d")

    if startend == "start":
        socal_date = today.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif startend == "end":
        socal_date = today.replace(
            hour=23, minute=59, second=59, microsecond=999000
        )
    else:
        raise ValueError("Pick 'start' or 'end'")

    return (
        socal_date.astimezone(ZoneInfo("UTC"))
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def API_token():
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
        "startDate": socalDate("start"),
        "endDate": socalDate("end"),
    }

    labor_response = requests.get(labor_url, headers=headers,params=params) #API Call
    all_labor = labor_response.json()

    return all_labor


def toastAPI_orders():
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
            "startDate": socalDate("start"),
            "endDate": socalDate("end"),
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


def pipline_orders(ordersJSON):
    print("Creating Dictionary . . . .")

    order_dictionary = {}

    for order in ordersJSON:
        ## As long as the order is not voided
        if order["voided"] == False: 
            ## If the date is not in the dictionary yet
            # todayDate = order["openedDate"]
            if socalDate() not in order_dictionary:
                order_dictionary[socalDate()] = {
                    "orders": [],
                    # "labor": [],                
                }

            # One Order - Level#1
            orderItem = {
                        "businessDate": order["businessDate"],
                        "checks": [
                            {
                                "amount": order["checks"][0]["amount"], # check ammount
                                "appliedDiscounts": order["checks"][0]["appliedDiscounts"],
                                "closedDate": order["checks"][0]["closedDate"],
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
                        "createdDate": order["checks"][0]["createdDate"],
                        "guid": order["guid"],
                        "modifiedDate": order["modifiedDate"],
                        "openedDate": order["openedDate"],
                        "server": {"guid": order["server"]["guid"]},
                        "source": order["source"],
            }

            # Array of payments in a orders - Level#3 (Orders->checks->payments)
            for payment in order["checks"][0]["payments"]:
                
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

            for select in order["checks"][0]["selections"]:

                # to fix this error: 'NoneType' object is not subscriptable
                item = select.get("item") or {}
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
                        "guid": select["itemGroup"]["guid"],
                        "multiLocationId": select["itemGroup"]["multiLocationId"]
                    },
                    "modifiers": [], # Need to append data to this as well,
                    "preDiscountPrice": select["preDiscountPrice"],
                    "price": select["price"],
                    "quantity": select["quantity"],
                    "receiptLinePrice": select["receiptLinePrice"],
                    "tax": select["tax"]                        
                    }

                for mods in select["modifiers"]:

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
            order_dictionary[socalDate()]["orders"].append(orderItem)

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

    order_dictionary = pipline_orders( toastAPI_orders() )
    upload_orders(order_dictionary, "business_abc123")

    menu_dictionary = pipeline_menu(toastAPI_menu())

@app.route('/getmenu')
def get_menu():
    data = pipeline_menu(toastAPI_menu())
    return data["menuItems"]


@app.route('/getsales')
def get_sales():
    data = pipline_orders( toastAPI_orders() )
    return data["sales"]


if __name__ == '__main__':
    print(app.url_map)
    app.run(port=5000, debug=True)





def upload_orders(order_dictionary, business_id):

    orders_ref = (
        db.collection("businesses")
          .document(business_id)
          .collection("orders")
    )

    for date_data in order_dictionary.values():
        for order_id, order_data in date_data["orders"].items():

            orders_ref.document(order_id).set(order_data)

