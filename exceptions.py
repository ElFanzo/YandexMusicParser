class BaseError(Exception):
    """Base class for exceptions in this module."""
    pass


class LoginError(BaseError):
    """Raised if the 'login' argument type is wrong."""
    def __init__(self):
        super().__init__("The 'login' argument type must be a string!")


class NetworkError(BaseError):
    """Raised when a network connection error occurs."""
    def __init__(self):
        super().__init__("Bad connection! Please, try again.")


class UserError(BaseError):
    """Base exception for a user's profile errors."""
    pass


class UserDoesNotExistError(UserError):
    """Raised if a user does not exist."""
    def __init__(self, login):
        super().__init__(f"The user '{login}' does not exist.")


class AccessError(UserError):
    """Raised if a user's profile is private."""
    def __init__(self, login):
        super().__init__(f"The user '{login}' profile is private!")


class NoTracksError(UserError):
    """Raised if a user has no tracks."""
    def __init__(self, login):
        super().__init__(f"The user '{login}' has no tracks yet!")


class ArtistError(BaseError):
    """Base exception for an artist's profile errors."""
    pass


class ProfileError(ArtistError):
    """Raised if an artist has no profile."""
    def __init__(self, name):
        super().__init__(f"The artist '{name}' has no profile on the site.")


class LikesError(ArtistError):
    """Raised if an artist has no likes."""
    def __init__(self, name):
        super().__init__(f"The artist '{name}' has no likes.")
