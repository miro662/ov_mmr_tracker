from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Match

@login_required
def index_page(request):
    matches = Match.objects.filter(user=request.user)
    return render(request, "matches_list.html", {
        'matches': matches
    })