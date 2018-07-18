from django.db import models
from django.contrib.auth.models import User

from characters.models import Character


class Match(models.Model):
    """ Describes single Overwatch match

    date - when this match was played, defaults to creation data
    user - which match is this
    mmr_after - player's MMR after match
    characters - characters played by user during this match
    """

    date = models.DateTimeField(auto_now_add=True)
    mmr_after = models.PositiveIntegerField()
    characters = models.ManyToManyField(to=Character)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return "{}, {}".format(str(self.user), str(self.date))

    class Meta:
        ordering = ('-date',)
        verbose_name_plural = 'matches'
    
    @classmethod
    def lastMatch(cls, of:User):
        """ Return last match played by given user, otherwise return None
        """
        user_matches = cls.objects.filter(user=of).order_by('-date')
        if len(user_matches) == 0:
            return None
        return user_matches[0]

    def previousMatch(self):
        """ Returns match played before this match by same user
        """
        previous_matches = Match.objects.filter(user=self.user, date__lt=self.date)
        if len(previous_matches) == 0:
            return None
        return previous_matches[0]
    
    def mmrDifference(self):
        """ Returns how much MMR has changed from previous match, 0 if this is first match
        """
        previous_match = self.previousMatch()
        if previous_match is None:
            return 0
        return self.mmr - previous_match.mmr
