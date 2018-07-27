# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 12:25:25 2018

@author: James.Jacobs
"""
import csv
from const import const

class boardMaker:
    
    def saveBoard(newBoard, imagePath):
        #appends a new user to the list of users
        with open(const.BOARDNAME, 'w') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow([imagePath])
            for row in newBoard:
                writer.writerow(row)
                if const.LINUX == 0:
                    #delete line seems to be required in windows but not in linux!
                    boardMaker.deleteLastLine()  
                    
    def loadBoard():
        #this gets the contents of the csv file into a list
        try:
            with open(const.BOARDNAME, newline='') as csvfile:
                filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
                board = list(filereader)
            del board[0]
            return board
        except:
            return None
    
    def getBoardImagePath():
        #this gets the contents of the csv file into a list
        with open(const.BOARDNAME, newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
            board = list(filereader)
        return board[0][0]        
                    
    def deleteLastLine():
        #bodge to delete extra <CR> that appears when a problem is added
        readFile = open(const.BOARDNAME)
        lines = readFile.readlines()
        readFile.close()
        w = open(const.BOARDNAME,'w')
        w.writelines([item for item in lines[:-1]])
        w.close()                    
        
#const.initConfigVariables()
#board = [[1,1,1],[2,2,2],[3,3,3]]
#filename = "testboard.brd"
#imagepath = "image.jpg"
#boardMaker.saveBoard(board, imagepath)
#print(boardMaker.getBoardImagePath())
#print(boardMaker.loadBoard())