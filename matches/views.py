from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden

from .models import Match, MatchWithPrevData
from .forms import MatchForm

@login_required
def index_page(request):
    matches = MatchWithPrevData.objects.filter(user=request.user)
    return render(request, "matches_list.html", {
        'matches': [
            {
                'pk': m.pk,
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
            'form': MatchForm()
        })

@login_required
def edit_match(request, pk):
    try:
        match = Match.objects.get(pk=pk)
    except Match.DoesNotExist:
        raise Http404('Match does not exist')
    if match.user != request.user:
        return HttpResponseForbidden('This match is not a match of a logged user!')
    
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save()
            return HttpResponseRedirect('/matches/list')
        else:
            return render(request, "edit_match.html", {
                'form': form,
                'pk': match.pk
            })
    elif request.method == 'GET':
        form = MatchForm(instance=match)
        return render(request, "edit_match.html", {
            'form': form,
            'pk': match.pk
        })

@login_required
def delete_match(request, pk):
    try:
        match = Match.objects.get(pk=pk)
    except Match.DoesNotExist:
        raise Http404('Match does not exist')
    
    if match.user != request.user:
        return HttpResponseForbidden('This match is not a match of a logged user!')
    match.delete()
    return HttpResponseRedirect('/matches/list')