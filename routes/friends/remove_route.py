from flask import Blueprint, jsonify, Response, request, Request
from ...modules.user import User
from ...database.user_database import UserPostgreClient
from ...database.friend_database import FriendsPostgreClient
from ...modules.process_token import TokenClient


class RemoveFriendRoute:
    def __init__(
        self, user_database: UserPostgreClient, friend_database: FriendsPostgreClient
    ) -> None:

        self.user_database = user_database
        self.friend_database = friend_database
        self.token_processing = TokenClient(self.user_database)
        self.blueprint = Blueprint("remove_friend", __name__)

        @self.blueprint.route("/api/friends/remove/", methods=["POST"])
        def remove_friend() -> tuple[Response, int]:
            return self.__remove_friend(request)

    def __remove_friend(self, request: Request) -> tuple[Response, int]:
        token = self.token_processing.get_token(request, body=True)
        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.token_processing.validate_token(token)
        if user is None:
            return jsonify({"reason": "Invalid token"}), 401

        data = request.get_json()
        friendLogin = data.get("login")

        if friendLogin is None:
            return jsonify({"reason": "Login is required"}), 401

        friend = self.user_database.get_user_data(friendLogin)
        if friend is None:
            return jsonify({"reason": "User not found"}), 401

        if self.friend_database.remove_friend(user.login, friendLogin):
            return jsonify({"status": "ok"}), 200

        return jsonify({"reason": "Failed to remove friend"}), 401
