import csv
import os
from const import const

class projectClass:

    def readProjectFile():
        try:
            with open(const.PROJECTSPATH, newline='') as csvfile:
                filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
                projects = list(filereader)
            return projects
        except FileNotFoundError:
            return [['Username', 'ProblemName']]

    def saveProjectFile(projects):
        with open(const.PROJECTSPATH, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in projects:
                writer.writerow(row)

    def addProject(username, problemName):
        projects = projectClass.readProjectFile()
        for row in projects[1:]:
            if row[0] == username and row[1] == problemName:
                return -1  # already exists
        projects.append([username, problemName])
        projectClass.saveProjectFile(projects)
        return 0

    def removeProject(username, problemName):
        projects = projectClass.readProjectFile()
        projects = [projects[0]] + [r for r in projects[1:]
                    if not (r[0] == username and r[1] == problemName)]
        projectClass.saveProjectFile(projects)

    def getUserProjects(username):
        projects = projectClass.readProjectFile()
        return [r[1] for r in projects[1:] if r[0] == username]

    def isProject(username, problemName):
        projects = projectClass.readProjectFile()
        return any(r[0] == username and r[1] == problemName for r in projects[1:])
