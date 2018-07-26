from rest_framework import serializers

from characters.models import Character
from matches.models import Match


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ('id', 'name', 'role')


class MatchSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField()
    class Meta:
        model = Match
        fields = ('id', 'characters', 'date', 'mmr_after', 'user')