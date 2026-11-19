# import os
# from firebase_admin import credentials, firestore, initialize_app
# from firebase_admin import credentials, initialize_app, firestore
# import firebase_admin
from datetime import datetime, date, timezone, timedelta
from datetime import date, datetime
from zoneinfo import ZoneInfo
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# import requests
# import bcrypt
# import json

# from firebase_config import db
# from dotenv import load_dotenv
# from google.cloud.firestore_v1.base_query import FieldFilter



def socal_date(startend=None, given_date=None):
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

print(socal_date(None, "2026-11-09T20:26:00.623+0000"))