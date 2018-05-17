# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 12:05:16 2018

@author: James.Jacobs
"""

import csv
from operator import itemgetter
from const import const

NOHOLDSINDEX = 10
HOLDSINDEX = 11
STARTHOLDSINDEX = 6
FINHOLDSINDEX = 8

NAME = 0
GRADE = 1
STARS = 2
DATE = 3
USER = 4
NOTES = 5

class problemClass:#funcs that access information in the problem file
    
    def readProblemFile():
        #this gets the contents of the csv file into a list
        with open('problems.csv', newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
            problems = list(filereader)
        return problems
    
    def saveProblemFile(problems):
        #appends a new user to the list of users
        with open('problems.csv', 'w') as f:
            writer = csv.writer(f, dialect='excel')
            for row in problems:
                writer.writerow(row)
                if const.LINUX == 0:
                    #delete line seems to be required in windows but not in linux!
                    problemClass.deleteLastLine()    
        
    def getNameGradeStars():  
        problems = problemClass.readProblemFile()
        problemList = []
        #extracts just the name, grade & stars
        problemList = [[i[NAME],i[GRADE],i[STARS],i[DATE]] for i in problems]
        return problemList
    
    def getUser(problemNumber):
        problems = problemClass.readProblemFile()
        user = problems[problemNumber][USER]
        return user
    
    def getNotes(problemNumber):
        problems = problemClass.readProblemFile()
        notes = problems[problemNumber][NOTES]
        return notes
    
    def getProblem(problemNumber):
        problems = problemClass.readProblemFile()
        #get the details of a problem
        problem = problems[problemNumber][:]
        return problem
   
    def getHolds(problemNumber):
        problems = problemClass.readProblemFile()
        #create an array of the holds on the problem
        problemHolds = []
        problemNoHolds = int(problems[problemNumber][NOHOLDSINDEX])
        for i in range(HOLDSINDEX,HOLDSINDEX+problemNoHolds):
                problemHolds.append(int(problems[problemNumber][i]))
        return problemHolds
    
    def getStartHolds(problemNumber):
        problems = problemClass.readProblemFile()
        #array of the start holds
        startHolds = []
        for i in range(STARTHOLDSINDEX,STARTHOLDSINDEX+2):
                if (problems[problemNumber][i] != ''):
                    startHolds.append(int(problems[problemNumber][i]))
                else:
                    startHolds.append(-1)
        return startHolds
     
    def getFinHolds(problemNumber):
        problems = problemClass.readProblemFile()
        #array of the finish holds
        finHolds = []
        for i in range(FINHOLDSINDEX,FINHOLDSINDEX+2):
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
        if (const.LINUX == 0):
            problemClass.deleteLastLine()
            
    def sortProblems(sortBy):
        problems = problemClass.readProblemFile()
        problems = sorted(problems, key=itemgetter(sortBy), reverse=True)
        return problems
    
    #returns the indices of all items matching c in ml
    def find(c,ml):
        indices = [(i, item.index(c))
        for i, item in enumerate(ml)
        if c in item]
        return indices   
    
    #returns a column from a list - list must be a matrix in dimensions
    def column(matrix, i):
        return [row[i] for row in matrix]    
    
    #returns list of all problems logged by user
    def getGradeFilteredProblems(start, end):
        problems = problemClass.readProblemFile()
        #print(len(problems))
        matches = []
        for grade in const.GRADES[start:end+1]:
            matches += (problemClass.find(grade,problems))
        matches = problemClass.column(matches,0)
        matches.sort()
        fitleredProblems = []
        fitleredProblems.append(problems[0][0:4])
        for match in matches:
            fitleredProblems.append(problems[match][0:4])
        return fitleredProblems
        

#example of the functions in the FileIO class in use
#print(problemClass.getGradeFilteredProblems(0,6))
#problems = problemClass.readProblemFile()
#print(problems)
#print(problemClass.getNotes(problems,1))
#print(problemClass.getUser(problems,1))
#print(problemClass.getNameGradeStars())
#NameEtc = probFile.getNameGradeStars(problems)
#oneProblem = probFile.getProblem(problems,3)
#holdz = probFile.getHolds(problems,1)
#start = probFile.getStartHolds(problems,1)
#fin = probFile.getFinHolds(problems,2)
#sortedProblems = problemClass.sortProblems(problems, problemClass.GRADE)
#print(sortedProblems)

#print(fin)
            
#newProblem = ['new',  '7a',  '3',  '11/04/2018', 'James', 'comments go here',    '1', '',   '9', '',   '3',     '1', '5', '9']
#print(newProblem)
#problemClass.addNewProb(newProblem)

