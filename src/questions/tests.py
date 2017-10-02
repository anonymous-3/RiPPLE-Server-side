# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
import random
import math
from .models import Topic, Question, Distractor, QuestionResponse, QuestionScore, Competency
from users.models import User
from .services import QuestionService

# Create your tests here.


class QuestionTestCase(TestCase):
    def _bootstrap_topics(self):
        [Topic(id=i, name=x).save()
         for i, x in enumerate(["t1", "t2", "t3", "t4", "t5", "t6"])]

    def _bootstrap_questions(self):
        topic_map = [
            Topic.objects.filter(id__in=[1]),
            Topic.objects.filter(id__in=[1, 2]),
            Topic.objects.filter(id__in=[2, 3, 4]),
            Topic.objects.filter(id__in=[4]),
            Topic.objects.filter(id__in=[2, 4])
        ]

        for i in range(0, 5):
            q = Question(
                id=i + 1,
                content="",
                explanation="",
                difficulty=1,
                quality=1,
                difficultyCount=1,
                qualityCount=1
            )
            q.save()
            q.topics.set(topic_map[i])

    def _bootstrap_question_choices(self):
        question_count = Question.objects.all().count()
        for i in range(0, (4 * question_count)):
            id = i + 1
            Distractor(
                id=id,
                content="question " + str(i),
                response=chr(ord('A') + id % 4),
                isCorrect=id == 2,
                question_id=math.ceil(id / 4.0)
            ).save()

    def _bootstrap_user(self, id):
        user = User(id=id, first_name="u_firstname", last_name="u_lastname")
        user.save()
        return user

    def test_answering_new_question_single_topic(self):
        """ New question with single topic """
        self._bootstrap_topics()
        self._bootstrap_questions()
        self._bootstrap_question_choices()
        user = self._bootstrap_user(1)

        QuestionService.respond_to_question(1, user)

        self.assertEqual(QuestionResponse.objects.all().count(), 1)
        user_response = QuestionResponse.objects.first()
        self.assertEqual(user_response.user_id, 1)
        self.assertEqual(user_response.response_id, 1)

        self.assertEqual(QuestionScore.objects.all().count(), 1)
        question_score = QuestionScore.objects.all().first()
        self.assertEqual(question_score.user_id, 1)
        self.assertEqual(question_score.question_id, 1)
        self.assertEqual(question_score.score, -1)

        self.assertEqual(Competency.objects.all().count(), 1)
        competency = Competency.objects.first()

        # TODO: Work out comp
        self.assertEqual(competency.competency, 50)
        self.assertEqual(competency.confidence, 2)

    def test_answering_new_question_multiple_topics(self):
        """ New question with multiple topics """
        pass

    def test_answering_existing_question(self):
        # Existing item in QuestionScore with single topic
        # Existing item in QuestionScore with multiple topics
        [Topic(name=x).save() for x in ["t3", "t4", "t5"]]

        self.assertEqual(Topic.objects.all().count(), 3)

    def test_answering_multiple_questions(self):
        # New question with existing items with single topic
        # New question with existing items with multiple topics
        self.assertEqual(True, True)
