from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.forms import ModelForm

from characters.models import Character
from .models import Match, MatchWithPrevData
from .forms import MatchForm

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


class MatchWithPrevDataModelTest(TestCase):
    """
    Tests MatchWithPrevData read-only model
    """
    def setUp(self):
        _createSampleData(self)
        self.withPrevData = [MatchWithPrevData.objects.get(pk=x.pk) for x in self.matches]
    
    def testStrMethod(self):
        """
        __str__ method should return string containing username and date of this match
        """
        self.assertEqual(str(self.withPrevData[0]), "{}, {}".format(str(self.withPrevData[0].user), str(self.withPrevData[0].date)))
    
    def testLastMatchMethod(self):
        """ 
        lastMatch method should return last match played by each user
        """
        self.assertEqual(MatchWithPrevData.lastMatch(self.users[0]), self.withPrevData[1])
        self.assertEqual(MatchWithPrevData.lastMatch(self.users[1]), self.withPrevData[3])
        self.assertIsNone(MatchWithPrevData.lastMatch(self.users[2]))
    
    def testPreviousMatchMethod(self):
        """ 
        previousMatch method should return previous match for every match (or None if there is no previous match)
        """
        self.assertEqual(self.withPrevData[1].previousMatch(), self.withPrevData[0])
        self.assertEqual(self.withPrevData[3].previousMatch(), self.withPrevData[2])

        self.assertIsNone(self.withPrevData[0].previousMatch())
        self.assertIsNone(self.withPrevData[2].previousMatch())
    
    def testMmrDifferenceMethod(self):
        """
        mmrDifference method should correctly calculate MMR difference
        """
        self.assertEqual(self.withPrevData[0].mmrDifference(), 0)
        self.assertEqual(self.withPrevData[1].mmrDifference(), 1000)
        self.assertEqual(self.withPrevData[2].mmrDifference(), 0)
        self.assertEqual(self.withPrevData[3].mmrDifference(), -1000)


class MatchModelTest(TestCase):
    """
    Tests Match model (including deprecated methods)
    """
    def setUp(self):
        _createSampleData(self)
    
    def testStrMethod(self):
        """
        __str__ method should return string containing username and date of this match
        """
        self.assertEqual(str(self.matches[0]), "{}, {}".format(str(self.matches[0].user), str(self.matches[0].date)))
    
    def testLastMatchMethod(self):
        """ 
        lastMatch method should return last match played by each user
        """
        self.assertEqual(Match.lastMatch(self.users[0]), self.matches[1])
        self.assertEqual(Match.lastMatch(self.users[1]), self.matches[3])
        self.assertIsNone(Match.lastMatch(self.users[2]))
    
    def testPreviousMatchMethod(self):
        """ 
        previousMatch method should return previous match for every match (or None if there is no previous match)
        """
        self.assertEqual(self.matches[1].previousMatch(), self.matches[0])
        self.assertEqual(self.matches[3].previousMatch(), self.matches[2])

        self.assertIsNone(self.matches[0].previousMatch())
        self.assertIsNone(self.matches[2].previousMatch())
    
    def testMmrDifferenceMethod(self):
        """
        mmrDifference method should correctly calculate MMR difference
        """
        self.assertEqual(self.matches[0].mmrDifference(), 0)
        self.assertEqual(self.matches[1].mmrDifference(), 1000)
        self.assertEqual(self.matches[2].mmrDifference(), 0)
        self.assertEqual(self.matches[3].mmrDifference(), -1000)


class IndexPageViewTest(TestCase):
    INDEX_PAGE_VIEW_URL='/matches/list'

    def setUp(self):
        _createSampleData(self)
        self.client = Client()

    def testIfReturnsNoMatchesForUserWithoutThem(self):
        """ Index page view should return empty matches table when there are no matches
        """
        self.assertTrue(self.client.login(username='user_without_matches', password='testTEST'))
        response = self.client.get(self.INDEX_PAGE_VIEW_URL)
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
        response = self.client.get(self.INDEX_PAGE_VIEW_URL)
        self.assertEqual(
            len(response.context['matches']),
            2
        )
        self.assertIn(matchData[0], response.context['matches'])
        self.assertIn(matchData[1], response.context['matches'])
        self.client.logout()

        # Test for user randy
        self.assertTrue(self.client.login(username='randy', password='testTEST'))
        response = self.client.get(self.INDEX_PAGE_VIEW_URL)
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
        response = self.client.get(self.INDEX_PAGE_VIEW_URL)
        # Match added later should be first
        self.assertEqual(
            response.context['matches'][0]['pk'],
            self.matches[1].pk
        )
        self.assertEqual(
            response.context['matches'][1]['pk'],
            self.matches[0].pk
        )
        self.client.logout()
    

class NewMatchViewTest(TestCase):
    NEW_MATCH_VIEW_URL='/matches/new'

    def setUp(self):
        _createSampleData(self)
        self.client = Client()
        # Log in
        self.assertTrue(
            self.client.login(username='jimlahey', password='testTEST')
        )

    def tearDown(self):
        # Log out
        self.client.logout()

    def testIfGetRequestReturnsEmptyModelFormWithoutRelatedInstance(self):
        """ GET request to /matches/new should return empty ModelForm
            without related instance
        """
        # Make GET request to /matches/new
        response = self.client.get(self.NEW_MATCH_VIEW_URL)
        # Get form
        form = response.context['form']
        # Check if MatchForm hasn't instance; if so, PK should be None
        self.assertFalse(form.is_bound)
        self.assertIsNone(form.instance.pk)

    def testIfPostRequestWithValidDataCreatesValidInstance(self):
        """ POST request to /matches/new with valid data should create
            new Match
        """
        # Make POST request with valid data
        response = self.client.post(self.NEW_MATCH_VIEW_URL, data={
            'characters': self.characters[0].pk,
            'mmr_after': 5000
        })

        # Check if there is new match in database
        new_match = Match.objects.get(mmr_after=5000)
        self.assertEqual(
            new_match.user,
            self.users[0],
            'New match\'s user should be user that is currently logged in'
        )

        # Check if we've got redirect request (302 - Found)
        self.assertEqual(302, response.status_code)

    def testIfPostRequestWithInvalidDataDoesNotCreateNewInstance(self):
        """ POST request to /matches/new with invalid data should not create
            new Match, it should render matches_new template and pass 
            form with errors to it
        """
        def checkResponse(self, response, expected_mmr_after=None):
            """ Check if response contains invalid form and nothing were created
            """
            form = response.context["form"]
            self.assertFalse(form.is_valid(), "Form should be invalid")
            if expected_mmr_after is not None:
                with self.assertRaises(Match.DoesNotExist):
                    Match.objects.get(mmr_after=expected_mmr_after)

        # Make POST requests with invalid data and check responses
        # MMR < 0
        response = self.client.post(self.NEW_MATCH_VIEW_URL, data={
            'characters': self.characters[0].pk,
            'mmr_after': -20
        })
        checkResponse(self, response, -20)
        # No characters
        response = self.client.post(self.NEW_MATCH_VIEW_URL, data={
            'characters': '',
            'mmr_after': 500
        })
        checkResponse(self, response, 500)
        # No data
        response = self.client.post(self.NEW_MATCH_VIEW_URL, data={})
        checkResponse(self, response)


class EditMatchViewTest(TestCase):
    EDIT_MATCH_VIEW_URL='/matches/edit/{}'

    def setUp(self):
        _createSampleData(self)
        self.client = Client()
        # Log in
        self.assertTrue(
            self.client.login(username='jimlahey', password='testTEST')
        )

    def tearDown(self):
        # Log out
        self.client.logout()

    def testTryingToEditNotUsersMatch(self):
        """ View should return Forbidden error when someone tries to edit 
            match that does not belong to currently logged in user
        """
        # Test for GET request
        response = self.client.get(
            self.EDIT_MATCH_VIEW_URL.format(self.matches[2].pk)
        )
        self.assertEqual(
            response.status_code,
            403,
            'HTTP status code for response to GET should be 403 (Forbidden)'
        )
        
        # Test for POST request
        response = self.client.post(self.EDIT_MATCH_VIEW_URL.format(self.matches[2].pk), data = {
            'characters': self.characters[0].pk,
            'mmr_after': 600
        })
        self.assertEqual(
            response.status_code,
            403,
            'HTTP status code for response to POST should be 403 (Forbidden)'
        )
        with self.assertRaises(Match.DoesNotExist):
            Match.objects.get(mmr_after=600)

    def testGetRequest(self):
        """ View should return MatchForm with attached model
            when request method is GET
        """
        response = self.client.get(
            self.EDIT_MATCH_VIEW_URL.format(self.matches[0].pk)
        )
        form = response.context["form"]
        self.assertEqual(
            form.instance,
            Match.objects.get(pk=self.matches[0].pk),
            'Match instance bound to form should be match with given primary key'
        )
        self.assertEqual(
            self.matches[0].pk,
            response.context['pk'],
            'PK context value should be edited object\'s primary key'
        )

    def testPostRequestWithValidData(self):
        """ If data sent in POST request is correct, view should
            update this model with given data
        """
        response = self.client.post(
            self.EDIT_MATCH_VIEW_URL.format(self.matches[0].pk),
            data={
                'mmr_after': 700,
                'characters': self.characters[1].pk
            }
        ) 
        # Load updated match data from database
        match = Match.objects.get(pk=self.matches[0].pk)
        self.assertEqual(
            list(match.characters.all()),
            [self.characters[1]],
            'Characters should be modified by valid POST request'
        ) 
        self.assertEqual(
            match.mmr_after,
            700,
            'MMR should be modified by valid POST request'
        )
        self.assertEqual(
            response.status_code,
            302,
            'Response should have 302 (Found) status code - redirect'
        )

    def testPostRequestWithInvalidData(self):
        """ If data sent in POST request is incorrect, view should
            render form with errors and change nothing
        """
        def checkResponse(self, response, instance, former_mmr, former_characters):
            """ Check if response contains invalid form and nothing were created
            """
            form = response.context["form"]
            self.assertFalse(form.is_valid())
            self.assertEqual(
                list(instance.characters.all()),
                former_characters,
                'Characters should not be modified by invalid POST request'
            ) 
            self.assertEqual(
                instance.mmr_after,
                former_mmr,
                'MMR should not be modified by invalid POST request'
            )
            self.assertEqual(
                instance.pk,
                response.context['pk'],
                'PK context value should be edited object\'s primary key'
            )

        # Make POST requests with invalid data and check responses
        # MMR < 0
        response = self.client.post(
            self.EDIT_MATCH_VIEW_URL.format(self.matches[0].pk), data={
                'characters': self.characters[0].pk,
                'mmr_after': -20
            }
        )
        checkResponse(self, response, self.matches[0], 2000, [self.characters[0]])
        # No characters
        response = self.client.post(
            self.EDIT_MATCH_VIEW_URL.format(self.matches[0].pk), data={
                'characters': '',
                'mmr_after': 2000
            }
        )
        checkResponse(self, response, self.matches[0], 2000, [self.characters[0]])
        # No data
        response = self.client.post(
            self.EDIT_MATCH_VIEW_URL.format(self.matches[0].pk), data={}
        )
        checkResponse(self, response, self.matches[0], 2000, [self.characters[0]])

    def test404(self):
        """ Test if trying to edit non-existent match returns 404
        """
        response = self.client.get(self.EDIT_MATCH_VIEW_URL.format(12345))
        self.assertEqual(
            response.status_code,
            404,
            'Status code of GET edit request of non-existent Match should be 404'
        )
        response = self.client.post(self.EDIT_MATCH_VIEW_URL.format(12345))
        self.assertEqual(
            response.status_code,
            404,
            'Status code of POST edit request of non-existent Match should be 404'
        )


class DeleteMatchTestView(TestCase):
    DELETE_MATCH_VIEW_URL = '/matches/delete/{}'
    
    def setUp(self):
        _createSampleData(self)
        self.client = Client()
        # Log in
        self.assertTrue(
            self.client.login(username='jimlahey', password='testTEST')
        )

    def tearDown(self):
        # Log out
        self.client.logout()
    
    def test404(self):
        """ Test if trying to delete non-existent match returns 404
        """
        response = self.client.get(self.DELETE_MATCH_VIEW_URL.format(12345))
        self.assertEqual(
            response.status_code,
            404,
            'Status code of GET delete request on non-existent Match should be 404'
        )
    
    def testDeletingMatch(self):
        """ Test if DeleteMatch viev properly deletes match belonging
            to currently logged in user
        """
        pk_of_deleted = self.matches[1].pk
        self.assertEqual(self.matches[1].user, self.users[0])
        response = self.client.get(self.DELETE_MATCH_VIEW_URL.format(pk_of_deleted))
        # Try to find recently deleted match
        with self.assertRaises(Match.DoesNotExist):
            Match.objects.get(pk=pk_of_deleted)
        self.assertEqual(
            response.status_code,
            302,
            'Response should have 302 (Found) status code - redirect'
        )

    def testTryingToDeleteNotLoggedInUserMatch(self):
        """ View should return Forbidden error when someone tries to delete 
            match that does not belong to currently logged in user and not
            delete that match
        """
        pk_of_deleted = self.matches[2].pk
        response = self.client.get(
            self.DELETE_MATCH_VIEW_URL.format(pk_of_deleted)
        )
        self.assertEqual(
            response.status_code,
            403,
            'HTTP status code for response to GET should be 403 (Forbidden)'
        )
        self.assertIsNotNone(Match.objects.get(pk=pk_of_deleted))
