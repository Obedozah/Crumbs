import os
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv


load_dotenv()
clientID = os.getenv("clientID")
clientSecret = os.getenv("clientSecret")


def socal_date(startend=None, given_date=None):
    """
    Function Name: socal_date
    Programmer: Jerry Ochoa
        
    Returns a date or timestamp using the America/Los_Angeles timezone.
    
    Examples:
        socal_date()                       -> "2026-11-15"
        socal_date("start")                -> today's start timestamp
        socal_date("end")                  -> today's end timestamp
        socal_date("start", "2026-11-09")  -> November 9 start timestamp
        socal_date("end", "2026-11-09")    -> November 9 end timestamp
        socal_date(None, "2026-11-09T20:26:00.623+0000")  ->  2026-11-09

    """
    socal_tz = ZoneInfo("America/Los_Angeles")

    if given_date is None:
        target_date = datetime.now(socal_tz).date()

    elif isinstance(given_date, str):
        try:
            # Handles timestamps such as:
            # 2026-11-09T20:26:00.623+0000
            parsed_datetime = datetime.fromisoformat(
                given_date.replace("Z", "+00:00")
            )

            # Convert timestamp to Southern California time
            if parsed_datetime.tzinfo is not None:
                target_date = parsed_datetime.astimezone(
                    socal_tz
                ).date()
            else:
                target_date = parsed_datetime.date()

        except ValueError:
            # Handles a date such as: 2026-11-09
            target_date = datetime.strptime(
                given_date, "%Y-%m-%d"
            ).date()

    elif isinstance(given_date, datetime):
        target_date = given_date.astimezone(socal_tz).date()

    elif isinstance(given_date, date):
        target_date = given_date

    else:
        raise ValueError(
            "Date must be in YYYY-MM-DD or timestamp format"
        )

    if startend is None:
        return target_date.isoformat()

    if startend == "start":
        local_datetime = datetime.combine(
            target_date,
            time.min,
            tzinfo=socal_tz
        )

    elif startend == "end":
        local_datetime = datetime.combine(
            target_date,
            time(23, 59, 59, 999000),
            tzinfo=socal_tz
        )

    else:
        raise ValueError("Pick 'start' or 'end'")

    return (
        local_datetime
        .astimezone(ZoneInfo("UTC"))
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


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


def toastAPI_orders(start_date=None, end_date=None):
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

    if start_date is None and end_date is None:
        startDate = socal_date("start")
        endDate = socal_date("end")
    else:
        startDate = socal_date("start", start_date)
        endDate = socal_date("end", end_date)

    ## so we can loops through the pages
    pageNumber = 1
    while True:            
        params = {
            "startDate": startDate,
            "endDate": endDate,
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
