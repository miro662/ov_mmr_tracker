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