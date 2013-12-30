# coding: utf-8

import csv, json

def handleUploadedFile(uploadedFile):
    
    reader = csv.DictReader(uploadedFile, delimiter=',')
    data = []
    for r in reader:
        data.append(r)
    return data
    