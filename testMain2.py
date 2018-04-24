import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
#import time
import re
import datetime

from neopixel import *

from csvFuncs import problemClass
from mirror import mirror
#from strandtest import strandTest

TOTAL_LED_COUNT = 126

qtCreatorFile = "DiscoBoard.ui" # Enter file here.
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    stringlist = ['hello', 'James','one', 'two']
    
    
    def __init__(self):
        global problemsDB
        global newStartHolds
        global newProbHolds
        global newProbCounter
        global mirrorFlag
        #global prevPb
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        #LED Board widgets
        self.setupUi(self)
        #init Add Problem tab - bodge as should work without this
        #self.resetAddProblemTab()
        
        self.pbTestLEDs.clicked.connect(self.testLEDs)
        #self.pbTestLEDs.clicked.connect(strandTest.rainbow(strip))
        #self.lbProblemList.itemSelectionChanged.connect(self.lightProblem)
        self.tblProblems.clicked.connect(self.lightProblem)
<<<<<<< HEAD
=======
        
        #set pbMirror transparent
>>>>>>> 42af958c9063f6b4e055c52097ee0f877040ee9f
        self.pbMirror.clicked.connect(self.mirrorProb)
        
        #new problem widgiets
        self.pbDiscard.clicked.connect(self.resetAddProblemTab)
        self.pbSave.clicked.connect(self.saveNewProb)
<<<<<<< HEAD
        self.pb1.clicked.connect(self.changeButtonColour)
        self.pb2.clicked.connect(self.changeButtonColour)
        self.pb3.clicked.connect(self.changeButtonColour)
        self.pb4.clicked.connect(self.changeButtonColour)
        self.pb5.clicked.connect(self.changeButtonColour)
        self.pb6.clicked.connect(self.changeButtonColour)
        self.pb7.clicked.connect(self.changeButtonColour)
        self.pb8.clicked.connect(self.changeButtonColour)
        self.pb9.clicked.connect(self.changeButtonColour)
        self.pb10.clicked.connect(self.changeButtonColour)
        self.pb11.clicked.connect(self.changeButtonColour)
        self.pb12.clicked.connect(self.changeButtonColour)
        self.pb13.clicked.connect(self.changeButtonColour)
        self.pb14.clicked.connect(self.changeButtonColour)
        self.pb15.clicked.connect(self.changeButtonColour)
        self.pb16.clicked.connect(self.changeButtonColour)
        self.pb17.clicked.connect(self.changeButtonColour)
        self.pb18.clicked.connect(self.changeButtonColour)
        self.pb19.clicked.connect(self.changeButtonColour)
        self.pb20.clicked.connect(self.changeButtonColour)
        self.pb21.clicked.connect(self.changeButtonColour)
        self.pb22.clicked.connect(self.changeButtonColour)
        self.pb23.clicked.connect(self.changeButtonColour)
        self.pb24.clicked.connect(self.changeButtonColour)
        self.pb25.clicked.connect(self.changeButtonColour)
        self.pb26.clicked.connect(self.changeButtonColour)
        self.pb27.clicked.connect(self.changeButtonColour)
        self.pb28.clicked.connect(self.changeButtonColour)
        self.pb29.clicked.connect(self.changeButtonColour)
        self.pb30.clicked.connect(self.changeButtonColour)
        self.pb31.clicked.connect(self.changeButtonColour)
        self.pb32.clicked.connect(self.changeButtonColour)
        self.pb33.clicked.connect(self.changeButtonColour)
        self.pb34.clicked.connect(self.changeButtonColour)
        self.pb35.clicked.connect(self.changeButtonColour)
        self.pb36.clicked.connect(self.changeButtonColour)
        self.pb37.clicked.connect(self.changeButtonColour)
        self.pb38.clicked.connect(self.changeButtonColour)
        self.pb39.clicked.connect(self.changeButtonColour)
        self.pb40.clicked.connect(self.changeButtonColour)
        self.pb41.clicked.connect(self.changeButtonColour)
        self.pb42.clicked.connect(self.changeButtonColour)
        self.pb43.clicked.connect(self.changeButtonColour)
        self.pb44.clicked.connect(self.changeButtonColour)
        self.pb45.clicked.connect(self.changeButtonColour)
        self.pb46.clicked.connect(self.changeButtonColour)
        self.pb47.clicked.connect(self.changeButtonColour)
        self.pb48.clicked.connect(self.changeButtonColour)
        self.pb49.clicked.connect(self.changeButtonColour)
        self.pb50.clicked.connect(self.changeButtonColour)
        self.pb51.clicked.connect(self.changeButtonColour)
        self.pb52.clicked.connect(self.changeButtonColour)
        self.pb53.clicked.connect(self.changeButtonColour)
        self.pb54.clicked.connect(self.changeButtonColour)
        self.pb55.clicked.connect(self.changeButtonColour)
        self.pb56.clicked.connect(self.changeButtonColour)
        self.pb57.clicked.connect(self.changeButtonColour)
        self.pb58.clicked.connect(self.changeButtonColour)
        self.pb59.clicked.connect(self.changeButtonColour)
        self.pb60.clicked.connect(self.changeButtonColour)
        self.pb61.clicked.connect(self.changeButtonColour)
        self.pb62.clicked.connect(self.changeButtonColour)
        self.pb63.clicked.connect(self.changeButtonColour)
        self.pb64.clicked.connect(self.changeButtonColour)
        self.pb65.clicked.connect(self.changeButtonColour)
        self.pb66.clicked.connect(self.changeButtonColour)
        self.pb67.clicked.connect(self.changeButtonColour)
        self.pb68.clicked.connect(self.changeButtonColour)
        self.pb69.clicked.connect(self.changeButtonColour)
        self.pb70.clicked.connect(self.changeButtonColour)
        self.pb71.clicked.connect(self.changeButtonColour)
        self.pb72.clicked.connect(self.changeButtonColour)
        self.pb73.clicked.connect(self.changeButtonColour)
        self.pb74.clicked.connect(self.changeButtonColour)
        self.pb75.clicked.connect(self.changeButtonColour)
        self.pb76.clicked.connect(self.changeButtonColour)
        self.pb77.clicked.connect(self.changeButtonColour)
        self.pb78.clicked.connect(self.changeButtonColour)
        self.pb79.clicked.connect(self.changeButtonColour)
        self.pb80.clicked.connect(self.changeButtonColour)
        self.pb81.clicked.connect(self.changeButtonColour)
        self.pb82.clicked.connect(self.changeButtonColour)
        self.pb83.clicked.connect(self.changeButtonColour)
        self.pb84.clicked.connect(self.changeButtonColour)
        self.pb85.clicked.connect(self.changeButtonColour)
        self.pb86.clicked.connect(self.changeButtonColour)
        self.pb87.clicked.connect(self.changeButtonColour)
        self.pb88.clicked.connect(self.changeButtonColour)
        self.pb89.clicked.connect(self.changeButtonColour)
        self.pb90.clicked.connect(self.changeButtonColour)
        self.pb91.clicked.connect(self.changeButtonColour)
        self.pb92.clicked.connect(self.changeButtonColour)
        self.pb93.clicked.connect(self.changeButtonColour)
        self.pb94.clicked.connect(self.changeButtonColour)
        self.pb95.clicked.connect(self.changeButtonColour)
        self.pb96.clicked.connect(self.changeButtonColour)
        self.pb97.clicked.connect(self.changeButtonColour)
        self.pb98.clicked.connect(self.changeButtonColour)
        self.pb99.clicked.connect(self.changeButtonColour)
        self.pb100.clicked.connect(self.changeButtonColour)
        self.pb101.clicked.connect(self.changeButtonColour)
        self.pb102.clicked.connect(self.changeButtonColour)
        self.pb103.clicked.connect(self.changeButtonColour)
        self.pb104.clicked.connect(self.changeButtonColour)
        self.pb105.clicked.connect(self.changeButtonColour)
        self.pb106.clicked.connect(self.changeButtonColour)
        self.pb107.clicked.connect(self.changeButtonColour)
        self.pb108.clicked.connect(self.changeButtonColour)
        self.pb109.clicked.connect(self.changeButtonColour)
        self.pb110.clicked.connect(self.changeButtonColour)
        self.pb111.clicked.connect(self.changeButtonColour)
        self.pb112.clicked.connect(self.changeButtonColour)
        self.pb113.clicked.connect(self.changeButtonColour)
        self.pb114.clicked.connect(self.changeButtonColour)
        self.pb115.clicked.connect(self.changeButtonColour)
        self.pb116.clicked.connect(self.changeButtonColour)
        self.pb117.clicked.connect(self.changeButtonColour)
        self.pb118.clicked.connect(self.changeButtonColour)
        self.pb119.clicked.connect(self.changeButtonColour)
        self.pb120.clicked.connect(self.changeButtonColour)
        self.pb121.clicked.connect(self.changeButtonColour)
        self.pb122.clicked.connect(self.changeButtonColour)
        self.pb123.clicked.connect(self.changeButtonColour)
        self.pb124.clicked.connect(self.changeButtonColour)
        self.pb125.clicked.connect(self.changeButtonColour)
        self.pb126.clicked.connect(self.changeButtonColour)
        
=======
        for num in range (1,TOTAL_LED_COUNT+1):
            label = getattr(self, 'pb{}'.format(num))
            label.clicked.connect(self.changeButtonColour)
            label.setStyleSheet("background-color: rgba(240, 240, 240, 75%)")
                
>>>>>>> 42af958c9063f6b4e055c52097ee0f877040ee9f
        self.populateProblemTable()
        self.tabWidget.setCurrentIndex(0)
        
        #init new problem globals
        newProbCounter = 0
        newStartHolds = []
        newProbHolds = []
        mirrorFlag = 0
        
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
<<<<<<< HEAD
        #reset button colours
        self.pb1.setStyleSheet("background-color: #efebe7")
        self.pb2.setStyleSheet("background-color: #efebe7")
        self.pb3.setStyleSheet("background-color: #efebe7")
        self.pb4.setStyleSheet("background-color: #efebe7")
        self.pb5.setStyleSheet("background-color: #efebe7")
        self.pb6.setStyleSheet("background-color: #efebe7")
        self.pb7.setStyleSheet("background-color: #efebe7")
        self.pb8.setStyleSheet("background-color: #efebe7")
=======
        #reset button colours            
        for num in range (1,TOTAL_LED_COUNT+1):
            label = getattr(self, 'pb{}'.format(num))
            label.setStyleSheet("background-color: rgba(240, 240, 240, 75%)")#f0f0f0(240,240,240) #efebe7(239,235,231)
            font = label.font();
            font.setPointSize(12);
            label.setFont(font);
>>>>>>> 42af958c9063f6b4e055c52097ee0f877040ee9f
        
        #init new problem globals
        newProbCounter = 0
        newStartHolds = []
        newProbHolds = []                
        
    def saveNewProb(self):
        print('save')
        global newProbCounter
        global newProbHolds
        global newStartHolds
             
        newProblem = []
        if (self.leProblemName.text() == ''):
            QtWidgets.QMessageBox.warning(self, "Oh no!", "You must give a problem name")
        elif (newProbCounter < 2):
            QtWidgets.QMessageBox.warning(self, "Easy now!", "Must click at least 2 holds")
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
            self.resetAddProblemTab()
            self.populateProblemTable()
            QtWidgets.QMessageBox.warning(self, "Bon Effort!", "Well Done! New problem added!")
            self.tabWidget.setCurrentIndex(0)
                   
    def changeButtonColour(self):
        global newProbCounter
        global prevPb
        global newProbHolds
        
        #first check if button already clicked by loading colour
        colour = self.sender().palette().button().color().name()
        print(colour)
<<<<<<< HEAD
        if (colour != '#efebe7'): #is it NOT the default colour?
            #get hold number
            holdString = str(self.sender().objectName())
            holdNumber = int(re.search(r'\d+', holdString).group())
            self.sender().setStyleSheet("background-color: #efebe7")
            #delete this hold from problem/start holds
            if holdNumber in newProbHolds: newProbHolds.remove(holdNumber)
            if holdNumber in newStartHolds: newStartHolds.remove(holdNumber)
            #newProbCounter -= 1
=======
        if (colour != '#f0f0f0'): #is it NOT the default colour? #efebe7
            ####
            #### Do Nothing
            ####
            
            #get hold number
            #holdString = str(self.sender().objectName())
            #holdNumber = int(re.search(r'\d+', holdString).group())
            #set back to gray
            #self.sender().setStyleSheet("background-color: #f0f0f0")#efebe7
            #delete this hold from problem/start holds
            #if holdNumber in newProbHolds: newProbHolds.remove(holdNumber)
            #if holdNumber in newStartHolds: newStartHolds.remove(holdNumber)
>>>>>>> 42af958c9063f6b4e055c52097ee0f877040ee9f
            print("newProbHolds",newProbHolds)
        else:
            print(newProbCounter)
            if (newProbCounter == 0):
                self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                
            elif (newProbCounter == 1):
                self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                #save prev hold
                holdString = str(prevPb.objectName())
                holdNumber = int(re.search(r'\d+', holdString).group())
                newStartHolds.append(holdNumber)
                print(newStartHolds)
                prevPb.setStyleSheet("background-color: rgba(0, 128, 0, 75%)")#green
            elif (newProbCounter == 2):
                choice = QtWidgets.QMessageBox.question(self, 'Start Holds',
                                                    "Two start holds?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if (choice == QtWidgets.QMessageBox.Yes):
                    self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                    #save prev hold
                    holdString = str(prevPb.objectName())
                    newStartHolds.append(int(re.search(r'\d+', holdString).group()))
                    print(newStartHolds)
                    prevPb.setStyleSheet("background-color: rgba(0, 128, 0, 75%)")#green
                else:
                    newStartHolds.append(0)
                    holdString = str(prevPb.objectName())
                    newProbHolds.append(int(re.search(r'\d+', holdString).group()))
                    self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                    prevPb.setStyleSheet("background-color: rgba(0, 0, 255, 75%)")#blue
            elif (newProbCounter >= 3):
                holdString = str(prevPb.objectName())
                newProbHolds.append(int(re.search(r'\d+', holdString).group()))
                print('newProbHolds', newProbHolds)
                self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 75%)")#red
                prevPb.setStyleSheet("background-color: rgba(0, 0, 255, 75%)")#blue
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
            #for i in range(0,TOTAL_LED_COUNT,1):
             #   strip.setPixelColorRGB(i,int((255/TOTAL_LED_COUNT)*i), 0, 0)
<<<<<<< HEAD
            for j in range(256*1):
                for i in range(strip.numPixels()):
                    strip.setPixelColor(i, MyApp.wheel((i+j) & 255))
            strip.show()
            print('on')
        else:
            LEDState = 0
            for i in range(0,TOTAL_LED_COUNT,1):
                strip.setPixelColorRGB(i, 0, 0, 0)
                strip.show()
=======
            #for j in range(256*1):
            #    for i in range(strip.numPixels()):
            #        strip.setPixelColor(i, MyApp.wheel((i+j) & 255))
            #strip.show()
            print('on')
        else:
            LEDState = 0
            #for i in range(0,TOTAL_LED_COUNT,1):
            #    strip.setPixelColorRGB(i, 0, 0, 0)
            #    strip.show()
>>>>>>> 42af958c9063f6b4e055c52097ee0f877040ee9f
            print('off')
            
    def lightLEDs(startHolds, probHolds, finHolds):
        for i in range(0,TOTAL_LED_COUNT,1):
            strip.setPixelColorRGB(i, 0, 0, 0)
        for hold in probHolds:
            strip.setPixelColorRGB(hold-1, 0, 0, 50)
        for hold in startHolds:
            strip.setPixelColorRGB(hold-1, 0, 50, 0)
        for hold in finHolds:
            strip.setPixelColorRGB(hold-1, 50, 0, 0)
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
        return -1
            
    def lightProblem(self):
        global mirrorFlag
        
        mirrorFlag = 0
        items = self.tblProblems.selectedIndexes()[0]
        #print(problemsDB)
        #print(MyApp.find(problemsDB,(self.tblProblems.item((items.row()),0).text()))[0])
        #print(problemsDB.index(self.tblProblems.item((items.row()),0).text()))
        rowProb = MyApp.find(problemsDB,(self.tblProblems.item((items.row()),0).text()))[0]
        #(items.row()+1)
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
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    LEDState = 0
    strip = Adafruit_NeoPixel(TOTAL_LED_COUNT, 18, 800000, 5, False, 255)
    strip.begin()   #only call this once - each call creates new memory instance which
                    #eventually will crash program
    strip.setPixelColorRGB(TOTAL_LED_COUNT, 0, 0, 0)
    strip.show()
        
    sys.exit(app.exec_())
    
