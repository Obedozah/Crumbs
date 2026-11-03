from firebase_admin import credentials, auth
from flask import Flask, request, jsonify
from datetime import datetime, date
from zoneinfo import ZoneInfo
from flask_cors import CORS
import firebase_admin
import requests
import bcrypt
import json
from firebase_admin import firestore
from firebase_config import db
import os
from dotenv import load_dotenv

# API Keys
load_dotenv()
clientID = os.getenv('clientID')
clientSecret = os.getenv('clientSecret')

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

db = firestore.client()

# firebase connection
# cred = credentials.Certificate("serviceAccountKey.json") # Add Key
# firebase_admin.initialize_app(cred)

@app.route('/test')
def test():
    return "sup"


def socalDate(startend):
    #this function gives back the start and end of todays date. depending on what your asking for
    today = date.today()
    date_array = []
    tempVal = ""
    for index,char in enumerate(str(today)):
        if char == "-" or index==len(str(today))-1:
            date_array.append(int(tempVal))
            tempVal=""
        else:
            tempVal = tempVal + char
    
    if startend == "start":
        startInput = datetime(date_array[0], date_array[1], date_array[2], 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles")) # 2026, 1, 1
        socal_date = startInput.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
    elif startend =="end":
        endInput = datetime(date_array[0], date_array[1], date_array[2], 23, 59, 59, 999000, tzinfo=ZoneInfo("America/Los_Angeles"))
        socal_date = endInput.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    else:
        print("** Pick 'start' or 'end' - socal(todayDate, startend) **")

    return socal_date


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

                server = payment.get("server") or {} 
                
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
                    "server": {
                        "guid": server.get("guid"), #payment["server"]["guid"] 'NoneType' object is not subscriptable
                    }, 
                    "type": payment["type"]
                }
                orderItem["checks"][0]["payments"].append(paymentItem)

            for select in order["checks"][0]["selections"]:

                #### 'NoneType' fix
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

                    #### 'NoneType' fix
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


@app.route('/synicdata')
def API_SYNC_Button():
    # Get the last date that was added to the DB
    # Add all days till the current Day
    # If Date exist update date by adding the new orders to it(last date added == today) - if we missed some data before store close

    print( pipline_orders( toastAPI_orders() ) ) # change this to push to DB



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

