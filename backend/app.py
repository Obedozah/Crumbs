from flask import Flask, g
from flask_cors import CORS
from firebaseAuth import require_firebase_user

app = Flask(__name__)
CORS(app)

@app.route('/test')
def test():
    return 'sup'


@app.route('/me')
@require_firebase_user
def me():
    return {
        'uid': g.firebase_user['uid'],
        'email': g.firebase_user.get('email'),
    }

if __name__ == '__main__':
    app.run(debug=True)