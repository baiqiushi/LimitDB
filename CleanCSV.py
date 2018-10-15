import csv

inCSVFileName = "coord_tweets_max.csv.2"
outCSVFileName = "coord_tweets_max.csv.3"

with open(outCSVFileName, 'w') as outcsvFile:
        csvWriter = csv.writer(outcsvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        with open(inCSVFileName, 'rbU') as incsvFile:
            csvReader = csv.reader(incsvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in csvReader:
                # Number of columns wrong
                if len(row) < 9 or len(row) > 9:
                    print '# -', row
                    continue
                else:
                    # id is not digit
                    if not row[0].isdigit():
                        print 'id -', row, row[0]
                        continue

                    # x is not float
                    try:
                        x = float(row[3])
                    except ValueError:
                        print 'x -', row, row[3]
                        continue

                    # y is not float
                    try:
                        y = float(row[4])
                    except ValueError:
                        print 'y -', row, row[4]
                        continue

                    # x0 is not float
                    try:
                        x0 = float(row[5])
                    except ValueError:
                        print 'x0 -', row, row[5]
                        continue

                    # y0 is not float
                    try:
                        y0 = float(row[6])
                    except ValueError:
                        print 'y0 -', row, row[6]
                        continue

                    # x1 is not float
                    try:
                        x1 = float(row[7])
                    except ValueError:
                        print 'x1 -', row, row[7]
                        continue

                    # y1 is not float
                    try:
                        y1 = float(row[8])
                    except ValueError:
                        print 'y1 -', row, row[8]
                        continue

                    # # remove quotes in create_at
                    # row[1] = row[1].replace('\\\"', '')
                    #
                    # remove quotes in text
                    row[2] = row[2].replace('"', '')

                    csvWriter.writerow(row)

