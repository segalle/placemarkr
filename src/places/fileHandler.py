import csv

def handleUploadedFile(uploadedFile):
    content = uploadedFile.read()
    print content
    
    #with open(uploadedFile, 'rb') as csvfile:
    #    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    #    for row in spamreader:
    #        print ', '.join(row)
