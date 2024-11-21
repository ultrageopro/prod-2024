from flask import Blueprint, jsonify, Response, request, Request
from ...modules.user import User
from ...database.user_database import UserPostgreClient
from ...database.friend_database import FriendsPostgreClient
from ...modules.process_token import TokenClient


class ListFriendRoute:
    def __init__(
        self, user_database: UserPostgreClient, friend_database: FriendsPostgreClient
    ) -> None:

        self.user_database = user_database
        self.friend_database = friend_database
        self.token_processing = TokenClient(self.user_database)
        self.blueprint = Blueprint("list_friend", __name__)

        @self.blueprint.route("/api/friends/", methods=["POST"])
        def list_friend() -> tuple[Response, int]:
            return self.__list_friend(request)

    def __list_friend(self, request: Request) -> tuple[Response, int]:
        token = self.token_processing.get_token(request)
        limit = request.args.get("limit", 5, int)
        offset = request.args.get("offset", 0, int)

        if limit > 50 or limit < 0 or offset < 0:
            return jsonify({"reason": "Invalid limit or offset"}), 401

        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.token_processing.validate_token(token)
        if user is None:
            return jsonify({"reason": "Invalid token"}), 401

        friends = self.friend_database.get_user_friends(user.login)[
            offset : offset + limit
        ]
        return jsonify(friends), 200
