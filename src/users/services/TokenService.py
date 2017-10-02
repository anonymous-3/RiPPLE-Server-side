# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random

from django.db import transaction
from users.models import User, Token


def token_valid(token):
    if token is None:
        return False
    try:
        return Token.objects.get(payload=token) is not None
    except Token.DoesNotExist:
        return False


@transaction.atomic
def generate_token():
    # Get random user to requester
    count = User.objects.count()
    random_index = random.randint(0, count - 1)
    user = User.objects.all()[random_index]

    digits = '1234567890'
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    token = ''.join(random.SystemRandom().choice(letters + digits)
                    for _ in range(32))

    if token_valid(token) is False:
        new_token = Token(payload=token, user=user)
        new_token.save()
    else:
        return generate_token()

    return new_token.payload


def token_to_user(token):
    return Token.objects.get(payload=token).user
