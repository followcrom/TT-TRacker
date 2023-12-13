# -----------------------------------------


def user_or_ip(group, request):
    if request.user.is_authenticated:
        # Return a unique key for authenticated users
        print("Username:", request.user.username)
        return "user:{}".format(request.user.username)
    else:
        # Return the user's IP address for unauthenticated users
        return "ip:{}".format(get_client_ip(request))


# -----------------------------------------


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    print("IP:", ip)
    return ip


# -----------------------------------------


def rate(group, request):
    if request.user.is_authenticated:
        rate = "1000/m"
    else:
        rate = "2/m"
    print("Rate:", rate)
    return rate


# -----------------------------------------
