#Andy, Alyssa

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from csp.decorators import csp_exempt
import csv

from .models import Species, Grid, Results

def index(request):
    #set page to load
    index_page = "home.html"

    #defines what happens when there is a GET request
    if request.method == "GET":  
        return render(request, index_page)

@csp_exempt
def map(request):
    #set page to load
    map_page = "map.html"
    
    #defines what happens when there is a GET request
    if request.method == "GET":
        #gets all the birds
        birds = Species.objects.all()
        return render(request, map_page, {'birds': birds})

@csp_exempt
def enchanted_circle_map(request):
    
    return render(request, 'enchanted_circle_map.html')

@csp_exempt
def query(request, modelName):
    # Create the HttpResponse object with the appropriate CSV header.
    filename = f"{modelName.lower()}_data.csv"
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

    # make sure a valid model type is being requested
    modelDict = {
        "Species" : Species,
        "species" : Species,
        "Grid" : Grid,
        "grid" : Grid,
        "Results" : Results,
        "results" : Results
    }

    # get the db model/table we want:
    modelChoice = modelDict.get(modelName)
    # otherwise, return an error
    if modelChoice is None:
        return HttpResponseNotFound("<h1>Error: Model Not Found!</h1>")
    
    # start a csv writer
    writer = csv.writer(response)

    # get the fields and write them to the csv
    fields = [field.name for field in modelChoice._meta.fields]
    writer.writerow(fields)

    # get all elements of model from db
    modelQuerySet = modelChoice.objects.all()

    # write all elements to the csv
    for entry in modelQuerySet:
        writer.writerow([getattr(entry, field) for field in fields])

    # return the http response, download the csv
    return response

@csp_exempt
def instructions(request):
    
    instructions_page = "instructions.html"

    #defines what happens when there is a GET request
    if request.method == "GET":  
        return render(request, instructions_page)