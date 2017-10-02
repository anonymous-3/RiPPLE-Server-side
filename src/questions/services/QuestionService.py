from ..models import Question, Topic, Distractor, QuestionRating, QuestionResponse, Competency, CompetencyMap, QuestionScore
from django.core.exceptions import ObjectDoesNotExist
from ripple.util import util


def allQuestions():
    return Question.objects.all()


def allTopics():
    return Topic.objects.distinct()


def getQuestion(id):
    try:
        return Question.objects.get(pk=id)
    except ObjectDoesNotExist:
        return None


def respond_to_question(distractor_id, user):
    try:
        answered_option = Distractor.objects.get(pk=distractor_id)
    except Distractor.DoesNotExist:
        return None

    response = QuestionResponse(
        user=user,
        response=answered_option
    )
    response.save()

    update_competency(user, answered_option.question, response)
    return True


def rate_question(distractor_id, response, user):
    difficulty = response.get("difficulty", None)
    quality = response.get("quality", None)
    try:
        answered_option = Distractor.objects.get(pk=distractor_id)
        found = QuestionRating.objects.filter(
            user_id=user.id, response_id=distractor_id
        ).first()

        if found is None:
            QuestionRating(
                quality=quality,
                difficulty=difficulty,
                response=answered_option,
                user=user
            ).save()
            return True
        else:
            # Update existing response
            found.quality = quality
            found.difficulty = difficulty
            found.save()
            return True
    except ObjectDoesNotExist:
        return None


def calculate_question_score(attempts, is_correct):
    score_map = {
        1: 1 if is_correct else -1,
        2: 0.25 if is_correct else -1,
        3: -0.25 if is_correct else -1,
        4: -0.75 if is_correct else -1
    }
    return score_map[attempts]


def update_question_score(user, question, new_score):
    """
        Helper method to update the cached QuestionScore for a users question to new_score
        Creates a QuestionScore is none exists
    """
    try:
        cached_question_score = QuestionScore.objects.get(
            user=user, question=question)
        cached_question_score.score = new_score
        cached_question_score.save()
    except QuestionScore.DoesNotExist:
        QuestionScore(user=user, question=question,
                      score=new_score).save()


def update_competency(user, question, response):
    """
        Updates the users competency for all topic combinations in the given question
    """
    # Weigh each topic
    weights = util.topic_weights(question.topics.all())

    for i in weights:
        topics = i["topics"]
        weight = i["weight"]

        mapped_competencies = CompetencyMap.objects.filter(
            user=user, topic__in=topics)

        previous_score = 0
        attempt_count = 1
        if len(topics) == mapped_competencies.count():
            attempt_count = QuestionResponse.objects.filter(
                user=user, response__in=Distractor.objects.filter(question=question)).count()

            user_competency = Competency.objects.get(
                pk=mapped_competencies.first().for_competency_id)

            if attempt_count > 1:
                # Has not attempted question before
                previous_score = QuestionScore.objects.get(
                    user=user, question=question).score

        else:
            user_competency = Competency.objects.create(
                competency=50, confidence=1)

            for topic in topics:
                CompetencyMap(
                    user=user,
                    topic=topic,
                    for_competency=user_competency
                ).save()

        question_score = calculate_question_score(
            attempt_count, response.response.isCorrect)

        user_competency.competency = (
            user_competency.competency * user_competency.confidence - previous_score + question_score) / (user_competency.confidence + weight)

        user_competency.confidence += weight
        user_competency.save()

        update_question_score(user, question, question_score)
        return user_competency
