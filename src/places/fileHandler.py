# coding: utf-8

import csv, json

def handleUploadedFile(uploadedFile, file_type):
    
    data = []
    
    if file_type == 'json':
        data = json.load(uploadedFile.file)
    
    elif file_type == 'csv':
        reader = csv.DictReader(uploadedFile, delimiter=',')
        for r in reader:
            data.append(r)
    
    return data
    