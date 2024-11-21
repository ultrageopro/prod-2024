from ...database.posts_database import PostPostgreClient
from ...database.user_database import UserPostgreClient
from ...database.friend_database import FriendsPostgreClient
from ...database.reactions_database import ReactionPostgreClient


from flask import Blueprint, Response, request, jsonify, Request
from ...modules.process_token import TokenClient


class PostsRoute:
    def __init__(
        self,
        post_database: PostPostgreClient,
        user_database: UserPostgreClient,
        friend_database: FriendsPostgreClient,
        reaction_database: ReactionPostgreClient,
    ) -> None:
        self.post_database = post_database
        self.user_database = user_database
        self.friend_database = friend_database
        self.reaction_database = reaction_database

        self.blueprint = Blueprint("new", __name__)
        self.token_processing = TokenClient(self.user_database)

        @self.blueprint.route("/api/posts/new", methods=["POST"])
        def new() -> tuple[Response, int]:
            return self.__new_post(request)

        @self.blueprint.route("/api/posts/feed/<login>", methods=["GET"])
        def my_posts(login: str) -> tuple[Response, int]:
            return self.__get_posts(login=login, request=request)

        @self.blueprint.route("/api/posts/<post_id>", methods=["GET"])
        def get_by_id(post_id: str) -> tuple[Response, int]:
            return self.__get_by_id(request, post_id)

        @self.blueprint.route("/api/posts/<post_id>/like", methods=["POST"])
        def like(post_id: str) -> tuple[Response, int]:
            return self.__reaction(request, post_id, "like")

        @self.blueprint.route("/api/posts/<post_id>/dislike", methods=["POST"])
        def dislike(post_id: str) -> tuple[Response, int]:
            return self.__reaction(request, post_id, "dislike")

    def __new_post(self, request: Request) -> tuple[Response, int]:
        token = self.token_processing.get_token(request, body=True)
        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.token_processing.validate_token(token)
        if user is None:
            return jsonify({"reason": "Invalid token"}), 401

        data = request.get_json()
        new_post = self.post_database.add_post(user.login, data)
        if new_post is None:
            return jsonify({"reason": "Bad data"}), 401

        return jsonify(new_post.post), 200

    def __get_by_id(self, request: Request, post_id: str) -> tuple[Response, int]:

        token = self.token_processing.get_token(request)
        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user_from = self.token_processing.validate_token(token)
        if user_from is None:
            return jsonify({"reason": "Invalid token"}), 401

        post = self.post_database.get_post_by_id(post_id)
        if post is None:
            return jsonify({"reason": "Post not found"}), 404

        author_login = post.author

        user_to = self.user_database.get_user_data(author_login)
        if user_to is None:
            return jsonify({"reason": "User not found"}), 404

        if user_to.isPublic:
            return jsonify(post.post), 200
        elif self.friend_database.is_friend_registered(user_to.login, user_from.login):
            return jsonify(post.post), 200
        return jsonify({"reason": "Post not found"}), 404

    def __get_posts(self, request: Request, login: str) -> tuple[Response, int]:

        limit = request.args.get("limit", 5, int)
        offset = request.args.get("offset", 0, int)

        if limit > 50 or limit < 0 or offset < 0:
            return jsonify({"reason": "Invalid limit or offset"}), 401

        token = self.token_processing.get_token(request)
        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.token_processing.validate_token(token)
        if user is None:
            return jsonify({"reason": "Invalid token"}), 401

        match login:
            case "my":
                posts = self.post_database.get_posts_by_user(user.login)
                return jsonify(posts[offset : offset + limit]), 200
            case _:
                requested_user = self.user_database.get_user_data(login)
                if requested_user is None:
                    return jsonify({"reason": "User not found"}), 404

                try:
                    friend_registered = self.friend_database.is_friend_registered(
                        requested_user.login, user.login
                    )
                except:
                    return jsonify({"reason": "User not found"}), 404

                if not requested_user.isPublic and not friend_registered:
                    return jsonify({"reason": "User not found"}), 404
                posts = self.post_database.get_posts_by_user(requested_user.login)
                return jsonify(posts[offset : offset + limit]), 200

    def __reaction(
        self, request: Request, post_id: str, reaction: str
    ) -> tuple[Response, int]:
        token = self.token_processing.get_token(request)
        if token is None:
            return jsonify({"reason": "Invalid token"}), 401

        user = self.token_processing.validate_token(token)
        if user is None:
            return jsonify({"reason": "Invalid token"}), 401

        post = self.post_database.get_post_by_id(post_id)
        if post is None:
            return jsonify({"reason": "Post not found"}), 404

        requested_user = self.user_database.get_user_data(post.author)
        if requested_user is None:
            return jsonify({"reason": "Post not found"}), 404
        try:
            friend_registered = self.friend_database.is_friend_registered(
                requested_user.login, user.login
            )
        except:
            return jsonify({"reason": "Post not found"}), 404

        if not requested_user.isPublic and not friend_registered:
            return jsonify({"reason": "Post not found"}), 404

        self.reaction_database.add_reaction(post_id, user.login, reaction)
        reactions_count = self.reaction_database.get_reaction_counts(post_id)

        likes = reactions_count.get("likesCount")
        dislikes = reactions_count.get("dislikesCount")
        if likes is None:
            return jsonify({"reason": "Post not found"}), 404
        if dislikes is None:
            return jsonify({"reason": "Post not found"}), 404

        self.post_database.update_post(
            post_id, {"likesCount": likes, "dislikesCount": dislikes}
        )

        final_post = self.post_database.get_post_by_id(post_id)
        if final_post is None:
            return jsonify({"reason": "Post not found"}), 404
        return jsonify(final_post.post), 200
