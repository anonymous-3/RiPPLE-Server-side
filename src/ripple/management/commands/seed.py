from django.core.management.base import BaseCommand
from questions.models import Topic, Question, Distractor, QuestionResponse, QuestionRating, Competency, CompetencyMap
from users.models import User

from questions.services import QuestionService

from random import randint, randrange, sample, choice
from faker import Factory
fake = Factory.create()


class Command(BaseCommand):
    args = ''
    help = 'Populates the Questions database'

    def handle(self, *args, **options):
        users = [User(first_name=fake.first_name(), last_name=fake.last_name())
                 for user in range(50)]
        [x.save() for x in users]

        unique_topics = ["Arrays", "Loops", "Recursion",
                         "Algorithms", "Data Structures", "Variables"]

        all_topics = [Topic.objects.create(name=x) for x in unique_topics]

        distractors = []
        for i in range(0, 100):
            imageURL = "<img src='" + fake.image_url() + "' />" if randrange(0, 3) is 0 else ""
            answerURL = "<img src='" + fake.image_url() + "' />" if randrange(0, 3) is 0 else ""

            question = Question(
                content=imageURL + fake.text(),
                explanation=answerURL + fake.text(),
                difficulty=randrange(0, 5),
                quality=randrange(0, 5),
                difficultyCount=randint(0, 100),
                qualityCount=randint(0, 100)
            )

            question.save()
            question.topics.set(sample(all_topics, randrange(1, 5)))

            correctIndex = randrange(0, 4)

            for i in range(0, 4):
                distractor = Distractor(
                    content=fake.text(),
                    response=chr(ord('A') + i),
                    isCorrect=i == correctIndex)
                distractor.question = question
                distractor.save()
                distractors.append(distractor)

        for user in users:
            for i in range(0, 10):
                if randrange(0, 2) is 0:
                    userChoice = choice(distractors)
                    response = QuestionResponse(
                        response=userChoice,
                        user=user
                    )
                    response.save()
                    user_competency = QuestionService.update_competency(
                        user, userChoice.question, response)
                    user_competency.competency = randrange(0, 100)
                    user_competency.confidence = randrange(0, 100)

                    user_competency.save()

                    if randrange(0, 2) is 0:
                        rating = QuestionRating(
                            quality=randrange(0, 10),
                            difficulty=randrange(0, 10),
                            response=userChoice,
                            user=user
                        )
                        rating.save()
