from django.core.management.base import BaseCommand
from map_app.models import Species, Grid, Results
import csv

# define command's class
class Command(BaseCommand):
    # main help
    help = "Used to auto-populate the database from a file"

    # add argument to command
    def add_arguments(self, parser):
        # add a file name/path argument
        parser.add_argument('filePath', type=str, help="File name of/path to file to extract data from")

    # main command function, takes in self, positional args, and keyword arguments
    def handle(self, *args, **kwargs):
        # get the file/path
        filePath = kwargs['filePath']
        print(filePath)

        # try to open file
        try:
            with open(filePath, "r") as inFile:
                # create a csv reader object
                csvreader = csv.reader(inFile)
                
                # skip field names
                fields = next(csvreader)
                print(fields)
                match fields[0]:
                    # if species file
                    case "speciesID":
                        # go through data line by line
                        for line in csvreader:
                            # get the bird ID
                            birdID = int(line[0])
                            
                            # get the species name
                            speciesName = line[1]
                            
                            # get the bird code
                            birdCode = line[2]
                            
                            # check to see if an element with this combination of FKs already exists
                            try:
                                obj = Species.objects.filter(speciesID=birdID).first()
                            except Exception as e:
                                print({e})
                            # if it exists, update it
                            if obj:
                                obj.speciesID = birdID
                                obj.species = speciesName
                                obj.birdcode = birdCode
                            # otherwise, insert
                            else:
                                obj = Species(speciesID=birdID, species=speciesName, birdcode=birdCode)
                            # save to the database
                            try:
                                obj.save()
                            except Exception as e:
                                print(f'{e}')
                    
                    # if grid file
                    case "ï»¿OID_":
                        # go through data line by line
                        for line in csvreader:
                            # get the OID
                            oid = int(line[0])

                            # get the grid id
                            gridID = line[1]

                            # get Grid_E_NAD83
                            gridENAD = int(line[2])

                            # get Grid_N_NAD83
                            gridNNAD = int(line[3])

                            # get UTM_Zone
                            utmZone = int(line[4])

                            # get Grid_Lat_NAD83
                            gridLatNAD = float(line[5])

                            # get Grid_Long_NAD83
                            gridLongNAD = float(line[6])

                            # get BCR
                            bcr = int(line[7])

                            # get MgmtEntity
                            mgmtEnt = line[8]

                            # get MgmtRegion
                            mgmtReg = line[9]

                            # get MgmtUnit
                            mgmtUnit = line[10]

                            # get MgmtDistrict
                            mgmtDist = line[11]

                            # get County
                            county = line[12]

                            # get State
                            state = line[13]

                            # get PriorityLandscape
                            priLand = line[14]

                            # get inPL
                            inpl = bool(line[15])

                            # check to see if an element with this combination of FKs already exists
                            obj = Grid.objects.filter(OID=oid).first()

                            # if it exists, update it
                            if obj:
                                obj.OID = oid
                                obj.Grid_ID = gridID
                                obj.Grid_E_NAD83 = gridENAD
                                obj.Grid_N_NAD83 = gridNNAD
                                obj.UTM_Zone = utmZone
                                obj.Grid_Lat_NAD83 = gridLatNAD
                                obj.Grid_Long_NAD83 = gridLongNAD
                                obj.BCR = bcr
                                obj.MgmtEntity = mgmtEnt
                                obj.MgmtRegion = mgmtReg
                                obj.MgmtUnit = mgmtUnit
                                obj.MgmtDistrict = mgmtDist
                                obj.County = county
                                obj.State = state
                                obj.PriorityLandscape = priLand
                                obj.inPL = inpl
                            # otherwise, insert
                            else:
                                obj = Grid(OID=oid, Grid_ID=gridID, Grid_E_NAD83=gridENAD, Grid_N_NAD83=gridNNAD, UTM_Zone=utmZone,
                                               Grid_Lat_NAD83=gridLatNAD, Grid_Long_NAD83=gridLongNAD, BCR=bcr, MgmtEntity=mgmtEnt,
                                                 MgmtRegion=mgmtReg, MgmtUnit=mgmtUnit, MgmtDistrict=mgmtDist, County=county, State=state,
                                                   PriorityLandscape=priLand, inPL=inpl)
                            # save to the database
                            try:
                                obj.save()
                            except Exception as e:
                                print(f'{e}')

                    # if results file
                    case "parameter":
                        # go through data line by line
                        for line in csvreader:
                            # clean up first element of csv
                            birdGrid = line[0].strip("psi[]")
                            birdGrid = birdGrid.split(",")

                            # get the first element, bird ID
                            birdID = int(birdGrid[0])
                            # get the second element, grid ID
                            gridNum = int(birdGrid[1])

                            # get lbci
                            lbciInput = float(line[1])

                            # get posterior median
                            postMed = float(line[2])

                            # get ubci
                            ubciInput = float(line[3])
                            # check to see if an element with this combination of FKs already exists
                            obj = Results.objects.filter(bird_speciesID=birdID, gridID=gridNum).first()

                            # if it exists, update it
                            if obj:
                                obj.bird_speciesID = birdID
                                obj.gridID = gridNum
                                obj.lbci = lbciInput
                                obj.posterior_median = postMed
                                obj.ubci = ubciInput
                            # otherwise, insert
                            else:
                                obj = Results(bird_speciesID_id=birdID, gridID_id=gridNum, lbci=lbciInput, posterior_median=postMed, ubci=ubciInput)
                            # save to the database
                            try:
                                obj.save()
                            except Exception as e:
                                print(f'{e}')

            self.stdout.write(self.style.SUCCESS(f'Database populated successfully from {filePath}!'))

        # if file inaccessible, return an error
        except Exception as e2:
            print(f'Error: {e2}')