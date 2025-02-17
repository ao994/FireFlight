#Andy, Alyssa

from django.shortcuts import render
from django.http import HttpResponse
from csp.decorators import csp_exempt

from .models import Species, Grid, Results

def index(request):
    #set page to load
    index_page = "home.html"

    #defines what happens when there is a GET request
    if request.method == "GET":  
        return render(request, index_page)


@csp_exempt #currently not enforcing the set csp protection rules
def map(request):
    #set page to load
    map_page = "map.html"
    
    #defines what happens when there is a GET request
    if request.method == "GET":
        #gets all the birds
        birds = Species.objects.all()
        return render(request, map_page, {'birds': birds})

@csp_exempt #currently not enforcing the set csp protection rules
def enchanted_circle_map(request):
    
    return render(request, 'enchanted_circle_map.html')