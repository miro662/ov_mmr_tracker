from django.shortcuts import render
from django.http import HttpResponse


def index_page(request):
    page = """
<html>
    <head>
        <meta charset="utf-8">
        <title>Temporary main page</title>
    </head>
    <body>
        <p>Temporary main page</p>
    </body>
</html>
    """
    return HttpResponse(page)