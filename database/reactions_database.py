import psycopg2
from psycopg2.extras import DictCursor
from typing import Dict


class ReactionPostgreClient:
    def __init__(self, ps_conn: str) -> None:
        self.ps_conn = ps_conn
        self.init_database()

    def init_database(self) -> None:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            cur.execute("DROP TABLE IF EXISTS post_reactions")
            cur.execute(
                """
                CREATE TABLE post_reactions (
                    post_id TEXT NOT NULL,
                    user_login TEXT NOT NULL,
                    reaction TEXT NOT NULL,
                    PRIMARY KEY (post_id, user_login)
                );
                """
            )

            conn.commit()

    def add_reaction(self, post_id: str, user_login: str, reaction: str) -> None:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()
            # Проверяем, существует ли уже реакция пользователя на этот пост
            cur.execute(
                """
                SELECT * FROM post_reactions 
                WHERE post_id = %s AND user_login = %s;
                """,
                (post_id, user_login),
            )
            existing_reaction = cur.fetchone()
            if existing_reaction:
                # Если реакция уже существует, обновляем ее значение
                cur.execute(
                    """
                    UPDATE post_reactions 
                    SET reaction = %s 
                    WHERE post_id = %s AND user_login = %s;
                    """,
                    (reaction, post_id, user_login),
                )
            else:
                # Иначе добавляем новую реакцию
                cur.execute(
                    """
                    INSERT INTO post_reactions (post_id, user_login, reaction) 
                    VALUES (%s, %s, %s);
                    """,
                    (post_id, user_login, reaction),
                )

                cur.execute(
                    """
                    SELECT * FROM post_reactions 
                    """,
                )
                existing_reaction = cur.fetchall()

            conn.commit()

    def get_reaction_counts(self, post_id: str) -> Dict[str, int]:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor(cursor_factory=DictCursor)
            # Сначала получаем суммарное количество лайков
            cur.execute(
                """
                SELECT COALESCE(SUM(CASE WHEN reaction = 'like' THEN 1 ELSE 0 END), 0) as likes_count
                FROM post_reactions 
                WHERE post_id = %s;
                """,
                (post_id,),
            )
            likesCount = cur.fetchone()["likes_count"]

            # Затем получаем суммарное количество дизлайков
            cur.execute(
                """
                SELECT COALESCE(SUM(CASE WHEN reaction = 'dislike' THEN 1 ELSE 0 END), 0) as dislikes_count
                FROM post_reactions 
                WHERE post_id = %s;
                """,
                (post_id,),
            )
            dislikesCount = cur.fetchone()["dislikes_count"]

            return {"likesCount": likesCount, "dislikesCount": dislikesCount}
