from django.test import TestCase
from .models import Character


class TestCharacterModel(TestCase):
    def setUp(self):
        self.character = Character(name="TestCharacter", role=Character.SUPPORT)
    
    def test_str(self):
        self.assertEqual(self.character.name, str(self.character))
