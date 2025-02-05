import csv

# function for processing csv
def readCsv():
    # get name of input file from user
    fileName = input("Please enter the .csv file you would like to export from: ")
    # get name of output file to export to(or name of file to be created for export)
    outputName = input("Please enter the name of the file you would like to export to: ")

    # try to open file
    try:
        # open input file
        with open( fileName, "r" ) as file:
            # open export file
            with open( outputName, "w" ) as outputFile:
                reader = csv.reader(file)
                # with our database, first line is typically column names
                # we'll collect them as a list and hold onto them for later use
                colNames = file.readline()
                # get rid of whitespace chars
                colNames = colNames.strip()
                # make a list delimited by commas
                colNames = colNames.split(',')

                # ask user for specified field to export
                rowStart = input("Enter desired row range starting index: ")
                rowEnd = input("Enter desired row range end index: ")
                # make ints
                rowStart = int(rowStart)
                rowEnd = int(rowEnd)
                print("Select column(s) to use: \n")
                for index in range(len(colNames)):
                    print(str(index) + ": " + colNames[index])
                # get list of cols to export results from:
                choiceList = []
                choosingCols = True
                # while user still choosing
                while( choosingCols ):
                    # get a user's choice of column
                    colChoice = input("Enter a columns index: ")
                    # append choice to list of chosen cols
                    choiceList.append(int(colChoice))
                    # see if user wants more columns
                    exitChoice = input("Would you like to select another? Y/N: ")
                    # if done, set choosingCols to false
                    if exitChoice == "N":
                        choosingCols = False

                # since csv reader object can't be indexed, create a count to make
                # sure we stay in the desired row range
                rowCount = 0
                # for elements in list of cols chosen:
                for colIndex in choiceList:
                    # write that column's title in the first line
                    outputFile.write(colNames[colIndex])
                    # if last element, don't add a comma
                    if(colIndex != choiceList[-1]):
                        outputFile.write(", ")
                # add a newline after we're done with the title line
                outputFile.write("\n")
                # for rows in csv reader:
                for row in reader:
                    # if count in range
                    if rowStart <= rowCount <= rowEnd:
                        # for elements in list of cols chosen:
                        for colIndex in choiceList:
                            # write value that row has at column index
                            outputFile.write(row[colIndex])
                            # add a comma until at last column
                            if(colIndex != choiceList[-1]):
                                outputFile.write(", ")
                        # add a new line unless last row
                        if(rowCount != rowEnd):
                            outputFile.write("\n")
                    # increment row count
                    rowCount = rowCount + 1

    # if error encountered
    except:
        # return an error
        print("Error!")


# main function
def main():
    readCsv()

main()
