from flask import Blueprint, jsonify, request, Response, Request
import re
import bcrypt
from psycopg2.errors import UniqueViolation
from typing import Any, Optional
from ...modules.user import User
from ...database.user_database import UserPostgreClient
from ...database.countries_database import CountryPostgreClient


class RegisterRoute:
    def __init__(
        self, user_database: UserPostgreClient, country_database: CountryPostgreClient
    ) -> None:
        self.blueprint = Blueprint("register", __name__)
        self.user_database = user_database
        self.country_database = country_database

        @self.blueprint.route("/api/auth/register", methods=["POST"])
        def register() -> tuple[Response, int]:
            return self.__user_register(request)

    def __user_register(self, request: Request) -> tuple[Response, int]:
        content_type = request.headers.get("Content-Type")
        if content_type != "application/json":
            return jsonify({"reason": "Bad content type"}), 400

        user_data = request.json
        required_fields = ["login", "email", "password", "countryCode", "isPublic"]
        if not all(field in user_data for field in required_fields):
            return jsonify({"reason": "Missing fields"}), 400

        try:
            user = User(**user_data)
        except:
            return jsonify({"reason": "Bad user data"}), 400

        if not self.user_database.check_password(user.password):
            return jsonify({"reason": "Bad password"}), 400

        result = {
            "profile": user.get_profile(),
        }

        try:
            self.user_database.add_user(user)
        except UniqueViolation:
            return jsonify({"reason": "User already exists"}), 409
        except:
            return jsonify({"reason": "Failed to register user"}), 400

        return jsonify(result), 201
