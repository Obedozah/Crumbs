from firebase_config import db
from zoneinfo import ZoneInfo
from datetime import datetime, date, timezone, timedelta


def socal_date(startend=None):
    """
    Function Name: socal_date
    Programmer: Jerry Ochoa

    This function is used to return a formatted current date to use when calling the POS API
    that requires a date range. This function takes in one text parameter of start or end that will
    return the date with a start of the day or end of the day time stamp. Leaving the parameter empty
    will return the current date without a time stamp.

    """
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
        currentDate = socal_date() 
        ## As long as the order is not voided
        if order["voided"] == False: 
            ## If the date is not in the dictionary yet
            # todayDate = order["openedDate"]
            if currentDate not in order_dictionary:
                order_dictionary[currentDate] = {
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
                        "createdDate": currentDate,
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
            # order_dictionary[socal_date()]["orders"].append(orderItem)
            order_dictionary[currentDate]["orders"][orderItem["guid"]] = orderItem

    return order_dictionary

def upload_orders(order_dictionary, business_id):

    orders_ref = (
        db.collection("businesses")
          .document(business_id)
          .collection("orders")
    )

    for date_data in order_dictionary.values():
        for order_id, order_data in date_data["orders"].items():

            orders_ref.document(order_id).set(order_data)

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

def pipeline_TimeEntries(timeJSON):
    print("Creating Dictionary . . . .")

    entries_dictionary = {}

    for entry in timeJSON:

        # Get the employee ID
        employee = entry.get("employeeReference") or {}
        employee_id = employee.get("guid")

        # Get associated time entry ID
        time_entry_id = entry.get("guid")

        # Skip entries without required IDs
        # since these are needed no point of
        # using entries without one or the other
        if not employee_id or not time_entry_id:
            continue

        # Skip deleted entries
        if entry.get("deleted") == True:
            continue

        entriesItem = {
            "employeeId": employee_id,
            "toastTimeEntryId": time_entry_id,
            "businessDate": entry.get("businessDate"),
            "clockIn": entry.get("inDate"),
            "clockOut": entry.get("outDate"),
            "regularHours": entry.get("regularHours") or 0,
            "overtimeHours": entry.get("overtimeHours") or 0,
            "hourlyWage": entry.get("hourlyWage")
        }

        # Add to dictionary using Toast GUID
        entries_dictionary[time_entry_id] = entriesItem

    return entries_dictionary

# def upload_TimeEntries(entries_dictionary, business_id):

# Todo
def pipeline_Labor(laborJSON):
    print("Creating Dictionary . . . .")
    
    labor_dictionary = {}

    for entry in laborJSON:

        # get the employee id's
        employee = entry.get("employeeReference") or {}
        employee_id = employee.get("guid")

        # get associated time entries
        time_entry_id = entry.get("guid")

        # Skip deleted entries
        if entry.get["deleted"] == True:
            continue

        laborItem = {

        }
        
        # add to dictionary using toast guid
        labor_dictionary[time_entry_id] = laborItem

    return labor_dictionary

# todo
# def update_labor():
