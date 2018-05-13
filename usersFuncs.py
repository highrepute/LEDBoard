# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 12:05:16 2018

@author: James.Jacobs
"""
LINUX = 1

import csv
#from operator import itemgetter

class userClass:#funcs that access information in the users file 
    
    def readUsersFile():
        #this gets the contents of the csv file into a list
        with open('users.csv', newline='') as csvfile:
            filereader = csv.reader(csvfile, delimiter=',', quotechar='|')
            users = list(filereader)
        return users
        
    def getUserNames(users):    
        #extracts just the name
        userList = [[i[0]] for i in users]
        return userList
    
    def checkPassword(users, username, password):
        #search users to match the username
        userRow = userClass.find(users,username)
        if (userRow[0] == -1):
            #uknown userName
            return -2
        else:
            #check the password is correct
            if (users[userRow[0]][1] == password):
                #return a login success
                return 0
            else:
                #invalid password
                return -1
    
    def deleteLastLine():
        #bodge to delete extra <CR> that appears when a problem is added
        readFile = open("users.csv")
        lines = readFile.readlines()
        readFile.close()
        w = open("users.csv",'w')
        w.writelines([item for item in lines[:-1]])
        w.close()
        
    def find(l, elem):
        for row, i in enumerate(l):
            try:
                #print(i)
                column = i.index(elem)
            except ValueError:
                continue
            return row, column
        return [-1,-1]        
    
    def addNewUser(newUser):
        #appends a new user to the list of users
        with open('users.csv', 'a') as f:
            writer = csv.writer(f, dialect='excel')
            writer.writerow(newUser)
        f.close()
        if LINUX == 0:
            #delete line seems to be required in windows but not in linux!
            userClass.deleteLastLine()
            
#example of the functions in the users class in use
#newUser = ['Mark','Crankin','2018-04-02']
#userClass.addNewUsers(newUser)
#usersDB = userClass.readUsersFile()
#print(usersDB)
#login = userClass.checkPassword(usersDB, 'EllieP', 'Highball_Pygall')
#print(login)
