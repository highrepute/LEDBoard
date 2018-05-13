# -*- coding: utf-8 -*-
"""
Created on Thu May  3 08:07:40 2018

@author: James.Jacobs
"""
LINUX = 1

import csv

class logClass:
    
    def readLogFile():
        #this gets the contents of the csv file into a list
        with open('logs.csv', newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
            log = list(filereader)
        return log
    
    #returns the indices of all matching items
    def find(c,ml):
        indices = [(i, item.index(c))
        for i, item in enumerate(ml)
        if c in item]
        return indices
    
    def deleteLastLine():
        #bodge to delete extra <CR> that appears when a problem is added
        readFile = open("logs.csv")
        lines = readFile.readlines()
        readFile.close()
        w = open("logs.csv",'w')
        w.writelines([item for item in lines[:-1]])
        w.close()    
    
    def logProblem(newLogProb):
        #appends a new user to the list of users
        with open('logs.csv', 'a') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(newLogProb)
        f.close()
        if LINUX == 0:
            #delete line seems to be required in windows but not in linux!
            logClass.deleteLastLine()
       
    #returns a list of the star votes of all logs of "problem"
    def getStarVotes(problem):
        starVotes = []
        log = logClass.readLogFile()
        matches = logClass.find(problem,log)
        for item in matches:
            starVotes.append(log[item[0]][3])
        return starVotes
    
    #returns a list of the grade votes of all logs of "problem"    
    def getGradeVotes(problem):
        gradeVotes = []
        log = logClass.readLogFile()
        matches = logClass.find(problem,log)
        for item in matches:
            gradeVotes.append(log[item[0]][2])
        return gradeVotes
        
    #returns list of all problems logged by user
    def getUserLogbook(user):
        log = logClass.readLogFile()
        matches = logClass.find(user,log)
        userLogbook = [log[0][1:7]]
        for row,zero in matches:
            userLogbook.append(log[row][1:7])
        return userLogbook
    
    #returns list of all ascents logged of a problem
    #ordered by date, most recent first
    def getProblemAscents(problem):
        log = logClass.readLogFile()
        matches = logClass.find(problem,log)
        problemAscents = []
        ascent = []
        for row,zero in matches:
            ascent = log[row]
            del ascent[1]
            problemAscents.append(ascent)
        
        return list(reversed(problemAscents))
        
#logClass.getUserProblems("James")
#gradeVotes = logClass.getGradeVotes("Pinch Test")
#print(gradeVotes)
#print(gradeVotes.count('6a'))
#print(gradeVotes.count('6c'))
#newLog = ['Toby','Zeke the Fake','6c','***','2018-05-02','This problem is aweseome!','Flash']
#logClass.logProblem(newLog)
#print(logClass.getUserLogbook("James"))
#print(logClass.getProblemAscents("Pinch Test"))
#print(logClass.getProblemAscents("Zeke the Fake"))
