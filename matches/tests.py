from django.test import TestCase
from django.contrib.auth.models import User

from characters.models import Character
from .models import Match

class MatchModelTest(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user('jimlahey'),
            User.objects.create_user('randy'),
            User.objects.create_user('user_without_matches')
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
        self.matches[1].characters.set([self.characters[1]])
        self.matches[2].characters.set([self.characters[0]])
        self.matches[3].characters.set([self.characters[0], self.characters[1]])
        for m in self.matches:
            m.save()
    
    def testStrMethod(self):
        """ Tests if str method works as it should
        """
        self.assertEqual(str(self.matches[0]), "{}, {}".format(str(self.matches[0].user), str(self.matches[0].date)))
    
    def testLastMatchMethod(self):
        """ Tests if lastMatch method returns last match played by each user
        """
        self.assertEqual(Match.lastMatch(self.users[0]), self.matches[1])
        self.assertEqual(Match.lastMatch(self.users[1]), self.matches[3])
        self.assertIsNone(Match.lastMatch(self.users[2]))
    
    def testPreviousMatchMethod(self):
        """ Tests if previousMatch method returns previous match for every match (or None if there is no previous match)
        """
        self.assertEqual(self.matches[1].previousMatch(), self.matches[0])
        self.assertEqual(self.matches[3].previousMatch(), self.matches[2])

        self.assertIsNone(self.matches[0].previousMatch())
        self.assertIsNone(self.matches[2].previousMatch())