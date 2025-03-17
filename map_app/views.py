#Andy, Alyssa

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from csp.decorators import csp_exempt
import csv, datetime

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
    
    #defines what happens when the map is updated
    if request.method == "POST":
        # IN PROGRESS
        getCSV()
        

@csp_exempt #currently not enforcing the set csp protection rules
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
        # variable for holding current row
        row = []

        # for field in database row's fields
        for field in fields:
            # get the attribute's value
            value = getattr(entry, field)

            # find out what it is
            fieldObj = modelChoice._meta.get_field(field)
            
            # if a primary key, get the key's id value
            if fieldObj.is_relation:
                value = getattr(value, "id", value)

            # add value to the current row
            row.append(value)

        # write the current row to the csv
        writer.writerow(row)

    # return the http response, download the csv
    return response

@csp_exempt
def instructions(request):
    
    instructions_page = "instructions.html"

    #defines what happens when there is a GET request
    if request.method == "GET":  
        return render(request, instructions_page)
    

#####################################################
#             Query to csv functions                #
#####################################################

#IN PROGRESS
def getCSV(birdList):
    #get date and time for export name
    curTime = datetime.datetime.now()
    timeStr = curTime.strftime("%m-%d-%Y_%H_%M")

    # Create the HttpResponse object with the appropriate CSV header.
    filename = f"bird_data_{timeStr}.csv"
    csvOutput = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

    # start a csv writer
    writer = csv.writer(csvOutput)


    # get the fields and write them to the csv
    # IN PROGRESS- make custom fields (bird name, etc that was specified by clients)
    fields = [field.name for field in modelChoice._meta.fields]
    writer.writerow(fields)

    #for bird in birdlist? or an if statement: if bird is in birdlist, print row

    return csvOutput