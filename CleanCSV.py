import csv

csvFileName = "test"

with open(csvFileName + "_out.csv", 'w') as outcsvFile:
        csvWriter = csv.writer(outcsvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        with open(csvFileName + ".csv", 'rbU') as incsvFile:
            csvReader = csv.reader(incsvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in csvReader:
                if len(row) < 4 or len(row) > 4:
                    print '# -', row
                    continue
                else:
                    if not row[0].isdigit():
                        print 'id -', row, row[0]
                        continue

                    try:
                        x = float(row[2])
                    except ValueError:
                        print 'x -', row, row[2]
                        continue

                    try:
                        y = float(row[3])
                    except ValueError:
                        print 'y -', row, row[3]
                        continue

                    csvWriter.writerow(row)

