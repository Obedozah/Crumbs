import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import bcrypt
import json
import firebase_admin
from firebase_admin import credentials, auth
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

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


# @app.route("/createUser", methods=['POST'])
# def createUser():
#     data = request.get_json()
#     email = data.get("email")
#     password = data.get("password")
        
#     pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

#     try:
#         newUser = auth.create_user(
#             email = data.get("email"),
#             password = pw_hash
#         )

#         return jsonify({
#             "message": "User created successfully!",
#             "uid": newUser.uid,
#             "email": newUser.email
#         }), 201
    
#     except auth.EmailAlreadyExistsError:
#         return jsonify({"error": "This email is already registered."}), 400
    

### Change these dates for your analysis - This way get a more accurate Date/Time for LA 
# [ Year, Month, Day ] 
todayDate = [2026,10,05]

def socalDate(todayDate, startend):
    if startend == "start":
        startInput = datetime(startDate[0], startDate[1], startDate[2], 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles")) # 2026, 1, 1
        socal_date = startInput.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
    elif startend =="end":
        endInput = datetime(endDate[0], endDate[1], endDate[2], 23, 59, 59, 999000, tzinfo=ZoneInfo("America/Los_Angeles"))
        socal_date = endInput.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    else:
        print("** Pick 'start' or 'end' - socal(todayDate, startend) **")

    return socal_date


def toastAPI_labor(startDate, endDate):
    
    ######################################
    token = "USE API_TOKEN()"
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

    ### Change these dates for your analysis - This way get a more accurate Date/Time for LA - Year, Month, Day
    startInput = datetime(startDate[0], startDate[1], startDate[2], 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles")) # 2026, 1, 1
    endInput = datetime(endDate[0], endDate[1], endDate[2], 23, 59, 59, 999000, tzinfo=ZoneInfo("America/Los_Angeles"))

    start = startInput.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    end = endInput.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    ## so we can loops through the pages
    params = {
        "startDate": start,
        "endDate": end,
    }

    labor_response = requests.get(labor_url, headers=headers,params=params) #API Call
    all_labor = labor_response.json()

    return all_labor

def toastAPI_orders(startDate, endDate):
    ######################################
    token = "USE API_TOKEN()"
    ######################################

    # with token we can login and use orders_URL
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Toast-Restaurant-External-ID": "f8510642-286e-49c4-a5f9-31b00dd0433b" #Restaurant GUID
    }

    ### Change these dates for your analysis - This way get a more accurate Date/Time for LA - Year, Month, Day
    startInput = datetime(startDate[0], startDate[1], startDate[2], 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles")) # 2026, 1, 1
    endInput = datetime(endDate[0], endDate[1], endDate[2], 23, 59, 59, 999000, tzinfo=ZoneInfo("America/Los_Angeles"))
    
    start = startInput.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    end = endInput.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    ############################################################
    all_orders = [] # gets orders from all pages
    ############################################################

    ## so we can loops through the pages
    pageNumber = 1
    while True:            
        params = {
            "startDate": start,
            "endDate": end,
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


if __name__ == '__main__':
    print(app.url_map)
    app.run(port=5000, debug=True)