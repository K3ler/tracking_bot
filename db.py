
import json
import os
import csv

from datetime import datetime


class DB(object):
    def __init__(self, id):
        self.id = id
        self.data = dict({"history": []})
        self.filePath = "{0}/data/id{1}.json".format(
            os.path.dirname(os.path.abspath(__file__)), id)

        self.csvPath = "{0}/csv/id{1}.csv".format(
            os.path.dirname(os.path.abspath(__file__)), id)

        self.loadFile()

    def loadFile(self):
        if not os.path.isdir('data'):
            os.mkdir('data')

        if os.path.isfile(self.filePath):
           with open(self.filePath) as file:
               self.data = json.load(file)
        else:
           f = open(self.filePath, "w+")
           json.dump(self.data, f)
           f.close()

    def saveMessage(self, data):

        self.data["history"] += [data]

        with open(self.filePath, "w+") as file:
            json.dump(self.data, file)

    def save(self):
        with open(self.filePath, "w+") as file:
            json.dump(self.data, file)

    def saveToCSV(self):
        if not os.path.isdir('csv'):
            os.mkdir('csv')

        f = csv.writer(open(self.csvPath, "w+"))
        f.writerow(['Что делали?', 'Время'])

        for item in self.data["history"]:
            f.writerow([item['message'], datetime.fromtimestamp(item["date"])])

        return self.csvPath

