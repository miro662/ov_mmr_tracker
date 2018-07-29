from django.db import models, connection
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
        Deprecated and slow (1 query/1 record), use MatchWithPrevData instead
        """
        prevData = MatchWithPrevData.objects.get(pk=self.pk)
        prev = prevData.previousMatch()
        if prev is None:
            return None
        return Match.objects.get(pk=prev.pk)
    
    def mmrDifference(self):
        """ Returns how much MMR has changed from previous match, 0 if this is first match
        Deprecated and slow (1 query/1 record), use MatchWithPrevData instead
        """
        prevData = MatchWithPrevData.objects.get(pk=self.pk)
        if prevData.mmr_difference is None:
            return 0
        return prevData.mmr_difference

class MatchWithPrevData(models.Model):
    """ Describes single Overwatch match, with data about previous matches included
    This is read-only model!

    date - when this match was played, defaults to creation data
    user - which match is this
    mmr_after - player's MMR after match
    characters - characters played by user during this match
    last_match_id - ID of a previous match played by same user
    mmr_difference - MMR difference between this match and previous one played
        by same user

    last_match_id and mmr_difference are NULL on first match
    Use this model instead Match when informations about last match and MMR difference
    are important to you
    """

    date = models.DateTimeField(auto_now_add=True)
    mmr_after = models.PositiveIntegerField()
    characters = models.ManyToManyField(to=Character)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    last_match_id = models.IntegerField(null=True)
    mmr_difference = models.IntegerField(null=True)

    def __str__(self):
        return "{}, {}".format(str(self.user), str(self.date))

    class Meta:
        ordering = ('-date',)
        verbose_name_plural = 'matches'
        managed = False
        db_table = 'matches_prev_match_data'
    
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
        if self.last_match_id is None:
            return None
        try:
            m = MatchWithPrevData.objects.get(pk=self.last_match_id)
            return m
        except self.DoesNotExist:
            return None
    
    def mmrDifference(self):
        """ Returns how much MMR has changed from previous match, 0 if this is first match
        """
        previous_match = self.previousMatch()
        if previous_match is None:
            return 0
        return self.mmr_difference
