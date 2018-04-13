import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
#import time
import re
import datetime

#from neopixel import *

from csvFuncs import problemClass
from mirror import mirror

TOTAL_LED_COUNT = 150

qtCreatorFile = "DiscoBoard.ui" # Enter file here.
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    stringlist = ['hello', 'James','one', 'two']
    
    
    def __init__(self):
        global problemsDB
        global newStartHolds
        global newProbHolds
        global newProbCounter
        #global prevPb
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        #LED Board widgets
        self.setupUi(self)
        self.pbTestLEDs.clicked.connect(self.testLEDs)
        self.lbProblemList.itemSelectionChanged.connect(self.lightProblem)
        self.pbMirror.clicked.connect(self.mirrorProb)
        #new problem widgiets
        self.pbDiscard.clicked.connect(self.resetAddProblemTab)
        self.pbSave.clicked.connect(self.saveNewProb)
        self.pb1.clicked.connect(self.changeButtonColour)
        self.pb2.clicked.connect(self.changeButtonColour)
        self.pb3.clicked.connect(self.changeButtonColour)
        self.pb4.clicked.connect(self.changeButtonColour)
        self.pb5.clicked.connect(self.changeButtonColour)
        self.pb6.clicked.connect(self.changeButtonColour)
        self.pb7.clicked.connect(self.changeButtonColour)
        self.pb8.clicked.connect(self.changeButtonColour)
        #populate problem list
        problemsDB = problemClass.readProblemFile()
        problemList = problemClass.getNameGradeStars(problemsDB)
        print(problemList)
        for i in range(len(problemList)):
            self.lbProblemList.addItem('\t'.join(problemList[i]))
        #init new problem globals
        newProbCounter = 0
        newStartHolds = []
        newProbHolds = []
        
    def resetAddProblemTab(self):
        print("reset")
        global newProbCounter
        global newStartHolds
        global newProbHolds
        #reset button colours
        self.pb1.setStyleSheet("background-color: #f0f0f0")
        self.pb2.setStyleSheet("background-color: #f0f0f0")
        self.pb3.setStyleSheet("background-color: #f0f0f0")
        self.pb4.setStyleSheet("background-color: #f0f0f0")
        self.pb5.setStyleSheet("background-color: #f0f0f0")
        self.pb6.setStyleSheet("background-color: #f0f0f0")
        self.pb7.setStyleSheet("background-color: #f0f0f0")
        self.pb8.setStyleSheet("background-color: #f0f0f0")
        #init new problem globals
        newProbCounter = 0
        newStartHolds = []
        newProbHolds = []                
        
    def saveNewProb(self):
        print('save')
        global newProbCounter
        global newProbHolds
        global newStartHolds
        
        #format        name    grade  stars   date        start1 & 2    fin-1 & 2   N-holds   holds
        #newProblem = ['new',  '7a',  '3',  '11/04/2018',    '1', '',   '9', '',   '3',     '1', '5', '9']
              
        newProblem = []
        if (self.leProblemName.text() == ''):
            QtWidgets.QMessageBox.warning(self, "Warning", "You must give a problem name")
        elif (newProbCounter < 2):
            QtWidgets.QMessageBox.warning(self, "Warning", "Must click atleast 2 holds")
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
            newProblem.append(now.strftime("%d-%m-%Y"))
            
            #append start holds
            newProblem.append(str(newStartHolds[0]))
            newProblem.append(str(newStartHolds[1]))
            if ((str(newStartHolds[1])) == ''):
                nStartHolds = 1
            else:
                nStartHolds = 2
            print ('nstart', nStartHolds)
            
            #append finish holds
            choice = QtWidgets.QMessageBox.question(self, 'Finish Holds',
                                                "Two Finish holds?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if (choice == QtWidgets.QMessageBox.Yes):
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
            MyApp.resetAddProblemTab(self)
                   
    def changeButtonColour(self):
        global newProbCounter
        global prevPb
        global newProbHolds
        
        #first check if button already clicked
        colour = self.sender().palette().button().color().name()
        print(colour)
        if (colour != '#f0f0f0'):
            holdString = str(self.sender().objectName())
            holdNumber = int(re.search(r'\d+', holdString).group())
            self.sender().setStyleSheet("background-color: #f0f0f0")
            #delete this hold from problem/start holds
            if holdNumber in newProbHolds: newProbHolds.remove(holdNumber)
            if holdNumber in newStartHolds: newStartHolds.remove(holdNumber)
            print("newProbHolds",newProbHolds)
        else:
            print(newProbCounter)
            if (newProbCounter == 0):
                self.sender().setStyleSheet("background-color: red")
                
            elif (newProbCounter == 1):
                self.sender().setStyleSheet("background-color: red")
                #save prev hold
                holdString = str(prevPb.objectName())
                holdNumber = int(re.search(r'\d+', holdString).group())
                newStartHolds.append(holdNumber)
                print(newStartHolds)
                prevPb.setStyleSheet("background-color: green")
            elif (newProbCounter == 2):
                choice = QtWidgets.QMessageBox.question(self, 'Start Holds',
                                                    "Two start holds?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if (choice == QtWidgets.QMessageBox.Yes):
                    self.sender().setStyleSheet("background-color: red")
                    #save prev hold
                    holdString = str(prevPb.objectName())
                    newStartHolds.append(int(re.search(r'\d+', holdString).group()))
                    print(newStartHolds)
                    prevPb.setStyleSheet("background-color: green")
                else:
                    newStartHolds.append(0)
                    holdString = str(prevPb.objectName())
                    newProbHolds.append(int(re.search(r'\d+', holdString).group()))
                    self.sender().setStyleSheet("background-color: red")
                    prevPb.setStyleSheet("background-color: blue")
            elif (newProbCounter >= 3):
                holdString = str(prevPb.objectName())
                newProbHolds.append(int(re.search(r'\d+', holdString).group()))
                print('newProbHolds', newProbHolds)
                self.sender().setStyleSheet("background-color: red")
                prevPb.setStyleSheet("background-color: blue")
            newProbCounter += 1
            prevPb = self.sender()
        
    def testLEDs(self):
        global LEDState
        if (LEDState == 0):
            LEDState = 1
            #for i in range(0,TOTAL_LED_COUNT,1):
            #    strip.setPixelColorRGB(i, i*5, 0, 50)
            #strip.show()
            print('on')
        else:
            LEDState = 0
            #for i in range(0,TOTAL_LED_COUNT,1):
            #    strip.setPixelColorRGB(i, 0, 0, 0)
            #strip.show()
            print('off')
            
    def lightLEDs(startHolds, probHolds, finHolds):
        #for i in range(0,TOTAL_LED_COUNT,1):
        #    strip.setPixelColorRGB(i, 0, 0, 0)
        #for hold in probHolds:
        #    strip.setPixelColorRGB(hold-1, 0, 0, 50)
        #for hold in startHolds:
        #    strip.setPixelColorRGB(hold-1, 0, 50, 0)
        #for hold in finHolds:
        #    strip.setPixelColorRGB(hold-1, 50, 0, 0)
        #strip.show()
        print('show')
            
    def lightProblem(self):
        items = self.lbProblemList.selectedIndexes()[0]
        rowProb = (items.row())
        startHolds = problemClass.getStartHolds(problemsDB, rowProb)
        finHolds = problemClass.getFinHolds(problemsDB, rowProb)
        probHolds = problemClass.getHolds(problemsDB, rowProb)
        print('start',startHolds)
        print('holds',probHolds)
        print('fin',finHolds)
        MyApp.lightLEDs(startHolds, probHolds, finHolds)
    
    def mirrorProb(self):
        print('mirror')
        items = self.lbProblemList.selectedIndexes()[0]
        rowProb = (items.row())
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
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    LEDState = 0
    #strip = Adafruit_NeoPixel(TOTAL_LED_COUNT, 18, 800000, 5, False, 255)
    #strip.begin()   #only call this once - each call creates new memory instance which
                    #eventually will crash program
    #strip.setPixelColorRGB(TOTAL_LED_COUNT, 0, 0, 0)
    #strip.show()
        
    sys.exit(app.exec_())
    
