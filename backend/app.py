from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import json
import firebase_admin
from firebase_admin import credentials, auth
import requests
from datetime import datetime, date
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv

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
    return 'sup'


@app.route('/createUser', methods=['POST'])
def test_makeUser():
    email = request.form.get("email")
    password = request.form.get("password")

    # Empty email/pass returns error
    if (not email or not password):
        return (jsonify({"error": "Missing email or password"}), 400)

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    print("-"*40)
    print("Encrypted password:\n" + pw_hash + "\nplz dont crack :)")
    print("-"*40)

    return jsonify({
        "email": email,
        "message": "Request received"
    })



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
            todayDate = socalDate("end")
            if todayDate not in order_dictionary:
                order_dictionary[todayDate] = {
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
                selectItems = {
                    # You need to make sure these are the right data first befor finnishing
                    "appliedDiscounts": select["appliedDiscounts"],
                    "appliedTaxes": select["appliedTaxes"],
                    "displayName": select["displayName"],
                    "item": {
                        "guid": select["item"]["guid"],
                        "multiLocationId": select["item"]["multiLocationId"]
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
                    modItems = {
                    "guid": mods["guid"],
                    "displayName": mods["displayName"],
                    "item": {
                        # "guid": mods["item"]["guid"], 'NoneType' object is not subscriptable
                        # "multiLocationId": mods["item"]["multiLocationId"] 'NoneType' object is not subscriptable
                    },
                    "optionGroup": {
                        # "guid": mods["optionGroup"]["guid"], 'NoneType' object is not subscriptable
                        # "multiLocationId": mods["optionGroup"]["multiLocationId"] 'NoneType' object is not subscriptable
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
            order_dictionary[todayDate]["orders"].append(orderItem)

    return order_dictionary


@app.route('/synicdata')
def API_SYNC_Button():
    # How are we going to order this
    # Right now its just by day
    print( pipline_orders( toastAPI_orders() ) )

@app.route('/getsales')
def get_sales():
    data = pipline_orders( toastAPI_orders() )
    return data["sales"]




if __name__ == '__main__':
    print(app.url_map)
    app.run(port=5000, debug=True)