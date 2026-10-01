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

#     if (email ==" " or password==" "):
#         print (jsonify({"error": "Missing email or password"}), 400)
        
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
    




if __name__ == '__main__':
    print(app.url_map)
    app.run(port=5000, debug=True)