msg = {}
msg["ERR_NET"] = (
    "Internet is not available. Please, check your connection and try again."
)
msg["ERR_NET_BUT_CACHE"] = (
    f"{msg['ERR_NET']} You can still get your data from the local cache."
)
msg["ERR_UPD"] = "Update method is not available for this object."
msg["ERR_USER"] = "The user '{}' does not exist!"
msg["ERR_ACCESS"] = "The account of the user '{}' is private!"

msg["UPD"] = "Please, wait. Your data is being updated..."

msg["CACHE_LOOK"] = "Looking for the local cache..."
msg["CACHE_SUCCESS"] = (
    "Successfully! Your playlist's data has been read from the cache."
)
msg["CACHE_FAIL"] = (
    "The cache wasn't found. Your playlist's data will be retrieved "
    "from the Internet and cached to the disc."
)

msg["DONE"] = "Done!"


def flash(**kwargs):
    key = kwargs["msg"]
    login = kwargs.get("login")

    print(msg[key].format(login) if login else msg[key])
