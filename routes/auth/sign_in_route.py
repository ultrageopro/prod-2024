from flask import Blueprint, jsonify, Response, request, Request
from typing import Optional, Any
import jwt
import datetime
import bcrypt
from ...database.user_database import UserPostgreClient

import time


class SignInRoute:
    def __init__(self, user_database: UserPostgreClient) -> None:
        self.blueprint = Blueprint("login", __name__)
        self.user_database = user_database

        @self.blueprint.route("/api/auth/sign-in/", methods=["POST"])
        def sign_in() -> tuple[Response, int]:
            # Route for user login
            return self.__user_sign_in(request)

    def __user_sign_in(self, request: Request) -> tuple[Response, int]:

        content_type = request.headers.get("Content-Type")
        if content_type != "application/json":
            # Check if content type is JSON
            return jsonify({"reason": "Bad content type"}), 400

        # Route for user login
        request_data = request.get_json()

        login = request_data.get("login")
        password = request_data.get("password")

        if login is None or password is None:
            return jsonify({"reason": "Login and password are required"}), 401

        user = self.user_database.get_user_data(login)
        if user is None:
            return jsonify({"reason": "User not registered"}), 401

        if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return jsonify({"reason": "Incorrect password"}), 401

        token: str = jwt.encode(
            {
                "login": user.login,
                "password": user.password,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            },
            "secret",
            algorithm="HS256",
        )

        return jsonify({"token": token}), 200
