from enum import StrEnum


class ExceptionCode(StrEnum):
    POST_NOT_FOUND = "POST_NOT_FOUND"
    COMMENT_NOT_FOUND = "COMMENT_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"


class DomainException(Exception):
    def __init__(self, *, message: str, code: ExceptionCode) -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __repr__(self) -> str:
        return self.message + self.code


class PostNotFoundException(DomainException):
    def __init__(self, post_id: str) -> None:
        self.message = f"Post with id {post_id} not found"
        super().__init__(message=self.message, code=ExceptionCode.POST_NOT_FOUND)


class CommentNotFoundException(DomainException):
    def __init__(self, comment_id: str) -> None:
        self.message = f"Comment with id {comment_id} not found"
        super().__init__(message=self.message, code=ExceptionCode.COMMENT_NOT_FOUND)


class UserNotFoundException(DomainException):
    def __init__(self, user_id: int) -> None:
        self.message = f"User with id {user_id} not found"
        super().__init__(message=self.message, code=ExceptionCode.USER_NOT_FOUND)
