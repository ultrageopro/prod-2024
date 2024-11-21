from flask import Blueprint, jsonify, Response, request, Request
from ...modules.user import User
from ...database.user_database import UserPostgreClient
from ...database.friend_database import FriendsPostgreClient
from ...modules.process_token import TokenClient


class AddFriendRoute:
    def __init__(
        self, user_database: UserPostgreClient, friend_database: FriendsPostgreClient
    ) -> None:

        self.user_database = user_database
        self.friend_database = friend_database
        self.token_processing = TokenClient(self.user_database)
        self.blueprint = Blueprint("add_friend", __name__)

        @self.blueprint.route("/api/friends/add/", methods=["POST"])
        def add_friend() -> tuple[Response, int]:
            return self.__add_friend(request)

    def __add_friend(self, request: Request) -> tuple[Response, int]:

        token = self.token_processing.get_token(request, body=True)
        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.token_processing.validate_token(token)
        if user is None:
            return jsonify({"reason": "Invalid token"}), 401

        data = request.get_json()
        friendLogin = data.get("login")

        if friendLogin is None:
            return jsonify({"reason": "Login is required"}), 400

        friend = self.user_database.get_user_data(friendLogin)
        if friend is None:
            return jsonify({"reason": "User not found"}), 404

        if friend.login == user.login:
            return jsonify({"reason": "Nothing to add"}), 200

        if self.friend_database.add_friend(user.login, friendLogin):
            return jsonify({"status": "ok"}), 200

        return jsonify({"reason": "Failed to add friend"}), 404
