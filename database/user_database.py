import psycopg2
from typing import Optional
import bcrypt
from ..modules.user import User
import re


class UserPostgreClient:
    """
    A class to interact with a PostgreSQL database for user management.
    """

    def __init__(self, ps_connect: Optional[str]) -> None:
        """
        Initialize the UserPostgreClient with a PostgreSQL connection string.

        Args:
            ps_connect (str): The PostgreSQL connection string.
        Raises:
            ValueError: If ps_connect is None.
        """

        if ps_connect is None:
            raise ValueError("ps_connect cannot be None")
        self.ps_conn = ps_connect
        self.init_database()

    def init_database(self) -> None:
        """
        Initialize the database by creating the users table if it does not exist.
        """

        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            cur.execute("DROP TABLE IF EXISTS users")
            cur.execute(
                """
                ALTER TABLE countries ADD UNIQUE (alpha2);
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    login TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    countryCode TEXT NOT NULL REFERENCES countries(alpha2),
                    isPublic BOOLEAN NOT NULL,
                    phone TEXT UNIQUE,
                    image TEXT,
                    CHECK (login ~ '^[a-zA-Z0-9-]{1,30}$'),
                    CHECK (LENGTH(email) <= 50),
                    CHECK (LENGTH(email) > 0),
                    CHECK (phone ~ '^\+[\d]+$'),
                    CHECK (LENGTH(image) <= 200)
                );
                """
            )

            conn.commit()

    def get_user_data(self, login: str) -> Optional[User]:
        """
        Retrieve user data from the database based on their login.

        Args:
            login (str): The user's login.

        Returns:
            dict: A dictionary containing user data.
        """

        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE login = %s", (login,))
            user_data = cur.fetchone()

        if user_data is None:
            return None

        keys = [
            "login",
            "email",
            "password",
            "countryCode",
            "isPublic",
            "phone",
            "image",
        ]
        result = dict(zip(keys, user_data[1:]))

        return User(**result)

    def add_user(self, user: User) -> None:
        """
        Add a new user to the database.

        Args:
            user (dict): A dictionary containing user information.
        """

        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            hashed_password = bcrypt.hashpw(
                user.password.encode("utf-8"), bcrypt.gensalt()
            )

            cur.execute(
                "INSERT INTO users (login, email, password, countryCode, isPublic, phone, image) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    user.login,
                    user.email,
                    hashed_password.decode("utf-8"),
                    user.countryCode,
                    user.isPublic,
                    user.phone,
                    user.image,
                ),
            )

            conn.commit()

    def update_user_data(self, login: str, new_data: dict) -> int:
        """
        Update user data in the database.

        Args:
            login (str): The user's login.
            new_data (dict): A dictionary containing the new user data.
        """

        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            try:
                for key, value in new_data.items():
                    cur.execute(
                        "UPDATE users SET {} = %s WHERE login = %s".format(key),
                        (value, login),
                    )
            except psycopg2.errors.UniqueViolation:
                return 409
            except:
                return 400

            conn.commit()

        return 200

    def change_password(self, login: str, new_password: str) -> int:
        """
        Change the password of the user.

        Args:
            login (str): The user's login.
            new_password (str): The new password.
        """

        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            hashed_password = bcrypt.hashpw(
                new_password.encode("utf-8"), bcrypt.gensalt()
            )

            try:
                cur.execute(
                    "UPDATE users SET password = %s WHERE login = %s",
                    (hashed_password.decode("utf-8"), login),
                )
                conn.commit()
            except:
                return 400

        return 200

    def check_password(self, password: str) -> bool:
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,100}$"
        return bool(re.search(pattern, password))
