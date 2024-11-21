from flask import Blueprint, jsonify, Response, request, Request
from ...database.user_database import UserPostgreClient
from ...database.countries_database import CountryPostgreClient
from ...modules.process_token import TokenClient


class ProfileRoute:
    def __init__(
        self, user_database: UserPostgreClient, country_database: CountryPostgreClient
    ) -> None:
        """
        Initialize the ProfileRoute with the given user_database.

        Args:
            user_database (Any): The user database object.
        """

        self.user_database = user_database
        self.country_database = country_database
        self.token_processing = TokenClient(self.user_database)
        self.blueprint = Blueprint("profile", __name__)

        @self.blueprint.route("/api/me/profile/", methods=["GET"])
        def get_profile() -> tuple[Response, int]:
            """
            Retrieve the profile of the current user.

            Returns:
                tuple[Response, int]: The profile data and HTTP status code.
            """
            return self.__get_profile(request)

        @self.blueprint.route("/api/me/profile/", methods=["PATCH"])
        def patch_profile() -> tuple[Response, int]:
            """
            Update the profile of the current user.

            Returns:
                tuple[Response, int]: The updated profile data and HTTP status code.
            """
            return self.__patch_profile(request)

    def __get_profile(self, request: Request) -> tuple[Response, int]:
        """
        Retrieve the profile of the current user.

        Returns:
            tuple[Response, int]: The profile data and HTTP status code.
        """
        token = self.token_processing.get_token(request)
        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.token_processing.validate_token(token)
        if user is None:
            return jsonify({"reason": "Invalid token"}), 401

        return jsonify(user.get_profile()), 200

    def __patch_profile(self, request: Request) -> tuple[Response, int]:
        """
        Update the profile of the current user.

        Returns:
            tuple[Response, int]: The updated profile data and HTTP status code.
        """

        token = self.token_processing.get_token(request, body=True)
        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.token_processing.validate_token(token)
        if user is None:
            return jsonify({"reason": "Invalid token"}), 401

        data = request.get_json()

        not_allowed_fields = ["login", "password", "email"]
        if set(data.keys()) & set(not_allowed_fields):
            return jsonify({"reason": "Bad data"}), 401

        err = self.user_database.update_user_data(user.login, data)
        if err != 200:
            return jsonify({"reason": "Not allowed fields or not valid data"}), err

        updated_user = self.user_database.get_user_data(user.login)
        if updated_user is None:
            return jsonify({"reason": "User not found"}), 401

        return jsonify(updated_user.get_profile()), 200
