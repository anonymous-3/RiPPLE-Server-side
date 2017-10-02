from django.http import JsonResponse
from users.services.TokenService import token_valid


class TokenValidator(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get("HTTP_AUTHORIZATION", None)
        if token is None and request.path != '/users/login/' and request.path != '/users/login':
            return JsonResponse({
                "error": "Missing token in Authorization header."
            }, status=401)

        if token is not None and token_valid(token) is not True:
            return JsonResponse({
                "error": "Provided token is invalid"
            }, status=401)

        return self.get_response(request)
