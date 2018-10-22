import ijson
import csv
import random
import time


def extractCSV(p_inFile, p_outFile):
    print "Converting [" + p_inFile + "] to [" + p_outFile + "] ... ..."
    inFile = open(p_inFile, 'r')
    outFile = open(p_outFile, 'w')

    parser = ijson.parse(inFile)
    cnt = 0
    t0 = time.time()
    for prefix, event, value in parser:
        # print 'prefix:', prefix, 'event:', event, 'value:', value
        if prefix == 'results.item' and event == 'string':
            cnt = cnt + 1
            if cnt % 10000000 == 0:
                print "finished: " + str(cnt/1000000) + "M, ", "time: ", time.time() - t0, "sec"
            outFile.write(value.replace("\n", " ").replace("\r", "").replace("\x00", "").encode('utf-8'))
            outFile.write("\n")


def randomCoordinate(p_inFile, p_outFile):
    print "Converting [" + p_inFile + "] to [" + p_outFile + "] ... ..."
    csvIn = open(p_inFile, 'r')
    csvReader = csv.reader(csvIn, delimiter=',', quotechar='"')
    with open(p_outFile, 'w') as csvOut:
        csvWriter = csv.writer(csvOut, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        cnt = 0
        skip = 0
        t0 = time.time()
        for record in csvReader:
            cnt = cnt + 1
            record[2] = record[2].replace("\"", "")
            # print record
            if len(record) != 9:
                skip = skip + 1
                print 'skip ==>', record
                continue
            else:
                if record[3] == record[4]:
                    record[5] = float(record[5])
                    record[6] = float(record[6])
                    record[7] = float(record[7])
                    record[8] = float(record[8])
                    record[3] = record[5] + (record[7] - record[5]) * random.uniform(0, 1)
                    record[4] = record[6] + (record[8] - record[6]) * random.uniform(0, 1)
                # print record
                csvWriter.writerow(record)
            if cnt % 10000000 == 0:
                print "finished: " + str(cnt/1000000) + "M, ", "skipped: ", skip, "time: ", time.time() - t0, "sec"


file0 = '/Users/white/coord_tweets_max.csv'
file1 = '/Users/white/coord_tweets_max.csv.0'
file2 = '/users/white/coord_tweets_max.csv.00'

extractCSV(file0, file1)
randomCoordinate(file1, file2)
