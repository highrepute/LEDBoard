# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 12:05:16 2018

@author: James.Jacobs
"""

import csv
from operator import itemgetter

class problemClass:#funcs that access information in the problem file
    NOHOLDSINDEX = 8
    HOLDSINDEX = 9
    STARTHOLDSINDEX = 4
    FINHOLDSINDEX = 6
    
    NAME = 0
    GRADE = 1
    STARS = 3
    DATE = 4
    
    problemList = []
    
    def readProblemFile():
        #this gets the contents of the csv file into a list
        with open('problems.csv', newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
            problems = list(filereader)
        return problems
        
    def getNameGradeStars(problems):    
        #extracts just the name, grade & stars
        problemList = [[i[0],i[1],i[2],i[3]] for i in problems]
        return problemList
    
    def getProblem(problems, problemNumber):
        #get the details of a problem
        problem = problems[problemNumber][:]
        return problem
   
    def getHolds(problems, problemNumber):
        #create an array of the holds on the problem
        problemHolds = []
        problemNoHolds = int(problems[problemNumber][problemClass.NOHOLDSINDEX])
        for i in range(problemClass.HOLDSINDEX,problemClass.HOLDSINDEX+problemNoHolds):
                problemHolds.append(int(problems[problemNumber][i]))
        return problemHolds
    
    def getStartHolds(problems, problemNumber):
        #array of the start holds
        startHolds = []
        for i in range(problemClass.STARTHOLDSINDEX,problemClass.STARTHOLDSINDEX+2):
                if (problems[problemNumber][i] != ''):
                    startHolds.append(int(problems[problemNumber][i]))
                else:
                    startHolds.append(-1)
        return startHolds
     
    def getFinHolds(problems, problemNumber):
        #array of the finish holds
        finHolds = []
        for i in range(problemClass.FINHOLDSINDEX,problemClass.FINHOLDSINDEX+2):
                if (problems[problemNumber][i] != ''):
                    finHolds.append(int(problems[problemNumber][i]))
                else:
                    finHolds.append(-1)
        return finHolds
    
    def deleteLastLine():
        #bodge to delete extra <CR> that appears when a problem is added
        readFile = open("problems.csv")
        lines = readFile.readlines()
        readFile.close()
        w = open("problems.csv",'w')
        w.writelines([item for item in lines[:-1]])
        w.close()
    
    def addNewProb(newProblem):
        #appends a new problem to the list of problems
        with open('problems.csv', 'a') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(newProblem)
        f.close()
        problemClass.deleteLastLine()
            
    def sortProblems(problems, sortBy):
        problems = sorted(problems, key=itemgetter(sortBy), reverse=True)
        return problems

#example of the functions in the FileIO class in use
#problems = problemClass.readProblemFile()
#print(problems)
#NameEtc = probFile.getNameGradeStars(problems)
#oneProblem = probFile.getProblem(problems,3)
#holdz = probFile.getHolds(problems,1)
#start = probFile.getStartHolds(problems,1)
#fin = probFile.getFinHolds(problems,2)
#sortedProblems = problemClass.sortProblems(problems, problemClass.GRADE)
#print(sortedProblems)

#print(fin)
            
#newProblem = ['new',  '7a',  '3',  '11/04/2018',    '1', '',   '9', '',   '3',     '1', '5', '9']
#print(newProblem)
#problemClass.addNewProb(newProblem)

