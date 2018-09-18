import csv

csvFileName = "test"

with open(csvFileName + "_out.csv", 'w') as outcsvFile:
        csvWriter = csv.writer(outcsvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        with open(csvFileName + ".csv", 'rbU') as incsvFile:
            csvReader = csv.reader(incsvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in csvReader:
                if len(row) < 4 or len(row) > 4:
                    print row
                    continue
                else:
                    csvWriter.writerow(row)

