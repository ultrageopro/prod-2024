import psycopg2
from typing import Any, Optional, Dict
from ..modules.post import Post
import uuid
import datetime


class PostPostgreClient:
    def __init__(self, ps_conn: str) -> None:
        self.ps_conn = ps_conn
        self.init_database()

    def init_database(self) -> None:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            cur.execute("DROP TABLE IF EXISTS posts")
            cur.execute(
                """
                CREATE TABLE posts (
                    id TEXT PRIMARY KEY NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT NOT NULL,
                    tags TEXT[] NOT NULL,
                    createdAt TIMESTAMP WITH TIME ZONE NOT NULL,
                    likesCount INTEGER DEFAULT 0,
                    dislikesCount INTEGER DEFAULT 0 
                );
                """
            )

            conn.commit()

    def add_post(self, login: str, post_data: Dict[str, Any]) -> Optional[Post]:

        post_data["post_id"] = str(uuid.uuid4())

        post_data["createdAt"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        post_data["author"] = login

        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            try:
                post = Post(**post_data)
                cur.execute(
                    """
                    INSERT INTO posts (id, content, author, tags, createdAt)
                    VALUES (%s, %s, %s, %s, NOW());
                    """,
                    (
                        post.id,
                        post.content,
                        login,
                        post.tags,
                    ),
                )

                conn.commit()
            except:
                return None

        return post

    def get_post_by_id(self, post_id: str) -> Optional[Post]:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            cur.execute(
                """
                SELECT * FROM posts WHERE id = %s;
                """,
                (post_id,),
            )

            post = cur.fetchone()

            if post:
                return Post(*post)
            else:
                return None

    def update_post(self, post_id: str, update_data: Dict[str, Any]) -> None:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            cur.execute(
                """
                UPDATE posts
                SET likesCount = %s, dislikesCount = %s
                WHERE id = %s;
                """,
                (
                    update_data.get("likesCount", 0),
                    update_data.get("dislikesCount", 0),
                    post_id,
                ),
            )

            conn.commit()

    def delete_post(self, post_id: str) -> None:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            cur.execute(
                """
                DELETE FROM posts WHERE id = %s;
                """,
                (post_id,),
            )

            conn.commit()

    def get_posts_by_user(self, login: str) -> list:
        with psycopg2.connect(self.ps_conn) as conn:
            cur = conn.cursor()

            cur.execute(
                """
                SELECT * FROM posts WHERE author = %s ORDER BY createdAt DESC;
                """,
                (login,),
            )

            posts = cur.fetchall()

        result = []
        for post in posts:
            result.append(Post(*post).post)
        return result
