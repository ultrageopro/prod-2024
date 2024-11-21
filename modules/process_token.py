import jwt
from ..database.user_database import UserPostgreClient
from ..modules.user import User
from typing import Optional
from flask import Request


class TokenClient:
    def __init__(self, user_database: UserPostgreClient) -> None:
        """
        Initialize the TokenClient with the given user_database.

        Args:
            user_database (Any): The user database object.
        """

        self.user_database = user_database

    def get_token(self, request: Request, body: bool = False) -> Optional[str]:
        content_type = request.headers.get("Content-Type")
        if content_type != "application/json" and body:
            # Check if content type is JSON
            return None

        token = request.headers.get("Authorization")
        if token is None:
            return None
        token = token.split(" ")[1]
        return token

    def validate_token(self, token: str) -> Optional[User]:
        """
        Validate the token.

        Args:
            token (str): The token to validate.

        Returns:
            Optional[User]: The user object if the token is valid, otherwise None.
        """

        try:
            decoded_token = jwt.decode(token, "secret", algorithms=["HS256"])
            login = decoded_token.get("login")
            password = decoded_token.get("password")
        except jwt.exceptions.InvalidSignatureError:
            return None
        except jwt.exceptions.ExpiredSignatureError:
            return None
        except:
            return None

        if login is None or password is None:
            return None

        user = self.user_database.get_user_data(login)

        if user is None:
            return None

        if password != user.password:
            return None

        return user
