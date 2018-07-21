from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from .models import Match
from .forms import MatchForm

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

@login_required
def new_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.user = request.user
            match.save()
            form.save_m2m()
            return HttpResponseRedirect('/matches/list')
        else:
            return render(request, "new_match.html", {
                'form': form
            })
    elif request.method == 'GET':
        return render(request, "new_match.html", {
            'form': MatchForm
        })