from typing import Optional


class User:
    def __init__(
        self,
        login: str,
        email: str,
        password: str,
        countryCode: str,
        isPublic: bool,
        phone: Optional[str] = None,
        image: Optional[str] = None,
    ):

        self.login = login
        self.email = email
        self.password = password
        self.countryCode = countryCode
        self.isPublic = isPublic
        self.phone = phone
        self.image = image

    def get_profile(self) -> dict:
        user: dict = {
            "login": self.login,
            "email": self.email,
            "countryCode": self.countryCode,
            "isPublic": self.isPublic,
        }

        if self.phone is not None:
            user["phone"] = self.phone

        if self.image is not None:
            user["image"] = self.image

        return user
