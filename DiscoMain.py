LINUX = 1

import sys
from PyQt5 import QtWidgets, uic, QtCore#, QtGui,
from PyQt5.QtCore import QTimer
#import time
import re
import datetime
import time
from collections import Counter
from threading import Timer

if LINUX == 1:
    from neopixel import *

from csvFuncs import problemClass
from mirror import mirror
from usersFuncs import userClass
from logFuncs import logClass
#from strandtest import strandTest

TOTAL_LED_COUNT = 126
LED_VALUE = 50

qtCreatorFile = "DiscoBoard.ui" # Enter file here.
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):        
    def __init__(self):
        global problemsDB
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
        
        #global prevPb
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        #LED Board widgets
        self.setupUi(self)
        
        #Connect buttons to functions
        self.pbTestLEDs.clicked.connect(self.testLEDs)        
        self.tblProblems.clicked.connect(self.lightProblem)
        self.pbMirror.clicked.connect(self.mirrorProb)
        self.pbLogin.clicked.connect(self.login)
        self.pbLogout.clicked.connect(self.logout)
        self.lbUsers.clicked.connect(self.updateLogLabel)
        self.pbLogProblem.clicked.connect(self.logProblem)
        self.pbSequence.clicked.connect(self.showSequence)
        self.pbShowTwoProbs.clicked.connect(self.showTwoProbs)
        self.pbViewLogbook.clicked.connect(self.viewLogbook)
        
        #new problem widgiets
        self.pbDiscard.clicked.connect(self.resetAddProblemTab)
        self.pbSave.clicked.connect(self.saveNewProb)
        self.pbUndo.clicked.connect(self.undo)
        
        #Add user tab
        self.pbAddNewUsers.clicked.connect(self.addNewUser)
        
        #link hold buttons to the changeButtonColour function
        for num in range (1,TOTAL_LED_COUNT+1):
            label = getattr(self, 'pb{}'.format(num))
            label.clicked.connect(self.addHoldtoProb)
            #make them transparent???
            label.setStyleSheet("background-color: rgba(240, 240, 240, 75%)")
                
        self.populateProblemTable()
        self.tabWidget.setCurrentIndex(0)
        
        #start timer that logs out inactive users
        self.start_timer()
        
        #self.showFullScreen()
        #self.LEDBoard.setStyleSheet("background-color: rgba(255, 0, 0, 0%)")
        
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
        startHoldsQ = []
        probHoldsQ = []
        finHoldsQ = []
        
    def viewLogbook(self):
        self.tabWidget.setCurrentIndex(3)
        self.populateLogbook()
        
    def showTwoProbs(self):
        print("show two probs")
        #self.light2LEDs()
        #change button colour to show "two prob" mode is active
        
    def showSequence(self):
        global mirrorFlag
        global showSequenceFlag
        global showSequenceCounter
        global startHoldsQ
        global probHoldsQ
        global finHoldsQ    
        global shownSequenceCount
        
        print("show sequence")
        #call a version of lightLEDs within an IRQ
        #use a timer 250ms???
        #set a flag/counter
        #timer elapses light next hold in sequence
        #loop through all holds 10??? times
        showSequenceFlag = 1 
        showSequenceCounter = 0
        shownSequenceCount = 0
        
        items = self.tblProblems.selectedIndexes()[0]
        probName = self.tblProblems.item((items.row()),0).text()
        rowProb = MyApp.find(problemsDB,probName)[0]
        #load the holds from the problemDB
        startHoldsQ = problemClass.getStartHolds(problemsDB, rowProb)
        probHoldsQ = problemClass.getHolds(problemsDB, rowProb)
        finHoldsQ = problemClass.getFinHolds(problemsDB, rowProb)
        
        if (mirrorFlag == 1):
            startHoldsQ = mirror.getMirror(startHoldsQ)
            probHoldsQ = mirror.getMirror(probHoldsQ)
            finHoldsQ = mirror.getMirror(finHoldsQ)
                   
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
            
        
    def addNewUser(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        userClass.addNewUser([self.leAddUsername.text(), self.leAddPassword.text(),date])
              
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
            #if time since logged-in is 30mins (1800secs)
            if ((time.time() - timeIn) > 1800):
                #log out that user
                index = MyApp.find(usersLoggedIn,user)[0]
                del usersLoggedIn[index]
                self.lbUsers.clear()
                if (len(usersLoggedIn) > 0):
                    self.lbUsers.addItems(MyApp.column(usersLoggedIn,0))
                    
    def timerQuickISR(self):
        global startHoldsQ
        global probHoldsQ
        global finHoldsQ
        global showSequenceFlag
        global showSequenceCounter
        global shownSequenceCount
        #print("quick timer", showSequenceFlag, showSequenceCounter, shownSequenceCount)
        if (showSequenceFlag == 1):
            text = "Showing sequence " + str(10 - shownSequenceCount)
            self.lblInfo.setText(text)
            if (shownSequenceCount < 10):
                if LINUX == 1:
                    showSequenceCounter = showSequenceCounter + 1
                    for i in range(0,TOTAL_LED_COUNT,1):
                        strip.setPixelColorRGB(i, 0, 0, 0)
                    for i in range(0,showSequenceCounter,1):
                        #print("i",i)
                        if (i < len(startHoldsQ)):
                            hold = startHoldsQ[i]
                            #print(hold)
                            strip.setPixelColorRGB(hold-1, 0, LED_VALUE, 0)
                        elif (i < (len(startHoldsQ)+len(probHoldsQ))):
                            hold = probHoldsQ[i-len(startHoldsQ)]
                            #print(hold)
                            strip.setPixelColorRGB(hold-1, 0, 0, LED_VALUE)
                        elif (i < (len(startHoldsQ)+len(probHoldsQ)+len(finHoldsQ))):
                            hold = finHoldsQ[i-len(startHoldsQ)-len(probHoldsQ)]
                            #print(hold)
                            strip.setPixelColorRGB(hold-1, LED_VALUE, 0, 0)
                        if (i == (len(startHoldsQ)+len(probHoldsQ)+len(finHoldsQ))):
                            #print("reset")
                            showSequenceCounter = 0
                            shownSequenceCount = shownSequenceCount + 1                          
                    strip.show()
            else:
                shownSequenceCount = 0
                showSequenceFlag = 0
                showSequenceCounter = 0
                self.lblInfo.setText("Welcome to Board of High Repute")
                    
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
                text = "Success!\nYou logged in\nWelcome - " + username[0]
                self.lblInfo.setText(text)
                usersLoggedIn.append([username[0],time.time()])
                print("users logged in", MyApp.column(usersLoggedIn,0))
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
                    print(user)
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
                else:
                    self.lblInfo.setText("Oh no!\nPlease select a user, you may need to login")
            except:
                self.lblInfo.setText("Oh no!\nPlease select a user, you may need to login")
        
    def populateProblemTable(self):
        global problemsDB
        #populate problem list
        problemsDB = problemClass.readProblemFile()
        problemList = problemClass.getNameGradeStars(problemsDB)
        self.tblProblems.setRowCount(len(problemList)-1)
        self.tblProblems.setColumnCount(4)
        self.tblProblems.horizontalHeader().setVisible(True)
        self.tblProblems.setHorizontalHeaderLabels(problemList[0])
        for i in range(1,len(problemList),1):
            for j in range(0,4,1):
                self.tblProblems.setItem(i-1,j, QtWidgets.QTableWidgetItem(problemList[i][j]))
        #set headers and column widths
        header = self.tblProblems.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        
    def resetAddProblemTab(self):
        print("reset")
        global newProbCounter
        global newStartHolds
        global newProbHolds
        global undoCounter
        #reset button colours            
        for num in range (1,TOTAL_LED_COUNT+1):
            label = getattr(self, 'pb{}'.format(num))
            label.setStyleSheet("background-color: rgba(240, 240, 240, 75%)")#f0f0f0(240,240,240) #efebe7(239,235,231)
            font = label.font();
            font.setPointSize(12);
            label.setFont(font);
        
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
        
        print("find - ", MyApp.find(problemsDB,(self.leProblemName.text()))[0])
        
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
            newProblem.append(self.leProblemName.text())
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
                #if (len(newProbHolds) == 2):
                newProblem.append(str(newProbHolds[-2]))#second to last hold
                newProblem.append(str(newProbHolds[-1]))#last hold
                del newProbHolds[-1]
                #else:
                #    newProblem.append(str(newProbHolds[-1]))#last hold
                #    newProblem.append('')
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
                
        print("prob", newProbHolds)
        print("start", newStartHolds)
        
    def setLEDbyButton(self,button,colour):
        holdString = str(button.objectName())
        holdNumber = int(re.search(r'\d+', holdString).group())
        print("hold Number -", holdNumber, "colour -", colour)
        if (LINUX == 1):
            if (colour == "red"):
                strip.setPixelColorRGB(holdNumber, LED_VALUE, 0, 0)#red
            elif (colour == "green"):
                strip.setPixelColorRGB(holdNumber, 0, LED_VALUE, 0)#green
            elif (colour == "blue"):
                strip.setPixelColorRGB(holdNumber, 0, 0, LED_VALUE)#blue
        
    def getHoldNumberFromButton(self,button):
        holdString = str(prevPb.objectName())
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
        global LEDState
        if (LEDState == 0):
            LEDState = 1
            if LINUX == 1:
                for i in range(0,TOTAL_LED_COUNT,1):
                    strip.setPixelColorRGB(i,int((255/TOTAL_LED_COUNT)*i), 0, 0)
                for j in range(256*1):
                    for i in range(strip.numPixels()):
                        strip.setPixelColor(i, MyApp.wheel((i+j) & 255))
                strip.show()
            print('on')
        else:
            LEDState = 0
            if LINUX == 1:
                for i in range(0,TOTAL_LED_COUNT,1):
                    strip.setPixelColorRGB(i, 0, 0, 0)
                    strip.show()
            print('off')
            
    def lightLEDs(startHolds, probHolds, finHolds):
        if LINUX == 1:
            for i in range(0,TOTAL_LED_COUNT,1):
                strip.setPixelColorRGB(i, 0, 0, 0)
            for hold in startHolds:
                strip.setPixelColorRGB(hold-1, 0, LED_VALUE, 0)
            for hold in probHolds:
                strip.setPixelColorRGB(hold-1, 0, 0, LED_VALUE)
            for hold in finHolds:
                strip.setPixelColorRGB(hold-1, LED_VALUE, 0, 0)
            strip.show()
        print('show')
        
    def lightTwoLEDs(startHolds, probHolds, finHolds, startHolds2, probHolds2, finHolds2):
        global showSequenceFlag
        showSequenceFlag = 0
        
        if LINUX == 1:
            for i in range(0,TOTAL_LED_COUNT,1):
                strip.setPixelColorRGB(i, 0, 0, 0)
            for hold in probHolds:
                strip.setPixelColorRGB(hold-1, 0, 0, LED_VALUE)#blue
            for hold in startHolds:
                strip.setPixelColorRGB(hold-1, 0, LED_VALUE, 0)#green
            for hold in finHolds:
                strip.setPixelColorRGB(hold-1, LED_VALUE, 0, 0)#red
            for hold in probHolds2:
                strip.setPixelColorRGB(hold-1, LED_VALUE, 0, LED_VALUE)#yellow
            for hold in startHolds2:
                strip.setPixelColorRGB(hold-1, 0, LED_VALUE, LED_VALUE)#teal
            for hold in finHolds2:
                strip.setPixelColorRGB(hold-1, LED_VALUE, 0,LED_VALUE )#pink
            #how handle one hold on both problems
            #second timer with short period 250ms???
            #toggle LED colour on timer elapse
            #here find crossover and pass those holds to the timer
            #flag - set a 2 problem flag that is cleared when two prob mode is exited
            strip.show()
        print('show')
        
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
        global problemsDB
        grade = problemsDB[rowProb][1]
        stars = problemsDB[rowProb][2]
        
        index = self.cbStars.findText(stars, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cbStars.setCurrentIndex(index)
                    
        index = self.cbGrade.findText(grade, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cbGrade.setCurrentIndex(index)   

    
    def updateProbInfo(self,rowProb):
        global problemsDB
        
        probName = problemsDB[rowProb][0]
        grade = problemsDB[rowProb][1]
        stars = problemsDB[rowProb][2]
        date = problemsDB[rowProb][3]
        setter = problemClass.getUser(problemsDB,rowProb)
        notes = problemClass.getNotes(problemsDB, rowProb)
        
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
            print("grade votes",gradeVotes)
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
                    
        #display info
        self.tbProblemInfo.setText(infoText)
        
    def getRowProb(self):
        #get index of selected problem in table
        items = self.tblProblems.selectedIndexes()[0]
        #get name of problem
        probName = self.tblProblems.item((items.row()),0).text()
        #find problem in problemDB using problem name from selected row
        rowProb = MyApp.find(problemsDB,probName)[0]
        return rowProb
            
    def lightProblem(self):
        global mirrorFlag
        global showSequenceFlag
        
        self.updateLogLabel()

        showSequenceFlag = 0                
        mirrorFlag = 0
        rowProb = self.getRowProb()
        #call function to display problem info
        self.updateProbInfo(rowProb)
        self.updateLogProblemDropdowns(rowProb)
        #load the holds from the problemDB
        startHolds = problemClass.getStartHolds(problemsDB, rowProb)
        finHolds = problemClass.getFinHolds(problemsDB, rowProb)
        probHolds = problemClass.getHolds(problemsDB, rowProb)
        print('start',startHolds)
        print('holds',probHolds)
        print('fin',finHolds)
        MyApp.lightLEDs(startHolds, probHolds, finHolds)
    
    def mirrorProb(self):
        print('mirror')
        global mirrorFlag
        if (mirrorFlag == 0):
            mirrorFlag = 1
            items = self.tblProblems.selectedIndexes()[0]
            rowProb = MyApp.find(problemsDB,(self.tblProblems.item((items.row()),0).text()))[0]
            startHolds = problemClass.getStartHolds(problemsDB, rowProb)
            finHolds = problemClass.getFinHolds(problemsDB, rowProb)
            probHolds = problemClass.getHolds(problemsDB, rowProb)
            print('start',startHolds)
            print('prob',probHolds)
            print('fin',finHolds)
            startHolds = mirror.getMirror(startHolds)
            print('startMirror',startHolds)
            probHolds = mirror.getMirror(probHolds)
            print('probMirror',probHolds)
            finHolds = mirror.getMirror(finHolds)
            print('finMirror',finHolds)
            MyApp.lightLEDs(startHolds, probHolds, finHolds)
        else:
            self.lightProblem()
            
    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        event.accept()            
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    LEDState = 0
    if LINUX == 1:
        strip = Adafruit_NeoPixel(TOTAL_LED_COUNT, 18, 800000, 5, False, 255)
        strip.begin()   #only call this once - each call creates new memory instance which
                        #eventually will crash program
        strip.setPixelColorRGB(TOTAL_LED_COUNT, 0, 0, 0)
        strip.show()
        
    sys.exit(app.exec_())
    
