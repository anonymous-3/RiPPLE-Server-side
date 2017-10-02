# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
from questions.models import Topic, Competency, CompetencyMap
from users.models import User
from users.services.TokenService import token_to_user


def logged_in_user(request):
    token = request.META.get("HTTP_AUTHORIZATION")
    if token is not None:
        return token_to_user(token)

    raise Exception("User not associated with token")


def user_competencies(user):
    def sort_competencies(carry, competency):
        if carry.get(competency.for_competency_id, None) is None:
            carry[competency.for_competency_id] = []

        carry[competency.for_competency_id].append(competency)
        return carry

    competency_map = CompetencyMap.objects.filter(user=user)
    # Reduce competency map to joined competencies
    user_competency_values = Competency.objects.filter(
        id__in=competency_map.values("for_competency")).distinct()

    # Reduce competency_map into an identifier mapping to topics
    sorted_competencies = reduce(sort_competencies, competency_map, {})

    edges = []
    for competency_id, nodes in sorted_competencies.iteritems():
        competency = user_competency_values.get(pk=competency_id)
        source = nodes[0]
        target = nodes[1] if len(nodes) > 1 else source
        edges.append([
            source.topic.toJSON(),
            target.topic.toJSON(),
            competency.competency,
            competency.confidence
        ])

    return edges
