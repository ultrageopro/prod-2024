from flask import Blueprint, jsonify, Response, request, Request
from ...database.user_database import UserPostgreClient
from ...database.countries_database import CountryPostgreClient
from ...modules.process_token import TokenClient
import bcrypt


class UpdatePasswordRoute:
    def __init__(self, user_database: UserPostgreClient) -> None:
        """
        Initialize the ProfileRoute with the given user_database.

        Args:
            user_database (Any): The user database object.
        """

        self.user_database = user_database
        self.token_processing = TokenClient(self.user_database)
        self.blueprint = Blueprint("update_password", __name__)

        @self.blueprint.route("/api/me/updatePassword/", methods=["POST"])
        def update_password() -> tuple[Response, int]:
            return self.__update_password(request)

    def __update_password(self, request: Request) -> tuple[Response, int]:
        """
        Update the password of the current user.

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

        if not self.user_database.check_password(data["newPassword"]):
            return jsonify({"reason": "Password not valid"}), 400

        if not bcrypt.checkpw(
            data["oldPassword"].encode("utf-8"), user.password.encode("utf-8")
        ):
            return jsonify({"reason": "Incorrect password"}), 403

        err = self.user_database.change_password(user.login, data["newPassword"])
        if err != 200:
            return jsonify({"reason": "Not allowed fields or not valid data"}), err

        updated_user = self.user_database.get_user_data(user.login)
        if updated_user is None:
            return jsonify({"reason": "User not found"}), 401

        return jsonify({"reason": "Password updated"}), 200
