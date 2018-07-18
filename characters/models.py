from django.db import models

class Character(models.Model):
    """ Describes single Overwatch character

    name - name of character
    role - character's role, can be Damage (DMG), Tank (TNK), Support (SUP)
    """

    name = models.CharField(max_length=100)
    DAMAGE = 'DMG'
    TANK = 'TNK'
    SUPPORT = 'SUP'
    ROLE_CHOICES = (
        (DAMAGE, 'Damage'),
        (TANK, 'Tank'),
        (SUPPORT, 'Support'),
    )
    role = models.CharField(max_length=3, choices=ROLE_CHOICES)

    def __str__(self):
        return self.name
