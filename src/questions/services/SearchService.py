from __future__ import unicode_literals
from ..models import Question, QuestionResponse, Topic, Distractor
from django.db.models import Count, Subquery, OuterRef, Func, F


class SearchService(object):
    def __init__(self):
        super(SearchService, self).__init__()
        self._query = Question.objects

    def addSort(self, sortField, sortOrder):
        if sortOrder == "DESC":
            sort_modifier = "-"
        else:
            sort_modifier = ""

        if sortField in ["difficulty", "quality", "created"]:
            self._query = self._query.order_by(sort_modifier + sortField)
        elif sortField is "personalisation":
            pass
            # Go somewhere else...
        elif sortField == "responses":
            self._query = self._query.annotate(responses=Subquery(
                Distractor.objects.filter(question_id=OuterRef("pk"))
                .annotate(c=Count("questionresponse")).values("c").annotate(
                    s=Func(F("c"), function="LOWER")).values("c")))
            self._query = self._query.order_by(sort_modifier + sortField)

    def addFilter(self, filterField):
        if filterField == "unanswered":
            # All questions where the Question is NOT IN the Distractor Responses
            self._query = self._query.exclude(
                id__in=Distractor.objects.filter(
                    id__in=QuestionResponse.objects.filter(
                        user_id=2).values("response_id")).values("question_id"))

        elif filterField == "answered":
            # All questions where the Question IS IN the Distractor Responses
            self._query = self._query.filter(
                id__in=Distractor.objects.filter(
                    id__in=QuestionResponse.objects.filter(
                        user_id=2).values("response_id")).values("question_id"))
        elif filterField == "wrong":
            # All answered Questions where the Response has the isCorrect=True property
            self._query = self._query.filter(
                id__in=Distractor.objects.filter(
                    isCorrect=False,
                    id__in=QuestionResponse.objects.filter(
                        user_id=2).values("response_id")).values("question_id"))

    def textSearch(self, textQuery):
        self._query = self._query.filter(content__contains=textQuery)

    def addTopicFilter(self, topics):
        self._query = self._query.exclude(topics__in=topics)

    def execute(self):
        return self._query
