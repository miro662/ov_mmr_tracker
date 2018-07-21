from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Match

@login_required
def index_page(request):
    matches = Match.objects.filter(user=request.user)
    return render(request, "matches_list.html", {
        'matches': [
            {
                'characters': m.characters.all(),
                'characters_list': ', '.join([str(x) for x in list(m.characters.all())]),
                'mmr_after': m.mmr_after,
                'mmr_difference': m.mmrDifference(),
                'won': m.mmrDifference() > 0,
                'lost': m.mmrDifference() < 0,
            } for m in matches
        ]
    })