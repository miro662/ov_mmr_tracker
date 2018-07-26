from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.serializers import DateTimeField

from characters.models import Character
from matches.models import Match
from .serializers import CharacterSerializer, MatchSerializer

class TestCharacterSerializer(TestCase):
    def setUp(self):
        self.character = Character(name='Test', role=Character.DAMAGE)
        self.character.save()

    def testSerializingCharacter(self):
        """
        Test if character serialization works correctly
        """
        expected_data = {
            'id': self.character.id,
            'name': self.character.name,
            'role': self.character.role
        }

        serializer = CharacterSerializer(self.character)
        self.assertEqual(
            expected_data,
            serializer.data,
            'Serializer should return data in expected format'
        )

    def testDeserializingCharacter(self):
        """
        Test if character deserialization works correctly
        """
        newData = {
            'name': 'New character',
            'role': Character.TANK
        }
        serializer = CharacterSerializer(data=newData)
        self.assertTrue(
            serializer.is_valid(),
            'Serialization of correct data is valid'
        )
        self.assertEqual(
            serializer.validated_data['name'],
            newData['name'],
            'Serialized data should have the same character name as in data'
        )
        self.assertEqual(
            serializer.validated_data['role'],
            newData['role'],
            'Serialized data should have the same role as in data'
        )


class TestMatchSerializer(TestCase):
    def setUp(self):
        self.characters = [
            Character(name='Test1', role=Character.DAMAGE),
            Character(name='Test2', role=Character.DAMAGE)
        ]
        for c in self.characters:
            c.save()

        self.user = User.objects.create_user('testuser')

        self.match = Match(user=self.user, mmr_after=1000)
        self.match.save()
        self.match.characters.set(self.characters)
    
    def testSerializingMatch(self):
        # Test if match serialization works correctly
        expected_data = {
            'id': self.match.id,
            'characters': [c.id for c in self.match.characters.all()],
            'date': DateTimeField().to_representation(self.match.date),
            'mmr_after': self.match.mmr_after,
            'user': self.match.user
        }
        serializer = MatchSerializer(self.match)
        self.assertEqual(
            expected_data,
            serializer.data,
            'Serializer should return data in expected format'
        )