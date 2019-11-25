msg = {
    "DB_DOWNLOAD": "Please, wait. Your data is being downloading...",
    "DB_FAIL": (
        "The user wasn't found. All the data will be retrieved "
        "from the Internet and saved to the database."
    ),
    "DB_SEARCH": "Looking for the user in the database...",
    "DEL_ALREADY": "The user '{}' is already deleted.",
    "DEL_SUCCESS": "The user '{}' and his data have been successfully deleted.",
    "DONE": "Done!",
    "ERR_ACCESS": "The account of the user '{}' is private!",
    "ERR_BUT_DB": "You can still get your data from the database.",
    "ERR_LOGIN": "The 'login' argument type must be a string!",
    "ERR_NET": (
        "Internet is not available. "
        "Please, check your connection and try again."
    ),
    "ERR_UPD": "Update method is not available for this object!",
    "ERR_USER": "The user '{}' does not exist!",
    "UPD": "Please, wait. Your data is being updated...",
    "USER_SUCCESS": (
        "Successfully! The user's data is accessed in the 'user' attribute."
    ),
}


def flash(**kwargs):
    """Print various kinds of information."""
    key = kwargs["msg"]
    login = kwargs.get("login")

    print(msg[key].format(login) if login else msg[key])
