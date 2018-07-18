from django.test import TestCase
from django.contrib.auth.models import User

from characters.models import Character
from .models import Match

class MatchModelTest(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user('jimlahey'),
            User.objects.create_user('randy')
        ]
        for u in self.users:
            u.save()
        self.characters = [
            Character(name='char1', role=Character.SUPPORT),
            Character(name='char2', role=Character.DAMAGE),
        ]
        for c in self.characters:
            c.save()
        self.matches = [
            Match(
                mmr_after=2000,
                user=self.users[0],
            ),
            Match(
                mmr_after=3000,
                user=self.users[0],
            ),
            Match(
                mmr_after=3000,
                user=self.users[1],
            ),
            Match(
                mmr_after=2000,
                user=self.users[1],
            ),
        ]
        for m in self.matches:
            m.save()
        self.matches[0].characters.set([self.characters[0]])
        self.matches[0].characters.set([self.characters[1]])
        self.matches[0].characters.set([self.characters[0]])
        self.matches[0].characters.set([self.characters[0], self.characters[1]])
        for m in self.matches:
            m.save()
    
    def testStrMethod(self):
        """ Tests if str method works as it should
        """
        self.assertEqual(str(self.matches[0]), "{}, {}".format(str(self.matches[0].user), str(self.matches[0].date)))