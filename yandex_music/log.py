MSG = {
    "DB_DOWNLOAD": "Please, wait. Your data is being downloading...",
    "DB_FAIL": (
        "The user wasn't found. All the data will be retrieved "
        "from the Internet and saved to the database."
    ),
    "DB_SEARCH": "Looking for the user in the database...",
    "DEL_ALREADY": "The user '{}' is already deleted.",
    "DEL_SUCCESS": "The user '{}' and his data have been successfully deleted.",
    "DONE": "Done!",
    "UPD": "Please, wait. Your data is being updated...",
    "USER_SUCCESS": (
        "Successfully! The user's data is accessed in the 'user' attribute."
    ),
}


def flash(**kwargs):
    """Print various kinds of information."""
    key = kwargs["msg"]
    login = kwargs.get("login")

    print(MSG[key].format(login) if login else MSG[key])
