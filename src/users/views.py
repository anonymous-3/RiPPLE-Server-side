# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from json import loads

from django.http import JsonResponse, HttpResponse
from users.services.TokenService import generate_token


def index(request):
    return JsonResponse({
        "login": "Returns a token to authenticate against the server"
    })


def login(request):
    token = request.META.get("HTTP_AUTHORIZATION", None)
    if token is not None:
        return JsonResponse({
            "token": token
        })

    return JsonResponse({
        "token": generate_token()
    })
