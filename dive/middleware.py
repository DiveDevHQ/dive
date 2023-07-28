from django.http import HttpResponse


def health(get_response):

    def middleware(request):
        if request.path == "/health":
            return HttpResponse("Healthy")
        return get_response(request)

    return middleware