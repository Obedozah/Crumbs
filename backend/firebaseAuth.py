from functools import wraps

from firebase_admin import auth, get_app, initialize_app
from firebase_admin.exceptions import FirebaseError
from flask import g, jsonify, request


def require_firebase_user(view):
	@wraps(view)
	def wrapped(*args, **kwargs):
		authorization = request.headers.get("Authorization", "")
		parts = authorization.split()
		if len(parts) != 2 or parts[0].lower() != "bearer":
			return jsonify({"error": "Missing bearer token"}), 401
		token = parts[1]

		try:
			try:
				get_app()
			except ValueError:
				initialize_app()

			g.firebase_user = auth.verify_id_token(token)
		except (FirebaseError, ValueError):
			return jsonify({"error": "Invalid or expired token"}), 401

		return view(*args, **kwargs)

	return wrapped
