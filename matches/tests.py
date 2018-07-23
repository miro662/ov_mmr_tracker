from django.test import TestCase, Client
from django.contrib.auth.models import User

from characters.models import Character
from .models import Match

def _createSampleData(self):
    self.users = [
        User.objects.create_user('jimlahey'),
        User.objects.create_user('randy'),
        User.objects.create_user('user_without_matches')
    ]
    for u in self.users:
        u.set_password('testTEST')
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

class MatchModelTest(TestCase):
    def setUp(self):
        _createSampleData(self)
    
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
    
    def testMmrDifferenceMethod(self):
        """ Tests if mmrDifference method correctly calculates MMR difference
        """
        self.assertEqual(self.matches[0].mmrDifference(), 0)
        self.assertEqual(self.matches[1].mmrDifference(), 1000)
        self.assertEqual(self.matches[2].mmrDifference(), 0)
        self.assertEqual(self.matches[3].mmrDifference(), -1000)

class IndexPageViewTest(TestCase):
    def setUp(self):
        _createSampleData(self)
        self.client = Client()

    def testIfReturnsNoMatchesForUserWithoutThem(self):
        """ Index page view should return empty matches table when there are no matches
        """
        self.assertTrue(self.client.login(username='user_without_matches', password='testTEST'))
        response = self.client.get('/matches/list')
        self.assertEqual(
            len(response.context['matches']), 
            0
        )
        self.client.logout()

    def testIfReturnsMatches(self):
        """ Index page view should return matches histroy for currently logged user
        """
        # Prepare match data
        matchData = [
            {
                'pk': m.pk,
                'characters_list': ', '.join([str(x) for x in list(m.characters.all())]),
                'mmr_after': m.mmr_after,
                'mmr_difference': m.mmrDifference(),
                'won': m.mmrDifference() > 0,
                'lost': m.mmrDifference() < 0
            } for m in self.matches
        ]

        # Test for user jimlahey
        self.assertTrue(self.client.login(username='jimlahey', password='testTEST'))
        response = self.client.get('/matches/list')
        self.assertEqual(
            len(response.context['matches']),
            2
        )
        self.assertIn(matchData[0], response.context['matches'])
        self.assertIn(matchData[1], response.context['matches'])
        self.client.logout()

        # Test for user randy
        self.assertTrue(self.client.login(username='randy', password='testTEST'))
        response = self.client.get('/matches/list')
        self.assertEqual(
            len(response.context['matches']),
            2
        )
        self.assertIn(matchData[2], response.context['matches'])
        self.assertIn(matchData[3], response.context['matches'])
        self.client.logout()

    def testIfMatchesAreInCorrectOrder(self):
        """ Tests if matches are passed in correct order 
        """
        self.assertTrue(self.client.login(username='jimlahey', password='testTEST'))
        response = self.client.get('/matches/list')
        # Match added later should be first
        self.assertEqual(
            response.context['matches'][0]['pk'],
            self.matches[1].pk
        )
        self.assertEqual(
            response.context['matches'][1]['pk'],
            self.matches[0].pk
        )