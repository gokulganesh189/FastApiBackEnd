# exceptions.py
class UserInfoException(Exception):
    ...


class UserInfoNotFoundError(UserInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "User Info Not Found"

    def show_message_not_found(self):
        return {"detail": self.detail, "status_code": self.status_code}


class UserInfoInfoAlreadyExistError(UserInfoException):
    def __init__(self):
        self.status_code = 409
        self.detail = "user Info Already Exist"

    def show_message_exists(self):
        return {"detail": self.detail, "status_code": self.status_code}


class EmailPasswordError(UserInfoException):
    def __init__(self):
        self.status_code = 404
        self.detail = "User Info Not Found recheck username/password "

    def check_username_password(self):
        return {"detail": self.detail, "status_code": self.status_code}
