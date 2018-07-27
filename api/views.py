from rest_framework import viewsets
from rest_framework import permissions

from characters.models import Character 
from matches.models import Match
from .serializers import CharacterSerializer, MatchSerializer
from .permissions import IsMatchOwner

class CharactersViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = CharacterSerializer
    queryset = Character.objects.all()


class MatchesViewset(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    permission_classes = (IsMatchOwner, permissions.IsAuthenticated)
    queryset = Match.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return Match.objects.filter(user=user)