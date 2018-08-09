# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 12:25:25 2018

@author: James.Jacobs
"""
import csv
from const import const
import ast

class boardMaker:
    
    def saveBoard(boardPath, newBoard, imagePath):
        #appends a new user to the list of users
        
        #we want to keep the mirror table so extract it before writing the file
        mirrorTable = boardMaker.getBoardMirrorTable(boardPath)
        #print(mirrorTable)
        #print(mirrorTable[0])
        with open(boardPath, 'w') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow([imagePath])
            writer.writerow('')#reserve for mirror table
            for row in newBoard:
                writer.writerow(row)
                if const.LINUX == 0:
                    #delete line seems to be required in windows but not in linux!
                    boardMaker.deleteLastLine(boardPath)
        boardMaker.setBoardMirrorTable(boardPath, mirrorTable)
                    
    def loadBoard(boardPath):
        #this gets the contents of the csv file into a list
        try:
            with open(boardPath, newline='') as csvfile:
                filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
                board = list(filereader)
            #print(board)
            del board[1]#mirror table
            del board[0]#image path
            return board
        except:
            return None
    
    def getBoardImagePath(boardPath):
        #this gets board image path from the first line of the brd file
        with open(boardPath, newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
            board = list(filereader)
        return board[0][0]     
    
    def getBoardMirrorTable(boardPath):
        #this gets board mirror table second line of the brd file
        with open(boardPath, newline='') as fh:
            for i, line in enumerate(fh):
                if i == 1:
                    listobj = ast.literal_eval(line)
                    break
        return listobj
    
    def setBoardMirrorTable(boardPath, mirrorTable):
        #this gets board image path from the first line of the brd file
        try:
            with open(boardPath, 'r') as file:
                data = file.readlines()
        except:#no file yet
            data = ['\n','']#file doesn't exist create something
        data[1] = str(mirrorTable) + "\n"  
        with open(boardPath, 'w') as file:
            file.writelines(data)

    def saveBoardAs(boardPath, saveAsPath):
        #basically copies a file to a new file
        with open(boardPath, 'r') as file:
            data = file.readlines()
        with open(saveAsPath, 'w') as file:
            file.writelines(data)            
                    
    def deleteLastLine(filePath):
        #bodge to delete extra <CR> that appears when a problem is added
        readFile = open(filePath)
        lines = readFile.readlines()
        readFile.close()
        w = open(filePath,'w')
        w.writelines([item for item in lines[:-1]])
        w.close()                    
        
#const.initConfigVariables()
#board = [[1,1,1,'a'],[2,2,2,'b'],[3,3,3,'c']]
#boardPath = "test2.brd"
#imagepath = "image.jpg"

#print(boardMaker.getBoardImagePath())
#print(boardMaker.loadBoard("test2.brd"))
#mirror = boardMaker.getBoardMirrorTable("testboard.brd")
#mirror = [[1,11],[2,21],[6,31]]
#print(mirror[0])
#boardMaker.saveBoard(boardPath, board, imagepath)
#boardMaker.setBoardMirrorTable("testboard.brd", mirror)
#boardMaker.loadBoard("test1.brd")
