import sys
from PyQt5 import QtWidgets, uic, QtCore#, QtGui
from PyQt5.QtCore import QTimer
#import time
import re
import datetime
import time

from collections import Counter

from problemFuncs import problemClass
from mirror import mirror
from usersFuncs import userClass
from logFuncs import logClass
from const import const

from qrangeslider import QRangeSlider

if const.LINUX == 1:
    from neopixel import *

qtCreatorFile = "DiscoBoard.ui" # Enter file here.
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):        
    def __init__(self):
        global newStartHolds
        global newProbHolds
        global newProbCounter
        global mirrorFlag
        global undoCounter
        global usersLoggedIn
        global showSequenceFlag
        global showSequenceCounter
        global startHoldsQ
        global probHoldsQ
        global finHoldsQ
        global shownSequenceCount
        global showTwoProbsFlag
        global startHoldsS2P
        global probHoldsS2P
        global finHoldsS2P
        global S2PStartMatches        
        global S2PProbMatches
        global S2PFinMatches
        global toggleLEDFlag
        global startHolds
        global probHolds
        global finHolds        
        global S2PProbName
        global probName
        global sliderFlag
        global adminFlag
        global userFilter
        
        #global prevPb
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        #LED Board widgets
        self.setupUi(self)
        
        #init slider
        self.slider = QRangeSlider(self)
        self.slider.setMax(8)
        self.slider.setMin(0)
        self.slider.setRange(0,7)
        self.QVBLayoutSlider.addWidget(self.slider)
        self.slider.endValueChanged.connect(self.sliderChange)
        self.slider.startValueChanged.connect(self.sliderChange)    
        
        #Connect buttons to functions
        self.pbTestLEDs.clicked.connect(self.testLEDs)        
        #self.tblProblems.clicked.connect(self.lightProblem)
        self.tblProblems.selectionModel().selectionChanged.connect(self.lightProblem)
        self.pbMirror.clicked.connect(self.mirrorProb)
        self.pbLogin.clicked.connect(self.login)
        self.pbLogout.clicked.connect(self.logout)
        self.lbUsers.clicked.connect(self.updateLogLabel)
        self.pbLogProblem.clicked.connect(self.logProblem)
        self.pbSequence.clicked.connect(self.showSequence)
        self.pbShowTwoProbs.clicked.connect(self.showTwoProbs)
        
        #new problem widgiets
        self.pbDiscard.clicked.connect(self.resetAddProblemTab)
        self.pbSave.clicked.connect(self.saveNewProb)
        self.pbUndo.clicked.connect(self.undo)
        
        #Add user tab
        self.pbAddNewUsers.clicked.connect(self.addNewUser)
        
        #admin tab
        self.pbAdminLogin.clicked.connect(self.adminLogin)
        self.pbEditUsers.clicked.connect(self.editUsers)
        self.pbEditLogs.clicked.connect(self.editLogs)
        self.pbEditProblems.clicked.connect(self.editProblems)
        self.pbEditSave.clicked.connect(self.editSave)
        self.tabWidget.currentChanged.connect(self.adminLogout)
        self.pbDeleteRow.clicked.connect(self.deleteRow)
        
        #filter tab
        #self.tabWidget.currentChanged.connect(self.populateFilterTab)
        self.pbFilterByUser.clicked.connect(self.filterByUser)
        self.lbUserFilter.selectionModel().selectionChanged.connect(self.filterUserChange)
        
        #link hold buttons to the changeButtonColour function
        for num in range (1,const.TOTAL_LED_COUNT+1):
            label = getattr(self, 'pb{}'.format(num))
            label.clicked.connect(self.addHoldtoProb)
            #make them transparent???
            label.setStyleSheet("background-color: rgba(240, 240, 240, 75%)")
            
        #init new problem globals
        newProbCounter = 0
        newStartHolds = []
        newProbHolds = []
        mirrorFlag = 0
        undoCounter = 0
        usersLoggedIn = []
        showSequenceFlag = 0
        showSequenceCounter = 0
        shownSequenceCount = 0
        showTwoProbsFlag = 0
        startHoldsS2P = []
        probHoldsS2P = []
        finHoldsS2P = []
        toggleLEDFlag = 0
        startHolds = []
        probHolds = []
        finHolds = []
        S2PStartMatches = []    
        S2PProbMatches = []
        S2PFinMatches = []
        S2PProbName = ""
        probName = ""
        sliderFlag = 0
        adminFlag = 0#0-logged out, 1-logged in, 2-editUsers, 3-editlogs, 4-editproblems
        userFilter = ""            
                
        self.populateProblemTable()
        self.tabWidget.setCurrentIndex(0)
        
        self.populateFilterTab()
        
        #start timer that logs out inactive users
        self.start_timer()
        
        #self.showFullScreen()
        #self.LEDBoard.setStyleSheet("background-color: rgba(255, 0, 0, 0%)")
        
        #default message
        self.lblInfo.setText(const.DEFAULTMSG)
        
        #make tables read only
        self.tblProblems.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblAscents.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblLogbook.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
    def filterUserChange(self):
        global userFilter 
        if userFilter != "":
            rowN = self.lbUserFilter.selectedIndexes()[0].row()
            user = self.lbUserFilter.item(rowN).text()
            userFilter = user
            text = "Filtering by user - " + user
            self.lblUserFilter.setText(text)
            self.lblInfo.setText(text)
            self.populateProblemTable()
        
    def filterByUser(self):
        global userFilter
        print("fitlerbyuser")
        if userFilter == "":
            try:
                rowN = self.lbUserFilter.selectedIndexes()[0].row()
                user = self.lbUserFilter.item(rowN).text()
                userFilter = user
                self.pbFilterByUser.setStyleSheet("background-color: rgba(0, 128, 0 100%)")#green 
                text = "Filtering by user - " + user
                self.lblUserFilter.setText(text)
                self.lblInfo.setText(text)                 
            except:
                userFilter = ""
                self.pbFilterByUser.setStyleSheet("background-color: rgba(240, 240, 240 100%)")#gray
                self.lblUserFilter.setText("Select a user before filtering")
                self.lblInfo.setText("Not filtering by user")
        else:
            self.pbFilterByUser.setStyleSheet("background-color: rgba(240, 240, 240 100%)")#gray
            self.lblUserFilter.setText("Not filtering by user")
            self.lblInfo.setText("Not filtering by user")
            userFilter = ""
        self.populateProblemTable()
        print(userFilter)
        
    def populateFilterTab(self):
        try:
            rowN = self.lbUserFilter.selectedIndexes()[0].row()
            users = userClass.getUserNames()
            self.lbUserFilter.clear()
            if (len(users) > 0):
                self.lbUserFilter.addItems(users)
            self.lbUserFilter.setCurrentRow(rowN)
        except:
            users = userClass.getUserNames()
            self.lbUserFilter.clear()
            if (len(users) > 0):
                self.lbUserFilter.addItems(users)            
        
    def deleteRow(self):
        model = self.tblEdit.model()
        indices = [self.tblEdit.selectedIndexes()[0]]
        print("delete", indices)
        for index in sorted(indices):
            model.removeRow(index.row())
        
    def editSave(self):
        global adminFlag
        
        if adminFlag > 1:
            model = self.tblEdit.model()
            
            #data=[]
            #need to add headers to the data - get from original data
            if adminFlag == 2:
                data = [userClass.readUsersFile()[0]]
            elif adminFlag == 3:
                data = [logClass.readLogFile()[0]]
            elif adminFlag == 4:
                data = [problemClass.readProblemFile()[0]]
            #get the data from the table
            for row in range(model.rowCount()-1):
              data.append([])
              for column in range(model.columnCount()):
                index = model.index(row+1, column)
                data[row+1].append(str(model.data(index)))  
            #save the data to the correct file
            if adminFlag == 2:
                userClass.saveUsersFile(data)
            elif adminFlag == 3:
                logClass.saveLogFile(data)
            elif adminFlag == 4:
                problemClass.saveProblemFile(data)
                
    def editProblems(self):
        global adminFlag
        
        if adminFlag > 0:
            adminFlag = 4
            problems = problemClass.readProblemFile()
            self.populateEditTable(problems)
            self.lblAdminState.setText("Loaded problems database")    
    
    def editLogs(self):
        global adminFlag
        
        if adminFlag > 0:
            adminFlag = 3
            log = logClass.readLogFile()
            self.populateEditTable(log)
            self.lblAdminState.setText("Loaded logbooks")
    
    def editUsers(self):
        global adminFlag
        
        if adminFlag > 0:
            adminFlag = 2
            users = userClass.readUsersFile()
            self.populateEditTable(users)
            self.lblAdminState.setText("Loaded users database")
            
    def populateEditTable(self, data):
        self.tblEdit.setRowCount(len(data)-1)
        maxCols = len(max(data,key=len))
        self.tblEdit.setColumnCount(maxCols)
        self.tblEdit.horizontalHeader().setVisible(True)
        self.tblEdit.setHorizontalHeaderLabels(data[0])
        for i in range(1,len(data),1):
            for j in range(0,maxCols,1):
                try:
                    item = QtWidgets.QTableWidgetItem(data[i][j])
                    self.tblEdit.setItem(i-1,j, item)
                except:
                    self.tblEdit.setItem(i-1,j, QtWidgets.QTableWidgetItem(''))
                    
        #set column widths - difficult to do well here but doesn't matter so much
        #header = self.tblEdit.horizontalHeader()                     
        #if maxCols > 0:
        #    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        #if maxCols > 4:
        #    header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
    
    def adminLogout(self):
        global adminFlag
        adminFlag = 0
        self.lblAdminState.setText("Logged Out")
        self.tblEdit.clear()
    
    def adminLogin(self):
        global adminFlag
        
        if adminFlag == 0:
            if self.leAdminPassword.text() == "admin":#CHANGE THIS!!!
                adminFlag = 1
                self.leAdminPassword.clear()
                self.lblInfo.setText("Logged In!\nLogged In. You may now edit the databassed. Be careful!")
                self.lblAdminState.setText("Logged In")
            else:
                self.lblInfo.setText("Oh no!\nI'm sorry your password is incorrect")
    
    def sliderChange(self):
        global sliderFlag
        sliderFlag = 1
        
        start = const.GRADES[self.slider.getRange()[0]]
        end = const.GRADES[self.slider.getRange()[1]-1]
        self.lblMax.setText(str(end))
        self.lblMin.setText(str(start))

    def viewLogbook(self):
        self.tabWidget.setCurrentIndex(3)
        self.populateLogbook()
        
    def showTwoProbs(self):
        global showTwoProbsFlag
        global startHolds
        global probHolds
        global finHolds
        global startHoldsS2P
        global probHoldsS2P
        global finHoldsS2P 
        global S2PStartMatches        
        global S2PProbMatches
        global S2PFinMatches
        print("show two probs")
        
        if showTwoProbsFlag == 0:
            showTwoProbsFlag = 1
            text = "Showing two problems\n" + probName + "\nand\n" + S2PProbName
            self.lblInfo.setText(text)
            #change button colour to show "two prob" mode is active
            self.pbShowTwoProbs.setStyleSheet("background-color: rgba(0, 128, 0 100%)")#green
            #get holds for both problems
            MyApp.lightTwoLEDs(startHolds, probHolds, finHolds, startHoldsS2P, probHoldsS2P, finHoldsS2P)
            #figure out any holds that are on both problems
            S2PStartMatches = list(set(startHolds) & set(startHoldsS2P))     
            S2PProbMatches = list(set(probHolds) & set(probHoldsS2P))  
            S2PFinMatches = list(set(finHolds) & set(finHoldsS2P))  
        else:
            #turn off show two problem mode
            showTwoProbsFlag = 0
            self.pbShowTwoProbs.setStyleSheet("background-color: rgba(240, 240, 240, 100%)")
            self.lightProblem()
        
    def showSequence(self):
        global mirrorFlag
        global showSequenceFlag
        global showSequenceCounter
        global startHolds
        global probHolds
        global finHolds   
        global shownSequenceCount
        global S2PProbName
        
        if showTwoProbsFlag == 1:
            self.showTwoProbs()
            
        showSequenceFlag = 1 
        showSequenceCounter = 0
        shownSequenceCount = 0
                   
    def logProblem(self):      
        if (self.tblProblems.selectedIndexes() != [])&(self.lbUsers.selectedIndexes() != []):
            #gather data for new log entry
            rowN = self.lbUsers.selectedIndexes()[0].row()
            user = self.lbUsers.item(rowN).text()
            #as user is active, reset login time-in
            self.resetUserTimeIn(user)
            rowN = self.tblProblems.selectedIndexes()[0].row()
            problem = self.tblProblems.item(rowN,0).text()
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            comments = self.tbLogComments.toPlainText().replace('\n', ' ')
            comments = comments.replace(',', '-')
            grade = self.cbGrade.currentText()
            stars = self.cbStars.currentText()
            style = self.cbStyle.currentText()
            #create new log entry
            logProblem = [user,problem,grade,stars,date,comments,style]
            print(logProblem)
            logClass.logProblem(logProblem)
            #clear text
            self.tbLogComments.clear()
            self.cbStyle.setCurrentIndex(0)
            rowProb = self.getRowProb()
            self.updateLogProblemDropdowns(rowProb)
            text = problem + " logged to " + user + "'s logbook"
            self.lblInfo.setText(text)
        elif (self.tblProblems.selectedIndexes() == []):
            self.lblInfo.setText("Oh no!\nPlease select a problem")
        else:
            self.lblInfo.setText("Oh no!\nPlease select a user, you may need to login")
        
    def updateLogLabel(self):        
        rowN = self.tblProblems.selectedIndexes()
        print(rowN)
        if (rowN != []):#if a problem selected
            rowN = rowN[0].row()
            problem = self.tblProblems.item(rowN,0).text()
            self.lblLogProb1.setText("Log")
            self.lblLogProb2.setText(problem)
        if (len(usersLoggedIn) > 0): #if a user logged in
            self.lblLogProb3.setText("as")
            try:
                rowN = self.lbUsers.selectedIndexes()[0].row()
                user = self.lbUsers.item(rowN).text()
            except:
                user = ''
            self.lblLogProb4.setText(user)
            string = "Add problem as "
            string += user
            self.lblAddProbUser.setText(string)
        else:
            self.lblLogProb3.setText("Select a - ")
            self.lblLogProb4.setText("user")
            self.lblAddProbUser.setText("Select a user")
        self.populateLogbook()    
        
    def addNewUser(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        username = self.leAddUsername.text()
        password = self.leAddPassword.text()
        if (len(username) < 3):
            QtWidgets.QMessageBox.warning(self, "Easy now!", "Username must be at least 3 characters")
        elif (len(password) < 3):
            QtWidgets.QMessageBox.warning(self, "Easy now!", "Password must be at least 3 characters")
        else:
            text = "New user " + username + " added, you may now login"
            QtWidgets.QMessageBox.warning(self, "Easy now!", text)
            self.lblInfo.setText(text)
            userClass.addNewUser([username, password,date])
            self.populateFilterTab()
              
    def start_timer(self):
        #timer with 1 minute timeout
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.autoLogout())
        self.timer.start(60000)#change to 1 minute = 60000
        #timer with 250ms timeout
        self.timerQuick = QTimer()
        self.timerQuick.timeout.connect(lambda: self.timerQuickISR())
        self.timerQuick.start(400)     
        
    #log a user out
    def autoLogout(self):
        global usersLoggedIn
        print("auto logout")
        for user,timeIn in usersLoggedIn:
            #if time since logged-in is 30mins (1800sec)
            print(time.time() - timeIn)
            if ((time.time() - timeIn) > 1800):
                #log out that user
                index = MyApp.find(usersLoggedIn,user)[0]
                del usersLoggedIn[index]
                self.lbUsers.clear()
                if (len(usersLoggedIn) > 0):
                    self.lbUsers.addItems(MyApp.column(usersLoggedIn,0))
                self.updateLogLabel()
                text = user + " automatically logged out"
                self.lblInfo.setText(text)
                    
    def timerQuickISR(self):
        global showSequenceFlag
        global showSequenceCounter
        global shownSequenceCount
        global S2PStartMatches        
        global S2PProbMatches
        global S2PFinMatches 
        global sliderFlag
        #print("quick timer", showSequenceFlag, showSequenceCounter, shownSequenceCount)
        if (showSequenceFlag == 1):
            #get index of selected problem in table
            items = self.tblProblems.selectedIndexes()[0]
            #get name of problem
            probName = self.tblProblems.item((items.row()),0).text()
            text = "Showing sequence of " + probName + "\n" + str(10 - shownSequenceCount)
            self.lblInfo.setText(text)
            if (shownSequenceCount < 10):
                showSequenceCounter = showSequenceCounter + 1
                if const.LINUX == 1:
                    for i in range(0,const.TOTAL_LED_COUNT,1):
                        strip.setPixelColorRGB(i, 0, 0, 0)
                    for i in range(0,showSequenceCounter,1):
                        #print("i",i)
                        if (i < len(startHolds)):
                            hold = startHolds[i]
                            #print(hold)
                            strip.setPixelColorRGB(hold-1, 0, const.LED_VALUE, 0)
                        elif (i < (len(startHolds)+len(probHolds))):
                            hold = probHolds[i-len(startHolds)]
                            #print(hold)
                            strip.setPixelColorRGB(hold-1, 0, 0, const.LED_VALUE)
                        elif (i < (len(startHolds)+len(probHolds)+len(finHolds))):
                            hold = finHolds[i-len(startHolds)-len(probHolds)]
                            #print(hold)
                            strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, 0)                       
                    strip.show()
                    if (i == (len(startHolds)+len(probHolds)+len(finHolds))):
                        #print("reset")
                        showSequenceCounter = 0
                        shownSequenceCount = shownSequenceCount + 1   
            else:
                shownSequenceCount = 0
                showSequenceFlag = 0
                showSequenceCounter = 0
                self.lblInfo.setText(const.DEFAULTMSG)
        if (showTwoProbsFlag == 1):
            MyApp.toggleLEDs(S2PStartMatches, S2PProbMatches, S2PFinMatches)
        if (sliderFlag == 1):
            sliderFlag = 0
            self.populateProblemTable()
            start = self.slider.getRange()[0]
            end = self.slider.getRange()[1] - 1
            text = "Showing problems between grades - " + const.GRADES[start] + " and " + const.GRADES[end]
            self.lblInfo.setText(text)
                    
    def resetUserTimeIn(self,user):
        global usersLoggedIn
        index = MyApp.find(usersLoggedIn,user)[0]
        usersLoggedIn[index][1] = time.time()
        print("time in",usersLoggedIn)
        
    #logout user selected in lbUsers listbox
    def logout(self):
        global usersLoggedIn
        
        rowN = self.lbUsers.selectedIndexes()[0].row()
        user = self.lbUsers.item(rowN).text()
        index = MyApp.find(usersLoggedIn,user)[0]
        del usersLoggedIn[index]
        self.lbUsers.clear()
        if (len(usersLoggedIn) > 0):
            self.lbUsers.addItems(MyApp.column(usersLoggedIn,0))
        self.updateLogLabel()
        text = user + " logged out"
        self.lblInfo.setText(text)
        rowN = self.lbUsers.selectedIndexes()[0].row()
        self.lblLogbook.setText("Login and select a user to view logbook")
    
    #returns a column from a list - list must be a matrix in dimensions
    def column(matrix, i):
        return [row[i] for row in matrix]
    
    def login(self):
        global usersLoggedIn
        
        usersDB = userClass.readUsersFile()
        login = userClass.checkPassword(usersDB, self.leUsername.text(), self.lePassword.text())
        if (login == -2):
            #QtWidgets.QMessageBox.warning(self, "Oh no!", "I'm sorry this Username is unknown!")
            self.lblInfo.setText("Oh no!\nI'm sorry username not recognised")
        elif (login == -1):
            #QtWidgets.QMessageBox.warning(self, "Oh no!", "I'm sorry your password is incorrect!")
            self.lblInfo.setText("Oh no!\nI'm sorry your password is incorrect")
        elif (login == 0):
            username = [self.leUsername.text()]
            #check if already logged in
            if (MyApp.find(usersLoggedIn, username[0])[0] == -1):
                #QtWidgets.QMessageBox.warning(self, "Success!", "Well done, logged in!")
                text = username[0] +  " logged in"
                self.lblInfo.setText(text)
                usersLoggedIn.append([username[0],time.time()])
                self.lbUsers.clear()
                self.lbUsers.addItems(MyApp.column(usersLoggedIn,0))
                self.leUsername.clear()
                self.lePassword.clear()
            else:
                #QtWidgets.QMessageBox.warning(self, "Oh no!", "You're already logged in!!")
                self.lblInfo.setText("Oh no!\nYou're already logged in!!")
                
    def populateLogbook(self):
        self.tblLogbook.clear()
        if (len(usersLoggedIn) > 0): #if a user logged in
            try:
                rowN = self.lbUsers.selectedIndexes()[0].row()
                user = self.lbUsers.item(rowN).text()
                
                if (self.lbUsers.selectedIndexes() != []):
                    logbook = logClass.getUserLogbook(user)
                    self.tblLogbook.setRowCount(len(logbook)-1)
                    self.tblLogbook.setColumnCount(6)
                    self.tblLogbook.horizontalHeader().setVisible(True)
                    self.tblLogbook.setHorizontalHeaderLabels(logbook[0])
                    for i in range(1,len(logbook),1):
                        for j in range(0,6,1):
                            self.tblLogbook.setItem(i-1,j, QtWidgets.QTableWidgetItem(logbook[i][j]))
                    #set headers and column widths
                    header = self.tblLogbook.horizontalHeader()       
                    header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
                    header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
                    header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
                    header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
                    header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
                    header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
                    text = "Showing logbook for - " + user
                    self.lblLogbook.setText(text)
                else:
                    self.lblInfo.setText("Oh no!\nPlease select a user, you may need to login")
            except:
                self.lblInfo.setText("Oh no!\nPlease select a user, you may need to login")
        
    def populateProblemTable(self):
        global userFilter
        #populate problem list
        start = self.slider.getRange()[0]
        end = self.slider.getRange()[1] - 1
        problemList = problemClass.getGradeFilteredProblems(start, end)
        problemList = problemClass.getUserFilteredProblems(problemList, userFilter)
        self.tblProblems.setRowCount(len(problemList)-1)
        self.tblProblems.setColumnCount(5)
        self.tblProblems.horizontalHeader().setVisible(True)
        self.tblProblems.setHorizontalHeaderLabels(problemList[0])
        for i in range(1,len(problemList),1):
            for j in range(0,5,1):
                self.tblProblems.setItem(i-1,j, QtWidgets.QTableWidgetItem(problemList[i][j]))
        #set headers and column widths
        header = self.tblProblems.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        #text = "Showing problems between grades - " + const.GRADES[start] + " and " + const.GRADES[end]
        #self.lblInfo.setText(text)
        
    def resetAddProblemTab(self):
        print("reset")
        global newProbCounter
        global newStartHolds
        global newProbHolds
        global undoCounter
        #reset button colours            
        for num in range (1,const.TOTAL_LED_COUNT+1):
            label = getattr(self, 'pb{}'.format(num))
            label.setStyleSheet("background-color: rgba(240, 240, 240, 75%)")#f0f0f0(240,240,240) #efebe7(239,235,231)
            font = label.font();
            font.setPointSize(12);
            label.setFont(font);
            
        #reset inputs
        self.leProblemName.clear()
        self.cbGrade_2.setCurrentIndex(0)
        self.cbStars_2.setCurrentIndex(0)
        self.tbComments.clear()
        
        #init new problem globals
        newProbCounter = 0
        newStartHolds = []
        newProbHolds = []
        undoCounter = 0
        
    def saveNewProb(self):
        print('save')
        global newProbCounter
        global newProbHolds
        global newStartHolds
        global prevPb
        global usersLoggedIn
        
        problemsDB = problemClass.readProblemFile()
        
        #get user
        user = ''
        if (len(usersLoggedIn) > 0):
            try:
                rowN = self.lbUsers.selectedIndexes()[0].row()
                user = self.lbUsers.item(rowN).text()
                #as user is active, reset login time-in
                self.resetUserTimeIn(user)
            except:
                user = ''
             
        newProblem = []
        if (self.leProblemName.text() == ''):
            QtWidgets.QMessageBox.warning(self, "Oh no!", "You must give a problem name")
        elif ((MyApp.find(problemsDB,(self.leProblemName.text())))[0] != -1):
           QtWidgets.QMessageBox.warning(self, "Steady on!", "A problem with this name already exists, choose a new name")    
        elif (newProbCounter < 2):
            QtWidgets.QMessageBox.warning(self, "Easy now!", "You must click at least 2 holds")
        elif (user == ''):
            QtWidgets.QMessageBox.warning(self, "Have a word!", "You must login and select a user to add a new problem")
        else:
            #finalise last hold in newProbHolds
            holdString = str(prevPb.objectName())
            newProbHolds.append(int(re.search(r'\d+', holdString).group()))
            print('probHolds', newProbHolds)            
            #append name, grade, stars & date
            probName = self.leProblemName.text()
            newProblem.append(probName)
            newProblem.append(self.cbGrade_2.currentText())
            newProblem.append(self.cbStars_2.currentText())
            now = datetime.datetime.now()
            newProblem.append(now.strftime("%Y-%m-%d"))        
            #append user
            newProblem.append(user)            
            #append comments
            comments = self.tbComments.toPlainText().replace('\n', ' ')
            comments = comments.replace(',', '-')
            newProblem.append(comments)
            #append start holds
            newProblem.append(str(newStartHolds[0]))
            if (len(newStartHolds) == 2):
                newProblem.append(str(newStartHolds[1]))
                print("N start holds", 2)
            else:
                newProblem.append('')
                print("N start holds", 1)
            #append finish holds
            choice = QtWidgets.QMessageBox.question(self, 'Finish Holds',
                                                "Two Finish holds?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if (choice == QtWidgets.QMessageBox.Yes)&(len(newProbHolds) >= 2):
                newProblem.append(str(newProbHolds[-2]))#second to last hold
                newProblem.append(str(newProbHolds[-1]))#last hold
                del newProbHolds[-1]
                del newProbHolds[-1]
            else:
                newProblem.append(str(newProbHolds[-1]))
                newProblem.append('')
                del newProbHolds[-1]
            #append number of & problem holds
            newProblem.append(str(len(newProbHolds)))
            for hold in newProbHolds:
                newProblem.append(str(hold))
            print(newProblem)
            #save to file
            problemClass.addNewProb(newProblem)
            self.resetAddProblemTab()
            self.populateProblemTable()
            QtWidgets.QMessageBox.warning(self, "Bon Effort!", "Well Done! New problem added!")
            self.tabWidget.setCurrentIndex(0)
            text = "New problem added - " + probName + "\n by user - " + user
            self.lblInfo.setText(text)
            
    def undo(self):#undo the last hold added
        global newProbCounter
        global prevPb
        global newProbHolds
        global newStartHolds
        global undoCounter
        
        if (newProbCounter != 0):
             #QtWidgets.QMessageBox.warning(self, "Nothing to Undo", "There are no holds to Undo!")          
        #else:#hold to undo
            prevPb.setStyleSheet("background-color: #f0f0f0")
            self.setLEDbyButton(prevPb,"off")
            newProbCounter -= 1
            undoCounter = 1
            #set prevPb (previously pushed button) back one
            #and delete last entry to new problem array (start or problem holds)
            if (len(newProbHolds) != 0):
                prevPb = getattr(self, 'pb{}'.format(newProbHolds[-1]))
                del(newProbHolds[-1])
            elif (len(newStartHolds) != 0):
                prevPb = getattr(self, 'pb{}'.format(newStartHolds[-1]))
                del(newStartHolds[-1])
        
    def setLEDbyButton(self,button,colour):
        holdNumber = self.getHoldNumberFromButton(button)
        print("hold Number -", holdNumber, "colour -", colour)
        if (const.LINUX == 1):
            if (colour == "red"):
                strip.setPixelColorRGB(holdNumber-1, const.LED_VALUE, 0, 0)#red
            elif (colour == "green"):
                strip.setPixelColorRGB(holdNumber-1, 0, const.LED_VALUE, 0)#green
            elif (colour == "blue"):
                strip.setPixelColorRGB(holdNumber-1, 0, 0, const.LED_VALUE)#blue
            elif (colour == "off"):
                strip.setPixelColorRGB(holdNumber-1, 0, 0, 0)#off
            strip.show()
        
    def getHoldNumberFromButton(self,button):
        holdString = str(button.objectName())
        holdNumber = int(re.search(r'\d+', holdString).group())
        return holdNumber
                   
    def addHoldtoProb(self):
        global newProbCounter
        global prevPb
        global newProbHolds
        global newStartHolds
        global undoCounter
        
        undoCounter = 0
        
        #first check if button already clicked by loading colour
        colour = self.sender().palette().button().color().name()
        if (colour != '#f0f0f0'): #is it NOT the default colour? #efebe7
            QtWidgets.QMessageBox.warning(self, "Hold Added", "To remove ho use the Undo button")      
        else:
            print("new count", newProbCounter)
            if (newProbCounter == 0):
                self.offLEDs()
                self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                self.setLEDbyButton(self.sender(),"red")
            elif (newProbCounter == 1):
                self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                self.setLEDbyButton(self.sender(),"red")
                newStartHolds.append(self.getHoldNumberFromButton(prevPb))
                print("start", newStartHolds)
                prevPb.setStyleSheet("background-color: rgba(0, 128, 0, 75%)")#green
                self.setLEDbyButton(prevPb,"green")
            elif (newProbCounter == 2):
                choice = QtWidgets.QMessageBox.question(self, 'Start Holds',
                                                    "Two start holds?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if (choice == QtWidgets.QMessageBox.Yes):
                    #two start holds
                    self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                    self.setLEDbyButton(self.sender(),"red")
                    newStartHolds.append(self.getHoldNumberFromButton(prevPb))
                    print("start", newStartHolds)
                    prevPb.setStyleSheet("background-color: rgba(0, 128, 0, 75%)")#green
                    self.setLEDbyButton(prevPb,"green")
                else:
                    #only one start hold
                    self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                    self.setLEDbyButton(self.sender(),"red")
                    newProbHolds.append(self.getHoldNumberFromButton(prevPb))
                    prevPb.setStyleSheet("background-color: rgba(0, 0, 255, 75%)")#blue
                    self.setLEDbyButton(prevPb,"blue")
            elif (newProbCounter >= 3):
                #append hold to newProbHold array and change button and LED colours
                self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                self.setLEDbyButton(self.sender(),"red")
                newProbHolds.append(self.getHoldNumberFromButton(prevPb))
                print('newProbHolds', newProbHolds)
                prevPb.setStyleSheet("background-color: rgba(0, 0, 255, 75%)")#blue
                self.setLEDbyButton(prevPb,"blue")
            newProbCounter += 1
            prevPb = self.sender()
        
    def wheel(pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)
    
    def testLEDs(self):
        global showSequenceFlag
        global LEDState
        global showTwoProbsFlag
        
        text = "Test LEDs button pressed\nAll LEDs lit"
        self.lblInfo.setText(text)

        showSequenceFlag = 0     
        
        if showTwoProbsFlag == 1:
            self.showTwoProbs()
        
        if (LEDState == 0):
            LEDState = 1
            if const.LINUX == 1:
                for i in range(0,const.TOTAL_LED_COUNT,1):
                    strip.setPixelColorRGB(i,int((255/const.TOTAL_LED_COUNT)*i), 0, 0)
                for j in range(256*1):
                    for i in range(strip.numPixels()):
                        strip.setPixelColor(i, MyApp.wheel((i+j) & 255))
                strip.show()
        else:
            LEDState = 0
            self.offLEDs()
            
    def offLEDs(self):
        if const.LINUX == 1:
            for i in range(0,const.TOTAL_LED_COUNT,1):
                strip.setPixelColorRGB(i, 0, 0, 0)
                strip.show()
            
    def lightLEDs(startHolds, probHolds, finHolds):
        if const.LINUX == 1:
            for i in range(0,const.TOTAL_LED_COUNT,1):
                strip.setPixelColorRGB(i, 0, 0, 0)
            for hold in startHolds:
                strip.setPixelColorRGB(hold-1, 0, const.LED_VALUE, 0)
            for hold in probHolds:
                strip.setPixelColorRGB(hold-1, 0, 0, const.LED_VALUE)
            for hold in finHolds:
                strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, 0)
            strip.show()
        
    def lightTwoLEDs(startHolds, probHolds, finHolds, startHolds2, probHolds2, finHolds2):
        global showSequenceFlag
        showSequenceFlag = 0
        
        if const.LINUX == 1:
            for i in range(0,const.TOTAL_LED_COUNT,1):
                strip.setPixelColorRGB(i, 0, 0, 0)
            for hold in startHolds:
                strip.setPixelColorRGB(hold-1, 0, const.LED_VALUE, 0)#green
            for hold in probHolds:
                strip.setPixelColorRGB(hold-1, 0, 0, const.LED_VALUE)#blue
            for hold in finHolds:
                strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, 0)#red
            for hold in startHolds2:
                strip.setPixelColorRGB(hold-1, 0,const.LED_VALUE, const.LED_VALUE)#teal
            for hold in probHolds2:
                strip.setPixelColorRGB(hold-1, const.LED_VALUE, const.LED_VALUE,0)#teal
            for hold in finHolds2:
                strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0,const.LED_VALUE )#pink
            strip.show()
            
    def toggleLEDs(startHolds, probHolds, finHolds):
        global toggleLEDFlag
        
        if const.LINUX == 1:
            if toggleLEDFlag == 0:
                toggleLEDFlag = 1
                #print("toggle 0")
                for hold in startHolds:
                    strip.setPixelColorRGB(hold-1, 0, const.LED_VALUE, 0)#blue
                for hold in probHolds:
                    strip.setPixelColorRGB(hold-1, 0, 0, const.LED_VALUE)#green
                for hold in finHolds:
                    strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, 0)#red
            elif toggleLEDFlag == 1:
                toggleLEDFlag = 0
                #print("toggle 1")
                for hold in startHolds:
                    strip.setPixelColorRGB(hold-1, 0, const.LED_VALUE, const.LED_VALUE)#yellow
                for hold in probHolds:
                    strip.setPixelColorRGB(hold-1, const.LED_VALUE, const.LED_VALUE,0)#teal
                for hold in finHolds:
                    strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0,const.LED_VALUE )#pink
            strip.show()
        
    def find(l, elem):
        for row, i in enumerate(l):
            try:
                #print(i)
                column = i.index(elem)
            except ValueError:
                continue
            return row, column
        return [-1,-1]
    
    def updateLogProblemDropdowns(self,rowProb):
        problemsDB = problemClass.readProblemFile()
        
        grade = problemsDB[rowProb][1]
        stars = problemsDB[rowProb][2]
        
        index = self.cbStars.findText(stars, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cbStars.setCurrentIndex(index)
                    
        index = self.cbGrade.findText(grade, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cbGrade.setCurrentIndex(index)   

    
    def updateProbInfo(self,rowProb):
        problemsDB = problemClass.readProblemFile()
        
        probName = problemsDB[rowProb][0]
        grade = problemsDB[rowProb][1]
        stars = problemsDB[rowProb][2]
        date = problemsDB[rowProb][3]
        setter = problemClass.getUser(rowProb)
        notes = problemClass.getNotes(rowProb)
        
        infoText = probName + "\n   " + grade + "   " + stars + "\nDate added - " + date + "\nSet by - " + setter + "\nComments\n" + notes
        
        #get and present star votes
        starVotes = logClass.getStarVotes(probName)
        stars = []
        stars.append(starVotes.count('***'))
        stars.append(starVotes.count('**'))
        stars.append(starVotes.count('*'))
        stars.append(starVotes.count('-'))
        barRange = max(stars)
        if (barRange < 1):
            barRange = 1
        self.barStar3.setRange(0,barRange)
        self.barStar2.setRange(0,barRange)
        self.barStar1.setRange(0,barRange)
        self.barStar0.setRange(0,barRange)
        self.barStar3.setValue(starVotes.count('***'))
        self.barStar2.setValue(starVotes.count('**'))
        self.barStar1.setValue(starVotes.count('*'))
        self.barStar0.setValue(starVotes.count('-'))
        
        #reset grade bars to zero
        for num in range (1,7):
            label = getattr(self, 'lblBarGrade{}'.format(num))
            bar = getattr(self, 'barGrade{}'.format(num))
            label.setText("-")
            bar.setValue(0)
            
        #get and present gradevotes
        gradeVotes = logClass.getGradeVotes(probName)
        if (len(gradeVotes) > 0):
            maxGradeVotes = Counter(gradeVotes).most_common(1)[0][1]
            self.barGrade1.setRange(0,maxGradeVotes)
            self.barGrade2.setRange(0,maxGradeVotes)
            self.barGrade3.setRange(0,maxGradeVotes)
            self.barGrade4.setRange(0,maxGradeVotes)
            self.barGrade5.setRange(0,maxGradeVotes)
            self.barGrade6.setRange(0,maxGradeVotes)
                
            num = 1
            for grade,count in Counter(gradeVotes).most_common(6):
                label = getattr(self, 'lblBarGrade{}'.format(num))
                bar = getattr(self, 'barGrade{}'.format(num))
                num += 1
                label.setText(grade)
                bar.setValue(count)
                
        #get problem ascents
        ascents = logClass.getProblemAscents(probName)
        #display in a table
        self.populateAscents(ascents)
        
        #display info
        self.tbProblemInfo.setText(infoText)
        
    def populateAscents(self, ascents):
        
        self.tblAscents.setRowCount(len(ascents)-1)
        self.tblAscents.setColumnCount(6)
        self.tblAscents.horizontalHeader().setVisible(True)
        self.tblAscents.setHorizontalHeaderLabels(ascents[0])
        for i in range(1,len(ascents),1):
            for j in range(0,6,1):
                self.tblAscents.setItem(i-1,j, QtWidgets.QTableWidgetItem(ascents[i][j]))
        #set headers and column widths
        header = self.tblAscents.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)     
        
    def getRowProb(self):
        global S2PProbName
        global probName
        
        problemsDB = problemClass.readProblemFile()
        #store previous problem name
        S2PProbName = probName
        #get index of selected problem in table
        try:
            #get index of selected problem in table
            items = self.tblProblems.selectedIndexes()[0]
            #get name of problem
            probName = self.tblProblems.item((items.row()),0).text()        
            #find problem in problemDB using problem name from selected row
            rowProb = MyApp.find(problemsDB,probName)[0]
        except:
            rowProb = -1
        return rowProb
            
    def lightProblem(self):
        global mirrorFlag
        global showSequenceFlag
        global startHoldsS2P
        global probHoldsS2P
        global finHoldsS2P
        global startHolds
        global probHolds
        global finHolds
        global showTwoProbsFlag
        global probName
        
        showSequenceFlag = 0                
        mirrorFlag = 0
        
        #store the previous problem before loading the next
        startHoldsS2P = startHolds
        finHoldsS2P = finHolds
        probHoldsS2P = probHolds
        
        self.updateLogLabel()    
        rowProb = self.getRowProb()
        #call function to display problem info
        self.updateProbInfo(rowProb)
        self.updateLogProblemDropdowns(rowProb)
        #load the holds from the problemDB
        startHolds = problemClass.getStartHolds(rowProb)
        finHolds = problemClass.getFinHolds(rowProb)
        probHolds = problemClass.getHolds(rowProb)   
        MyApp.lightLEDs(startHolds, probHolds, finHolds)
        text = "Problem displayed on board - " + probName 
        self.lblInfo.setText(text)
        if showTwoProbsFlag == 1:
            self.showTwoProbs()
    
    def mirrorProb(self):
        global startHolds
        global probHolds
        global finHolds
        global startHoldsS2P
        global probHoldsS2P
        global finHoldsS2P        
        global mirrorFlag
        global probName
        
        if showTwoProbsFlag == 1:
            self.showTwoProbs()
        
        #store the previous problem before loading the next
        startHoldsS2P = startHolds
        finHoldsS2P = finHolds
        probHoldsS2P = probHolds       

        if (mirrorFlag == 0):
            mirrorFlag = 1    
            startHolds = mirror.getMirror(startHolds)
            probHolds = mirror.getMirror(probHolds)
            finHolds = mirror.getMirror(finHolds)
            #check we have a problem selected before lighting
            if (self.getRowProb() != -1):
                MyApp.lightLEDs(startHolds, probHolds, finHolds)
                text = "Mirror displayed on board - " + probName 
                self.lblInfo.setText(text)
            else:
                self.lblInfo.setText("Select a problem before Mirroring")
        else:
            #check we have a problem selected before lighting
            if (self.getRowProb() != -1):
                self.lightProblem()
            
    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        event.accept()            
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    LEDState = 0
    if const.LINUX == 1:
        strip = Adafruit_NeoPixel(const.TOTAL_LED_COUNT, 18, 800000, 5, False, 255)
        strip.begin()   #only call this once - each call creates new memory instance which
                        #eventually will crash program
        strip.setPixelColorRGB(const.TOTAL_LED_COUNT, 0, 0, 0)
        strip.show()
        
    sys.exit(app.exec_())
    
