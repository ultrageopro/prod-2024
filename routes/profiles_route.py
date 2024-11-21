from flask import Blueprint, jsonify, Response, request, Request
from ..modules.user import User
from ..database.user_database import UserPostgreClient
from ..database.countries_database import CountryPostgreClient
from ..modules.process_token import TokenClient


class ProfilesRoute:
    def __init__(self, user_database: UserPostgreClient):

        self.user_database = user_database
        self.token_processing = TokenClient(self.user_database)
        self.blueprint = Blueprint("profiles", __name__)

        @self.blueprint.route("/api/profiles/<login>", methods=["GET"])
        def get_profile_by_login(login: str) -> tuple[Response, int]:
            """
            Retrieve the profile of the user with the given login.

            Args:
                login (str): The login of the user.

            Returns:
                tuple[Response, int]: The profile data and HTTP status code.
            """
            return self.__get_profile_by_login(request, login)

    def __get_profile_by_login(
        self, request: Request, login: str
    ) -> tuple[Response, int]:
        """
        Retrieve the profile of the user with the given login.

        Args:
            login (str): The login of the user.

        Returns:
            tuple[Response, int]: The profile data and HTTP status code.
        """
        token = self.token_processing.get_token(request)
        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.token_processing.validate_token(token)
        if user is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.user_database.get_user_data(login)
        if user is None:
            return jsonify({"reason": "User not found"}), 403
        if not user.isPublic:
            return jsonify({"reason": "User not found"}), 403
        return jsonify(user.get_profile()), 200
