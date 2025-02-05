#Andy, Alyssa

from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    index_page = "index.html"

    return render(request, index_page)


def map(request):
    map_page = "map.html"

    return render(request, map_page)