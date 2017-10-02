# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from json import loads

from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ripple.util.util import isNumber
from users.services import UserService
from questions.services import QuestionService, SearchService


def respond(request):
    if request.method != 'POST':
        return JsonResponse({
            "error": "Must use POST to this endpoint"
        }, status=405)

    post_request = loads(request.body)
    distractor_id = post_request.get("distractorID", None)

    if distractor_id is None:
        return JsonResponse({"error": "Missing integer distractorID in request"}, status=422)
    if QuestionService.respond_to_question(distractor_id, UserService.logged_in_user(request)) is None:
        return JsonResponse({"error": "Invalid distractorID"}, status=422)
    else:
        return HttpResponse(status=204)


def rate(request):
    if request.method != 'POST':
        return JsonResponse({
            "error": "Must use POST to this endpoint"
        }, status=405)

    post_request = loads(request.body)
    distractor_id = post_request.get("distractorID", None)

    difficulty = post_request.get("difficulty", None)
    quality = post_request.get("quality", None)

    if difficulty is None and quality is None:
        return JsonResponse({"error": "At least response.rating or response.quality must be specified"}, status=422)

    if difficulty is not None:
        if isNumber(difficulty) is False or not 0 <= int(difficulty) <= 5:
            return JsonResponse({"error": "response.difficulty must be between 0 and 5 inclusive"}, status=422)
        difficulty = int(difficulty)

    if quality is not None:
        if isNumber(quality) is False or not 0 <= int(quality) <= 5:
            return JsonResponse({"error": "response.quality must be between 0 and 5 inclusive"}, status=422)
        quality = int(quality)

    if distractor_id is None:
        return JsonResponse({"error": "Missing integer distractorID in request"}, status=422)

    user_ratings = {"difficulty": difficulty, "quality": quality}
    if QuestionService.rate_question(distractor_id, user_ratings, UserService.logged_in_user(request)) is None:
        return JsonResponse({"error": "Invalid distractorID"}, status=422)
    else:
        return HttpResponse(status=204)


def index(request):
    return JsonResponse({
        "all": "Returns all Questions",
        "topics": "Returns all Question Topics",
        "id/:id": "Fetch question by ID",
        "search/sortField/:sortField/sortOrder/:sortOrder/filterField/:filterField/query/:query": "Run a server search",
        "page/:id": "Fetch question collection in chunks",
        "competencies/all": "Fetch all competencies for the user"
    })


def id(request, id):
    question = QuestionService.getQuestion(id)

    if question is None:
        return JsonResponse({}, status=404)

    return JsonResponse(question.toJSON())


def competencies(request):
    logged_in_user = UserService.logged_in_user(request)
    user_competencies = UserService.user_competencies(logged_in_user)
    return JsonResponse(user_competencies, safe=False)


def all(request):
    all_questions = [x.toJSON() for x in QuestionService.allQuestions()]
    return JsonResponse(all_questions, safe=False)


def topics(request):
    unique_topics = [x.toJSON() for x in QuestionService.allTopics()]
    return JsonResponse(unique_topics, safe=False)


def search(request):
    if request.method != 'POST':
        return JsonResponse({
            "error": "Must use POST to this endpoint"
        }, status=405)

    search = SearchService.SearchService()
    post_request = loads(request.body)
    sort_field = post_request.get("sortField", None)
    filter_field = post_request.get("filterField", None)
    filter_topics = post_request.get("filterTopics", None)
    query = post_request.get("query", None)
    sort_order = post_request.get("sortOrder", None)
    page = post_request.get("page", None)

    if sort_field is None and filter_field is None and query is None:
        found_questions = QuestionService.allQuestions()
        return page_response(found_questions, page)

    if sort_field is not None:
        search.addSort(sort_field, sort_order)

    if filter_field is not None:
        search.addFilter(filter_field)

    if filter_topics is not None:
        search.addTopicFilter(filter_topics)

    if query is not None:
        search.textSearch(query)

    try:
        search_result = search.execute()
        return page_response(search_result, page)
    except TypeError:
        all_questions = QuestionService.allQuestions()
        return page_response(all_questions, page)


def page(request, page):
    return page_response(QuestionService.allQuestions(), page)


def page_response(data, page_index):
    page_manager = Paginator(data, 25)
    try:
        page = page_manager.page(page_index)
    except PageNotAnInteger:
        page_index = 1
        page = page_manager.page(page_index)
    except EmptyPage:
        page_index = page_manager.num_pages
        page = page_manager.page(page_index)

    return JsonResponse({
        "items": [x.toJSON() for x in page.object_list],
        "page": page_index,
        "totalItems": page_manager.count
    })
