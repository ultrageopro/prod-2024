class Post:
    def __init__(
        self,
        post_id: str,
        content: str,
        author: str,
        tags: list[str],
        createdAt: str,
        likesCount: int = 0,
        dislikesCount: int = 0,
    ):

        if len(content) > 1000 or len(tags) > 20:
            raise ValueError("Invalid content or tags")

        self.__content = content
        self.__tags = tags
        self.__author = author
        self.__likesCount = likesCount
        self.__dislikesCount = dislikesCount
        self.__id = post_id
        self.__createdAt = createdAt

    @property
    def post(self) -> dict:
        return {
            "id": self.__id,
            "content": self.__content,
            "author": self.__author,
            "tags": self.__tags,
            "createdAt": self.__createdAt,
            "likesCount": self.__likesCount,
            "dislikesCount": self.__dislikesCount,
        }

    @property
    def post_id(self) -> str:
        return self.__id

    @property
    def content(self) -> str:
        return self.__content

    @property
    def author(self) -> str:
        return self.__author

    @property
    def tags(self) -> list[str]:
        return self.__tags

    @property
    def createdAt(self) -> str:
        return self.__createdAt

    @property
    def likesCount(self) -> int:
        return self.__likesCount

    @property
    def dislikesCount(self) -> int:
        return self.__dislikesCount

    @property
    def id(self) -> str:
        return self.__id
