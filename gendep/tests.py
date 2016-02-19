from django.test import TestCase

import datetime
from django.utils import timezone

from .models import Dependency

# I need to finish these test cases for gendep:
# see: https://docs.djangoproject.com/en/1.9/intro/tutorial05/

#class QuestionMethodTests(TestCase):

#    def test_was_published_recently_with_future_question(self):
#        """
#        was_published_recently() should return False for questions whose
#        pub_date is in the future.
#        """
#        time = timezone.now() + datetime.timedelta(days=30)
#        future_question = Question(pub_date=time)
#        self.assertEqual(future_question.was_published_recently(), False)
