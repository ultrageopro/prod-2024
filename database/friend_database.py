import psycopg2
from typing import Any, List, Dict


class FriendsPostgreClient:
    def __init__(self, ps_conn: str) -> None:
        self.ps_conn = ps_conn
        self.init_database()

    def init_database(self) -> None:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            cur.execute("DROP TABLE IF EXISTS friends")
            cur.execute(
                """
                CREATE TABLE friends (
                    id SERIAL PRIMARY KEY,
                    login TEXT NOT NULL,
                    friendLogin TEXT NOT NULL,
                    date TIMESTAMP WITH TIME ZONE NOT NULL
                );
                """
            )

            conn.commit()

    def get_user_friends(self, login: str) -> List[Dict[str, Any]]:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT friendLogin, date FROM friends WHERE login = %s ORDER BY date DESC",
                (login,),
            )
            rows = cur.fetchall()
            friends = [
                {
                    "login": row[0],
                    "addedAt": row[1].strftime("%Y-%m-%dT%H:%M:%S")
                    + "Z"
                    + row[1].strftime("%z")[1:3]
                    + ":"
                    + row[1].strftime("%z")[3:],
                }
                for row in rows
            ]
            return friends

    def add_friend(self, login: str, friendLogin: str) -> bool:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            if self.is_friend_registered(login, friendLogin):
                return True

            try:
                cur.execute(
                    "INSERT INTO friends (login, friendLogin, date) VALUES (%s, %s, NOW())",
                    (login, friendLogin),
                )
            except:
                return False

            conn.commit()
        return True

    def remove_friend(self, login: str, friendLogin: str) -> bool:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            try:
                cur.execute(
                    "DELETE FROM friends WHERE login = %s AND friendLogin = %s",
                    (login, friendLogin),
                )
            except:
                return False

            conn.commit()
        return True

    def is_friend_registered(self, login: str, friend_login: str) -> bool:
        friends = self.get_user_friends(login)
        registered_logins = [friend["login"] for friend in friends]
        return friend_login in registered_logins
