from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import bcrypt
import json
import firebase_admin
from firebase_admin import firestore
import requests
from datetime import datetime, date
from zoneinfo import ZoneInfo
from firebase_config import db

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

db = firestore.client()

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
                    "orders": 0,
                    "sales": 0.0,
                    "cctips": 0.0,
                    "tax": 0.0,
                    "labor": 0.0,
                }

            order_dictionary[todayDate]["orders"] +=1

            addsale = order["checks"][0]["totalAmount"]
            order_dictionary[todayDate]["sales"] = round(order_dictionary[todayDate]["sales"] + addsale, 2)

            addtax = order["checks"][0]["taxAmount"]
            order_dictionary[todayDate]["tax"] = round(order_dictionary[todayDate]["tax"] + addtax, 2)

            tipsExist = order["checks"][0]["payments"]
            if tipsExist:
                addtips = tipsExist[0]["tipAmount"]
                order_dictionary[todayDate]["cctips"] = round(order_dictionary[todayDate]["cctips"] + addtips, 2)

    return order_dictionary


@app.route('/synicdata')
def API_SYNC_Button():
    # How are we going to order this
    # Right now its just by day
    print( pipline_orders( toastAPI_orders() ) )




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

