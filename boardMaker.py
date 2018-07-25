# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 12:25:25 2018

@author: James.Jacobs
"""
import csv
from const import const

class boardMaker:
    
    def saveBoard(newBoard, filename):
        #appends a new user to the list of users
        with open(filename, 'w') as f:
            writer = csv.writer(f, dialect='excel')
            for row in newBoard:
                writer.writerow(row)
                if const.LINUX == 0:
                    #delete line seems to be required in windows but not in linux!
                    boardMaker.deleteLastLine()  
                
    def loadBoard():
        #this gets the contents of the csv file into a list
        with open(const.BOARDNAME, newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
            board = list(filereader)
        return board
                    
    def deleteLastLine():
        #bodge to delete extra <CR> that appears when a problem is added
        readFile = open("users.csv")
        lines = readFile.readlines()
        readFile.close()
        w = open("users.csv",'w')
        w.writelines([item for item in lines[:-1]])
        w.close()                    
        