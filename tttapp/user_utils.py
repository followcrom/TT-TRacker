
# -----------------------------------------

from django.contrib import messages
from django.shortcuts import render


def rate_limit_exceeded(request, exception):
    messages.error(
        request,
        "You have exceeded the rate limit for this action.\nPlease try again later.",
    )
    return render(request, "403.html", status=403)


# -----------------------------------------

# Custom rate function
def rate(group, request):
    if request.user.is_authenticated:
        rate = "1000/m"
    else:
        rate = "2/m"
    print("Rate:", rate)
    return rate


# -----------------------------------------
