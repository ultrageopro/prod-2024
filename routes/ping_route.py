from flask import Blueprint, jsonify, Response


class PingRoute:
    def __init__(self) -> None:
        """
        Initializes the PingRoute class.
        """

        self.blueprint = Blueprint("ping", __name__)

        @self.blueprint.route("/api/ping", methods=["GET"])
        def ping() -> tuple[Response, int]:
            """
            Handles the GET request to /api/ping endpoint.

            Returns:
                tuple[Response, int]: A tuple containing the JSON response and the status code.
            """

            return jsonify({"status": "ok"}), 200
