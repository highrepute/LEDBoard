# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 12:05:16 2018

@author: James.Jacobs
"""

import csv
from operator import itemgetter
from const import const

class problemClass:#funcs that access information in the problem file
    
    def readProblemFile():
        #this gets the contents of the csv file into a list  
        with open(const.PROBPATH, newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
            problems = list(filereader)
        return problems
    
    def saveProblemFile(problems):
        #appends a new problem to the list of problems
        with open(const.PROBPATH, 'w') as f:
            writer = csv.writer(f, dialect='excel')
            for row in problems:
                writer.writerow(row)
                if const.LINUX == 0:
                    #delete line seems to be required in windows but not in linux!
                    problemClass.deleteLastLine()

    def updateProblemFile(problem, row):
        #replaces an entry at 'row' in the problem file with 'problem'
        #row should take into account the header
        problems = problemClass.readProblemFile()
        problems[row] = problem
        problemClass.saveProblemFile(problems)
        
    def getNameGradeStars():  
        problems = problemClass.readProblemFile()
        problemList = []
        #extracts just the name, grade & stars
        problemList = [[i[const.PROBNAMECOL],i[const.GRADECOL],i[const.STARSCOL],i[const.DATECOL]] for i in problems]
        return problemList
    
    def getAllUsers():#returns all unique users
        problems = problemClass.readProblemFile()
        userList = []
        #extracts just the name, grade & stars
        userList = [i[const.USERCOL] for i in problems]
        del userList[0]
        return list(set(userList))
    
    def getUniqueTags():#returns all unique tags
        problems = problemClass.readProblemFile()
        #extracts just the tags
        tagList = [[i[const.TAGSCOL],i[const.TAGSCOL+1],i[const.TAGSCOL+2],i[const.TAGSCOL+3],i[const.TAGSCOL+4],i[const.TAGSCOL+5],i[const.TAGSCOL+6],i[const.TAGSCOL+7],i[const.TAGSCOL+8],i[const.TAGSCOL+9]] for i in problems]
        del tagList[0]
        #gets unique items from the list of tags
        newList = list(set(x for l in tagList for x in l))
        newList = list(filter(None, newList))
        return sorted(newList)
    
    def getUser(problemNumber):
        problems = problemClass.readProblemFile()
        user = problems[problemNumber][const.USERCOL]
        return user
    
    def getNotes(problemNumber):
        problems = problemClass.readProblemFile()
        notes = problems[problemNumber][const.NOTESCOL]
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
        problemNoHolds = int(problems[problemNumber][const.NOHOLDSINDEX])
        for i in range(const.HOLDSINDEX,const.HOLDSINDEX+problemNoHolds):
                problemHolds.append(int(problems[problemNumber][i]))
        return problemHolds
    
    def getStartHolds(problemNumber):
        problems = problemClass.readProblemFile()
        #array of the start holds
        startHolds = []
        for i in range(const.STARTHOLDSINDEX,const.STARTHOLDSINDEX+2):
                if (problems[problemNumber][i] != ''):
                    startHolds.append(int(problems[problemNumber][i]))
                else:
                    startHolds.append(-1)
        return startHolds
     
    def getFinHolds(problemNumber):
        problems = problemClass.readProblemFile()
        #array of the finish holds
        finHolds = []
        for i in range(const.FINHOLDSINDEX,const.FINHOLDSINDEX+2):
                if (problems[problemNumber][i] != ''):
                    finHolds.append(int(problems[problemNumber][i]))
                else:
                    finHolds.append(-1)
        return finHolds
    
    def deleteLastLine():
        #bodge to delete extra <CR> that appears when a problem is added
        readFile = open(const.PROBPATH)
        lines = readFile.readlines()
        readFile.close()
        w = open(const.PROBPATH,'w')
        w.writelines([item for item in lines[:-1]])
        w.close()
    
    def addNewProb(newProblem):
        #appends a new problem to the list of problems
        with open(const.PROBPATH, 'a') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(newProblem)
        f.close()
        if (const.LINUX == 0):
            problemClass.deleteLastLine()
            
    def addNewTag(problemNumber, newTag):#adds a new tag if space
        problems = problemClass.readProblemFile()#get problem database
        tags = problems[problemNumber][const.TAGSCOL:const.TAGSCOL+10]
        if '' in tags:#check there is a blank entry
            if newTag in tags: #check if tag already exists
                return -1 #tag alreayd present
            else:
                #get indices of first blank entry
                i = 0
                for tag in tags:
                    if tag == '':
                        index = i
                        break 
                    i = i + 1
                #add newTag to problem
                problem = problems[problemNumber]
                problem[const.TAGSCOL+index] = newTag
                #save to problem file
                problemClass.updateProblemFile(problem, problemNumber)
                return 0
        else:
            return -2 #can't add tag
            
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
        matches = []
        #get list of problem grades
        gradesListStr = problemClass.column(problems,const.GRADECOL)
        del gradesListStr[0]
        #convert grades list to integer list
        gradesList = [int(i) for i in gradesListStr]
        for grade in range(start,end+1):#for each grade input to function
            i = 1
            for gradeInList in gradesList:
                if gradeInList == grade:#if grade matches
                    matches.append(i)
                i = i + 1
        fitleredProblems = []
        fitleredProblems.append(problems[0][0:17])#get header
        for match in matches:
            fitleredProblems.append(problems[match][0:17])#get problems that match
        return fitleredProblems
    
    def getUserFilteredProblems(problems,user):
        header = problems[0]
        del problems[0]
        matches = []
        matches += (problemClass.find(user,problemClass.column(problems,const.USERCOL)))
        matches = problemClass.column(matches,0)
        matches.sort()
        fitleredProblems = [header]
        for match in matches:
            fitleredProblems.append(problems[match][0:17])
        return fitleredProblems 

    def getStarFilteredProblems(problems,stars):
        stars = problemClass.find(stars,const.STARS)[0][0]#return index of first match
        header = problems[0]
        del problems[0]
        matches = []
        matches += problemClass.find(str(stars),problemClass.column(problems,const.STARSCOL))
        matches = problemClass.column(matches,0)
        matches.sort()
        fitleredProblems = [header]
        for match in matches:
            fitleredProblems.append(problems[match][0:17])
        return fitleredProblems    
      
    def getTagsFilteredProblems(problems,tags):
        header = problems[0]
        del problems[0]
        matches = []
        for tag in tags:#go through array of tags
            for i in range(10):#for each tag column in database find matching tag
                matches += (problemClass.find(str(tag),problemClass.column(problems,const.TAGSCOL+i)))
        matches = problemClass.column(matches,0)
        matches = list(set(matches))
        matches.sort()
        #create filtered problem list for output
        fitleredProblems = [header[0:5]]
        for match in matches:
            fitleredProblems.append(problems[match][0:5])
        return fitleredProblems    

#example of the functions in the FileIO class in use
const.initConfigVariables()
problems = problemClass.readProblemFile()
#problems = problemClass.getGradeFilteredProblems(5,8)
#print(problems)
problems = problemClass.getTagsFilteredProblems(problems,["crimpy","pinchy"])
print(problems)
#print(problemClass.addNewTag(3, 'pockets'))
#print(problemClass.getUniqueTags())
#problems = problemClass.getStarFilteredProblems(problems, '**')#
#problems = problemClass.getUserFilteredProblems(problems,"James")
#print(problems)

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
            
#newProblem = ['new',  '3',  '3',  '2018-08-21', 'James', 'comments go here',  'circles',  '1', '',   '9', '',   '3',     '1', '5', '9']
#print(newProblem)
#problemClass.updateProblemFile(newProblem,2)
#print(problemClass.getAllUsers())
#oneProblem = problemClass.getProblem(6)
#print(oneProblem)