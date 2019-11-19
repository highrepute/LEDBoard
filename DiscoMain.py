#############################################################
# check file path in const.py - comment for RasPi or windows#
#                                                           #
#############################################################
import sys
#fixes problem where screeninfo import throws as error
sys.path.append("/home/pi/.local/lib/python3.5/site-packages/screeninfo/")
from PyQt5 import QtWidgets, uic, QtCore#, QtGui
from PyQt5.QtCore import QTimer
#from PyQt5.QtWidgets import QSizePolicy
import re
import datetime
import time
import os

from collections import Counter

from problemFuncs import problemClass
from mirror import mirror
from usersFuncs import userClass
from logFuncs import logClass
from const import const
from dragButton import DragButton
from boardMaker import boardMaker

from qrangeslider import QRangeSlider

#load that configuration variables from config.ini
const.initConfigVariables()

if const.LINUX == 1:
    from screeninfo import get_monitors

if const.LINUX == 1:
    from neopixel import *

if const.LINUX == 1:
    m = get_monitors()
    if (m[0].width == 1024) & (m[0].height == 768):
        qtCreatorFile = "/home/pi/Desktop/LEDBoard-2/DiscoBoard1024x768.ui"
    else:
        qtCreatorFile = "/home/pi/Desktop/LEDBoard-2/DiscoBoard.ui"
else:
    if const.LINUX == 1:
        qtCreatorFile = "/home/pi/Desktop/LEDBoard-2/DiscoBoard.ui"
    else:
        qtCreatorFile = "DiscoBoard.ui"

#qtCreatorFile = "/home/pi/Desktop/LEDBoard-2/DiscoBoard.ui"
 
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
        global S2P2StartMatches        
        global S2P2ProbMatches
        global S2P2FinMatches        
        global toggleLEDFlag
        global startHolds
        global probHolds
        global finHolds        
        global S2PProbName
        global probName
        global sliderFlag
        global adminFlag
        global userFilter
        global tagsFilter
        global addButtonCount
        global firstMirrorHold
        global openExistingFlag
        
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        if const.LINUX == 1:
    		#find monitor resolution and position everything in the centre of screen       
            if (m[0].width == 1024) & (m[0].height == 768):
                moveTab = QtCore.QPoint(0, 0);
            else:
                moveTab = QtCore.QPoint((m[0].width - 1141)/2, ((m[0].height - 871)/2)+50);
        else:
            moveTab = QtCore.QPoint(0, 0);
        moveWallLogo = moveTab + QtCore.QPoint(800, -80);
        moveBoardLogo = moveTab + QtCore.QPoint(0, -80);
        self.tabWidget.move(moveTab)
        self.frmWallLogo.move(moveWallLogo)
        self.frmBoardLogo.move(moveBoardLogo)
        
        self.slider = QRangeSlider(self)
        self.slider.setMax(len(const.GRADES)+1)
        self.slider.setMin(0)
        self.slider.setRange(0,len(const.GRADES))
        self.QVBLayoutSlider.addWidget(self.slider)
        self.slider.endValueChanged.connect(self.sliderChange)
        self.slider.startValueChanged.connect(self.sliderChange)    
        
        #Connect buttons to functions
        #LED Board tab
        self.pbTestLEDs.clicked.connect(self.testLEDs)       
        self.tblProblems.selectionModel().selectionChanged.connect(self.lightProblem)
        self.pbMirror.clicked.connect(self.mirrorProb)
        self.pbLogin.clicked.connect(self.login)
        self.lePassword.returnPressed.connect(self.login)
        self.pbLogout.clicked.connect(self.logout)
        self.lbUsers.clicked.connect(self.updateLogLabel)
        self.pbLogProblem.clicked.connect(self.logProblem)
        self.pbSequence.clicked.connect(self.showSequence)
        self.pbShowTwoProbs.clicked.connect(self.showTwoProbs)
        self.pbAddTag.clicked.connect(self.addTag)
        
        #Add user tab
        self.pbAddNewUsers.clicked.connect(self.addNewUser)
        
        #admin tab
        self.pbAdminLogin.clicked.connect(self.adminLogin)
        self.leAdminPassword.returnPressed.connect(self.adminLogin)
        self.pbEditUsers.clicked.connect(self.editUsers)
        self.pbEditLogs.clicked.connect(self.editLogs)
        self.pbEditProblems.clicked.connect(self.editProblems)
        self.pbEditSave.clicked.connect(self.editSave)
        self.pbDeleteRow.clicked.connect(self.deleteRow)
        self.pbDefaultBoard.clicked.connect(self.setDefaultBoard)
        self.pbReset_1.clicked.connect(self.resetSoftware)
        self.pbReset_2.clicked.connect(self.resetSoftware)
        self.pbReset_3.clicked.connect(self.resetSoftware)
        self.pbReset_4.clicked.connect(self.resetSoftware)
        self.pbReset_5.clicked.connect(self.resetSoftware)
        self.pbReset_6.clicked.connect(self.resetSoftware)
        self.pbSetWallLogo.clicked.connect(self.setWallLogo)
        self.pbSetThemeColour.clicked.connect(self.setDefaultThemeColour)
            #edit problem tab
        #self.tabAdmin.currentChanged.connect(self.populateEditProblemList)
        self.lbEditProblemList.selectionModel().selectionChanged.connect(self.loadEditProblem)
        self.pbEditSaveProb.clicked.connect(self.saveEditProblem)
            #edit config tab
        self.pbConfigurationSave.clicked.connect(self.saveEditConfig)
        
        #filter tab
        self.pbFilterByUser.clicked.connect(self.filterByUser)
        self.lbUserFilter.selectionModel().selectionChanged.connect(self.filterUserChange)
        self.pbFilterByTags.clicked.connect(self.filterByTags)
        self.lbTagsFilter.selectionModel().selectionChanged.connect(self.filterTagsChange)        
        
        #changing tabs
        self.tabWidget.currentChanged.connect(self.stopShowSequence)
        self.tabWidget.currentChanged.connect(self.adminLogout)
        
        #Add problem tab
        self.pbDiscard.clicked.connect(self.resetAddProblemTab)
        self.pbSave.clicked.connect(self.saveNewProb)
        self.pbUndo.clicked.connect(self.undo)
        
        #Board Maker tab
        self.pbLoadImage.clicked.connect(self.loadFile)
        self.pbBuildBoard.clicked.connect(self.addButton)
        self.pbFinalise.clicked.connect(self.finalise)
        self.pbUndoAddHold.clicked.connect(self.undoAddHold)    
        self.pbSkipHold.clicked.connect(self.skipHold)
        self.pbReset.clicked.connect(self.resetSoftware)
        self.pbOpenExisting.clicked.connect(self.openExistingBoard)
        self.leHoldText.returnPressed.connect(self.changeHoldText)
        self.pbSetText.clicked.connect(self.changeHoldText)
        self.pbSaveAs.clicked.connect(self.saveBoardAs)
            
        #init globals
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
        S2P2StartMatches = []      
        S2P2ProbMatches = [] 
        S2P2FinMatches = []       
        S2PProbName = ""
        probName = ""
        sliderFlag = 0
        adminFlag = 0#0-logged out, 1-logged in, 2-editUsers, 3-editlogs, 4-editproblems
        userFilter = ""  
        tagsFilter = [""]
        addButtonCount = 1     
        firstMirrorHold = 0
        openExistingFlag = 0
        
        #default message
        self.lblInfo.setText(const.DEFAULTMSG)
        
        #initialise various bits
        self.initProblemTable()
        self.populateProblemTable()
        self.tabWidget.setCurrentIndex(0)#set startup tab
        self.populateFilterTab()
        self.populateComboBoxes()
        self.resetBoardMaker()
        self.initAdminTab(False)
        self.initialiseAddProblemTab()#takes ages!
        self.initSlider()
        self.initLogos()
        self.start_timer()
        self.saveAdmin = self.tabWidget.widget( 5 )
        self.saveBoardMaker = self.tabWidget.widget( 6 )
        self.tabWidget.removeTab( 6 )
        self.tabWidget.removeTab( 5 )
        self.initProbInfo()
        self.setThemeColour()
        
        #dispaly full screen
        self.showFullScreen()
        
        #make tables read only
        self.tblProblems.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblAscents.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblLogbook.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def setDefaultThemeColour(self):
        colour = QtWidgets.QColorDialog.getColor()
        #print(colour.name())
        const.setTHEMECOLOUR(colour.name())
        self.lblAdminState.setText("New theme colour set - press Apply to see new theme")

    def setThemeColour(self):
        self.tabWidget.setStyleSheet("QTabBar::tab:!selected { background: %s;}" % (const.THEMECOLOUR))
        #LED Board
        self.slider.handle.setStyleSheet('QRangeSlider #Span:active { background: %s;} QRangeSlider #Span { background: %s;}' % (const.THEMECOLOUR, const.THEMECOLOUR))
        self.tabWProbInfo.setStyleSheet("QTabBar::tab:!selected { background: %s;}" % (const.THEMECOLOUR))
        text = "QTextEdit, QListView, QLineEdit { selection-background-color: %s;} QPushButton:hover:!pressed { background-color: %s;} QTableView { selection-background-color: %s;} QHeaderView::section { background-color: %s;} QScrollBar::handle:vertical { background: %s;} QComboBox::item:selected{ background-color: %s;} QProgressBar::chunk { background-color: %s;}"
        self.frmStarsGrades.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR,  const.THEMECOLOUR))
        self.frmProblems.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))
        self.frmLogProb.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))
        self.frmProbButtons.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))
        self.frmLogin.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))
        #Filter by user
        self.frmFilter.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))
        #Add user
        self.frmAddUser.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))
        #Admin
        self.frmAdmin.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))
        #Board Maker
        self.frmBoardMaker.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))
        #Add Problem
        self.frmAddProb.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))
        #Logbook
        self.frmLogbook.setStyleSheet(text % (const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR, const.THEMECOLOUR))

    def hardClearDisplayProblem(self):
        #clears any lit holds - takes a long time!
        for num in range (1,const.TOTAL_LED_COUNT+1):
            widget_name = self.frmDispProb.findChild(QtWidgets.QPushButton, "pbi{}".format(num))
            if widget_name != None:
                widget_name.setStyleSheet("background: rgba(240, 240, 240, 10%); border: none;")#grey
            
    def clearDisplayProblem(self, startHolds, probHolds, finHolds):
        #clear any existing buttons
        for hold in startHolds:
            widget_name = self.frmDispProb.findChild(QtWidgets.QPushButton, "pbi{}".format(hold))
            if widget_name != None:
                widget_name.setStyleSheet("background: rgba(240, 240, 240, 10%); border: none;")#grey
        for hold in probHolds:
            widget_name = self.frmDispProb.findChild(QtWidgets.QPushButton, "pbi{}".format(hold))
            if widget_name != None:
                widget_name.setStyleSheet("background: rgba(240, 240, 240, 10%); border: none;")#grey
        for hold in finHolds:
            widget_name = self.frmDispProb.findChild(QtWidgets.QPushButton, "pbi{}".format(hold))
            if widget_name != None:
                widget_name.setStyleSheet("background: rgba(240, 240, 240, 10%); border: none;")#grey
        
    def setDisplayProblem(self, startHolds, probHolds, finHolds):
        #find holds and set colours
        for hold in startHolds:
            widget_name = self.frmDispProb.findChild(QtWidgets.QPushButton, "pbi{}".format(hold))
            if widget_name != None:
                widget_name.setStyleSheet("background: rgba(0, 128, 0, 30%); border: none;")#green
        for hold in probHolds:
            widget_name = self.frmDispProb.findChild(QtWidgets.QPushButton, "pbi{}".format(hold))
            if widget_name != None:
                widget_name.setStyleSheet("background: rgba(0, 0, 255, 30%); border: none;")#green
        for hold in finHolds:
            widget_name = self.frmDispProb.findChild(QtWidgets.QPushButton, "pbi{}".format(hold))
            if widget_name != None:
                widget_name.setStyleSheet("background: rgba(255, 0, 0, 30%); border: none;")#green
    
    def initProbInfo(self):
        #clear any existing buttons
        for num in range (1,const.TOTAL_LED_COUNT+1):#attempt to clear all holds
            widget_name = self.frmDispProb.findChild(QtWidgets.QPushButton, "pbi{}".format(num))
            if widget_name != None:
                widget_name.hide()
                widget_name.setParent(None)
        #load the individual buttons
        boardHolds = boardMaker.loadBoard(const.BOARDNAME)
        #print(boardHolds)
        if boardHolds != None:
            scaleHeight = self.frame_6.height()/self.frmDispProb.height()
            scaleWidth  = self.frame_6.width()/self.frmDispProb.width()
            #set background image of add problems frame and allow smaller buttons
            self.frmDispProb.setStyleSheet('#frmDispProb { border-image: url("' + const.IMAGEPATH + '")} QPushButton { min-height: 16px; min-width: 16px;}')
        
            for hold in boardHolds:
                #print(hold)
                button = QtWidgets.QPushButton("",self)
                button.resize(16,16)
                button.setParent(self.frmDispProb)
                button.move(int(hold[1])/scaleWidth,int(hold[2])/scaleHeight)
                button.setObjectName("pbi{}".format(hold[0]))
                button.show()
                button.setStyleSheet("background-color: rgba(240, 240, 240, 10%); border: none;")
                button = None

    def initLogos(self):
        if const.WALLLOGOPATH != None:
            self.frmWallLogo.setObjectName("frmWallLogo");
            self.frmWallLogo.setStyleSheet('#frmWallLogo { background-image: url("' + const.WALLLOGOPATH + '"); background-repeat: no-repeat; background-position: top right;}')
        if const.BOARDLOGOPATH != None:
            self.frmBoardLogo.setObjectName("frmBoardLogo");
            self.frmBoardLogo.setStyleSheet('#frmBoardLogo { background-image: url("' + const.BOARDLOGOPATH + '"); background-repeat: no-repeat; background-position: bottom left;}')
        
    def setWallLogo(self):
        imagePath = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '',"Image files (*.jpg *.png *.gif)")[0]
        #set background image of add problems frame
        self.frmWallLogo.setObjectName("frmWallLogo");
        self.frmWallLogo.setStyleSheet('QWidget#frmWallLogo { border-image: url("' + imagePath + '")}')
        const.setWALLLOGOPATH(imagePath)
        self.lblAdminState.setText("New logo set - press Apply to see new logo")
        
    def initSlider(self):
        self.lblMin.setText(str(const.GRADES[0]))
        self.lblMax.setText(str(const.GRADES[-1]))
        
    def resetSoftware(self):
        #disable so can't be pressed twice
        self.pbReset.setEnabled(False)
        self.pbReset_2.setEnabled(False)
        self.tabWidget.setCurrentIndex(0)#set startup tab 
        #load that configuration variables from config.ini
        const.initConfigVariables()
        #default message
        self.lblInfo.setText(const.DEFAULTMSG)
        #self.lblInfoAddProb.setText("Create new problems here - click a hold to begin")
        #initialise variout bits
        self.initProblemTable()
        self.populateProblemTable()
        self.hardClearDisplayProblem()
        self.setThemeColour()
        self.initProbInfo()
        self.populateFilterTab()
        #self.populateComboBoxes()
        self.resetBoardMaker()
        self.initAdminTab(False)
        self.initialiseAddProblemTab()
        self.start_timer()
        
    def initialiseAddProblemTab(self):
        #clear any existing buttons
        for num in range (1,const.TOTAL_LED_COUNT+1):#attempt to clear all holds
            widget_name = self.frame_6.findChild(QtWidgets.QPushButton, "pb{}".format(num))
            if widget_name != None:
                widget_name.hide()
                widget_name.setParent(None)
        #load the individual buttons
        boardHolds = boardMaker.loadBoard(const.BOARDNAME)
        #print(boardHolds)
        if boardHolds != None:
            #set background image of add problems frame
            self.frame_6.setObjectName("Frame_6");
            self.frame_6.setStyleSheet('QWidget#Frame_6 { border-image: url("' + const.IMAGEPATH + '")}')
        
            for hold in boardHolds:
                #print(hold)
                button = QtWidgets.QPushButton(hold[3],self)
                button.resize(31,31)
                button.setParent(self.frame_6)
                button.move(int(hold[1]),int(hold[2]))
                button.setObjectName("pb{}".format(hold[0]))
                button.clicked.connect(self.addHoldtoProb)
                button.show()
                button.setStyleSheet("background-color: rgba(240, 240, 240, 25%); border: none;")
                button = None
            self.lblInfoAddProb.setText("Create a new problem\nPress a hold to begin")
        else:
            #can't load a board - assume first use
            #const.setTOTAL_LED_COUNT(1000)#this allows test LED button to work on a new system - for max 1000 LEDs
            self.lblInfoAddProb.setText("Unable to load a board. Head over to The Board Maker to create one")
            self.lblInfo.setText("Unable to load a board. Head over to The Board Maker to create one")
        
    def saveBoardAs(self):
        if self.leSaveAsName.text() != "":
            saveAsPath = "/home/pi/Desktop/LEDBoard-2/" + self.leSaveAsName.text() + ".brd"
            boardMaker.saveBoardAs(self.lblBoardPath.text(), saveAsPath)
            self.leBoardName.setText(self.leSaveAsName.text())
            self.finalise()
            self.resetBoardMaker()
            self.lblBoardMakerInfo.setText("Board saved with new name - press Apply to load board")        
        else:
            self.lblBoardMakerInfo.setText("Enter a Board Name to Save As")

    def openExistingBoard(self):
        global addButtonCount
        global openExistingFlag
        
        self.resetBoardMaker()
        
        openExistingFlag = 1
        boardPath = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '',"Board files (*.brd)")[0]
        #print(boardPath)
        if boardPath != None:
            try:
                imagePath = str(boardMaker.getBoardImagePath(boardPath))
                #print(boardPath, ",", imagePath)
                boardHolds = boardMaker.loadBoard(boardPath)
            except:
                boardHolds = None
            if boardHolds != None:
                #set background image of frame
                self.frmBoard.setObjectName("frmBoard");
                self.frmBoard.setStyleSheet('QWidget#frmBoard { border-image: url("' + imagePath + '")}')
                                            
                #get the mirror table
                mirrorTable = boardMaker.getBoardMirrorTable(boardPath)
            
                #create the holds from the file
                for hold in boardHolds:                
                    w = QtWidgets.QWidget()
                    button = DragButton(str(hold[0]), w)
                    button.resize(31,31)
                    button.setParent(self.frmBoard)
                    button.move(int(hold[1]),int(hold[2]))
                    button.setObjectName("pbx{}".format(str(hold[0])))
                    button.setText(str(hold[3]))
                    if int(hold[0]) in (MyApp.column(mirrorTable,0)):
                        button.setStyleSheet("background: rgba(240, 240, 0, 50%); border: none;")
                    else:
                        button.setStyleSheet("background: rgba(240, 240, 240, 50%); border: none;")
                    button.clicked.connect(self.makeMirrorTable)
                    button.show()
                    addButtonCount += 1
                
                self.lblImagePath.setText(imagePath)
                self.lblBoardPath.setText(boardPath)
                boardName = os.path.splitext(os.path.basename(boardPath))[0]
                #print(boardName)
                self.leBoardName.setText(boardName)
                self.leBoardName.setEnabled(False)
                self.lblBoardMakerInfo.setText("Board loaded")
                self.pbFinalise.setEnabled(True)
                self.pbSkipHold.setEnabled(True)
                self.pbUndoAddHold.setEnabled(True)
                self.pbBuildBoard.setEnabled(True)
                self.pbSetText.setEnabled(True)
                self.pbSaveAs.show()
                self.leSaveAsName.show()
            else:
                self.resetBoardMaker()
                self.lblBoardMakerInfo.setText("Unable to load a board!")
        else:
            self.resetBoardMaker()
            self.lblBoardMakerInfo.setText("Unable to load a board!")    
    
    def resetBoardMaker(self):
        global addButtonCount
        global firstMirrorHold
        global openExistingFlag

        openExistingFlag = 0        
        firstMirrorHold = 0
        
        self.pbUndoAddHold.setEnabled(False)
        self.pbBuildBoard.setEnabled(False)
        self.pbFinalise.setEnabled(False)
        self.pbSkipHold.setEnabled(False)
        self.pbReset.setEnabled(False)
        self.pbSetText.setEnabled(False)
        self.leBoardName.setEnabled(False)
        self.pbSaveAs.hide()
        self.leSaveAsName.hide()
        self.leBoardName.setText("")
        self.leSaveAsName.setText("")
        self.lblBoardPath.setText("")
        self.lblImagePath.setText("")
        self.leHoldText.setText("")
        self.lblImagePath.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.lblBoardMakerInfo.setText("Load an existing board or an image to begin")
        self.frmBoard.setStyleSheet('QWidget#frmBoard { border-image: url("")}')
        self.lblImagePath.setText("Select an image")
        self.lblImagePath.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        #todo - clear all buttons
        for num in range (1,addButtonCount):
            widget_name = self.frmBoard.findChild(DragButton, "pbx{}".format(num))
            if widget_name != None:
                widget_name.setObjectName(None) 
                widget_name.hide()
                widget_name.setParent(None)
        addButtonCount = 1
        
    def makeMirrorTable(self):
        global firstMirrorHold
        if self.leBoardName.text() == "":
            QtWidgets.QMessageBox.warning(self, "No Board Name", "Please write in a Board Name before creating Mirrors")
        else:
            boardPath = "/home/pi/Desktop/LEDBoard-2/" + self.leBoardName.text() + ".brd"
            #get mirror table
            try:
                mirrorTable = boardMaker.getBoardMirrorTable(boardPath)
            except:
                mirrorTable = []
            #print(mirrorTable)
            if firstMirrorHold == 0:
                #get number of hold
                holdNumber = self.getHoldNumberFromButton(self.sender())
                #print(holdNumber)
                #if the mirror hold already exists then we are going to remove it
                if holdNumber in (MyApp.column(mirrorTable,0)):
                    #find the matching hold in mirror table and set that hold to grey
                    matchingIndex = (MyApp.column(mirrorTable,0)).index(holdNumber)
                    #print(matchingIndex)
                    self.sender().setStyleSheet("background: rgba(240, 240, 240, 50%); border: none;")#grey
                    mirrorToDel = mirrorTable[matchingIndex][1]#the mirrored hold - delete later
                    del mirrorTable[matchingIndex]#delete the entry to mirror table
                    #find the mirrored hold button, set grey and delete the entry to mirror table
                    widget_name = self.frmBoard.findChild(DragButton, "pbx{}".format(mirrorToDel))
                    if widget_name != None:
                        widget_name.setStyleSheet("background: rgba(240, 240, 240, 50%); border: none;")#grey
                    if mirrorToDel in (MyApp.column(mirrorTable,0)):
                        matchingIndex = (MyApp.column(mirrorTable,0)).index(mirrorToDel)
                        del mirrorTable[matchingIndex]
                    text = "Removed hold pairing -\n" + str(holdNumber) + ", " + str(mirrorToDel)
                    self.lblBoardMakerInfo.setText(text)
                else:#not already in mirror table - a new entry
                    #change hold to a colour - purple
                    self.sender().setStyleSheet("background: rgba(240, 0, 240, 50%); border: none;")
                    firstMirrorHold = self.getHoldNumberFromButton(self.sender())#save hold for when user clicks second hold
                    #print(firstMirrorHold)
                    text = "Click another hold to create pair"
                    self.lblBoardMakerInfo.setText(text)
            else:#firstMirrorHold > 1 - we are waiting for user to click second hold
                #change both holds to a new colour - yellow
                self.sender().setStyleSheet("background: rgba(240, 240, 0, 50%); border: none;")
                widget_name = self.frmBoard.findChild(DragButton, "pbx{}".format(firstMirrorHold))
                if widget_name != None:
                    widget_name.setStyleSheet("background: rgba(240, 240, 0, 50%); border: none;")        
                #create the new entry/ies to the mirror table
                secondMirrorHold = self.getHoldNumberFromButton(self.sender())
                #print(secondMirrorHold)
                if firstMirrorHold == secondMirrorHold:
                    newEntry = [firstMirrorHold, secondMirrorHold]
                    mirrorTable.append(newEntry)
                else:
                    newEntry = [firstMirrorHold, secondMirrorHold]
                    mirrorTable.append(newEntry)
                    newEntry = [secondMirrorHold, firstMirrorHold]
                    mirrorTable.append(newEntry)
                text = "Created hold pair -\n" + str(firstMirrorHold) + ", " + str(secondMirrorHold)
                self.lblBoardMakerInfo.setText(text)    
                #reset
                firstMirrorHold = 0
            #save the mirrorTable - what if no boardPath?    
            boardMaker.setBoardMirrorTable(boardPath, mirrorTable)
        
    def changeHoldText(self):
        global addButtonCount
        widget_name = self.frmBoard.findChild(DragButton, "pbx{}".format(addButtonCount-1))
        if widget_name != None:
            widget_name.setText(self.leHoldText.text())
        
    def skipHold(self):#skip a button for when LED is unused
        global addButtonCount
        addButtonCount += 1
        text = "LED - " + str(addButtonCount-1)
        self.lblBoardMakerInfo.setText(text)
        
    def undoAddHold(self):#undo last hold added or skipped
        global addButtonCount
        addButtonCount -= 1
        widget_name = self.frmBoard.findChild(DragButton, "pbx{}".format(addButtonCount))
        if widget_name != None:
            widget_name.hide()
            widget_name.setParent(None)
        text = "LED - " + str(addButtonCount-1)
        self.lblBoardMakerInfo.setText(text)
        if addButtonCount < 2:
            self.pbUndoAddHold.setEnabled(False)
            #self.pbBuildBoard.setEnabled(False)
            self.pbFinalise.setEnabled(False)
            text = "Click Add Hold to begin"
            self.lblBoardMakerInfo.setText(text)     
        
    def finalise(self):#save the new board layout
        global addButtonCount
        
        filename = self.leBoardName.text()
        if (filename != ""):
            filename = '/home/pi/Desktop/LEDBoard-2/' + filename + '.brd'
            const.setIMAGEPATH(self.lblImagePath.text())
            const.setBOARDNAME(filename)
            
            #find every hold button and append their position to a list (newBoard)
            newBoard = []
            for num in range (1,addButtonCount):
                widget_name = self.frmBoard.findChild(DragButton, "pbx{}".format(num))
                if widget_name != None:
                    newHold = [str(num), str(widget_name.pos().x()), str(widget_name.pos().y()), str(widget_name.text())]
                    newBoard.append(newHold)
            #save hold button locations list
            boardMaker.saveBoard(filename, newBoard, const.IMAGEPATH) 
            self.resetBoardMaker()
            self.pbReset.setEnabled(True)
            text = "Saved\n\nPress RESET to activate new board"
            self.lblBoardMakerInfo.setText(text)
        else:
            text = "Enter a name to save"
            self.lblBoardMakerInfo.setText(text)
        
    def addButton(self):
        global addButtonCount
        global openExistingFlag
        #print(addButtonCount)
        #light the LED that corrisponds to the button being added
        self.lightSingleLED(addButtonCount)
        #create a drag-able button - user places button over correct hold on image
        #correct hold is indicated by LED on board
        w = QtWidgets.QWidget()
        button = DragButton(str(addButtonCount), w)
        button.resize(31,31)
        button.setParent(self.frmBoard)
        button.move(addButtonCount,addButtonCount)
        button.setObjectName("pbx{}".format(addButtonCount))
        button.setStyleSheet("background: rgba(240, 240, 240, 50%); border: none;")
        button.clicked.connect(self.makeMirrorTable)
        button.show()
        addButtonCount += 1
        if addButtonCount > 1:
            self.pbUndoAddHold.setEnabled(True)
            self.pbBuildBoard.setEnabled(True)
            self.pbFinalise.setEnabled(True)
            self.pbSkipHold.setEnabled(True)
            if openExistingFlag != 1:
                self.leBoardName.setEnabled(True)
        text = "LED - " + str(addButtonCount-1)
        self.leHoldText.setText(str(addButtonCount-1))
        self.lblBoardMakerInfo.setText(text)
        
    def loadFile(self):#set the loaded image file as background for frame
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '',"Image files (*.jpg *.png *.gif)")[0]
        self.lblImagePath.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        #display the file path of the image selected - actually done this to use when saving the board (dodgy!)
        self.lblImagePath.setText(fname)
        #set image as background
        self.frmBoard.setStyleSheet('QWidget#frmBoard { border-image: url("' + fname + '")}')
        #enable the next buttons
        self.pbBuildBoard.setEnabled(True)     
        self.pbSkipHold.setEnabled(True)
        text = "Image loaded\nAdd Hold to begin"
        self.lblBoardMakerInfo.setText(text)
        
    def stopShowSequence(self):
        global showSequenceFlag
        if showSequenceFlag == 1:
            showSequenceFlag = 0
            text = "Show sequence stopped"
            self.lblInfo.setText(text)
        
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
        
        if userFilter == "":
            try:
                rowN = self.lbUserFilter.selectedIndexes()[0].row()
                user = self.lbUserFilter.item(rowN).text()
                userFilter = user
                self.pbFilterByUser.setStyleSheet("background-color: #fff;") 
                text = "Filtering by user - " + user
                self.lblUserFilter.setText(text)
                self.lblInfo.setText(text)                 
            except:
                userFilter = ""
                self.pbFilterByUser.setStyleSheet("background-color: #080;")#green
                self.lblUserFilter.setText("Select a user before filtering")
                self.lblInfo.setText("Not filtering by user")
        else:
            self.pbFilterByUser.setStyleSheet("background-color: #fff;")
            self.lblUserFilter.setText("Not filtering by user")
            self.lblInfo.setText("Not filtering by user")
            userFilter = ""
        self.populateProblemTable()
        
    def filterTagsChange(self):#list box selection change
        global tagsFilter 
        if tagsFilter != [""]:
            #rowN = self.lbTagsFilter.selectedIndexes()[0].row()
            #tags = self.lbTagsFilter.item(rowN).text()
            #tagsFilter = [tags]
            for item in self.lbTagsFilter.selectedIndexes():
                tagsFilter.append(self.lbTagsFilter.item(item.row()).text())            
            text = "Filtering by tag"# + tags
            self.lblTagsFilter.setText(text)
            self.lblInfo.setText(text)
            self.populateProblemTable()
            
    def addTag(self):
        if (self.tblProblems.selectedIndexes() != [])&(self.lbUsers.selectedIndexes() != []):
            rowN = self.tblProblems.selectedIndexes()[0].row()
            tag = self.cbTags.currentText()
            error = problemClass.addNewTag(rowN, tag)
            if error == 0:
                #reset combo box
                self.cbTags.setCurrentIndex(0)
                problem = self.tblProblems.item(rowN,0).text()
                text = tag + " added to  " + problem
            elif error == -1:
                text = "Can't add tag\nProblem has too many tags"
            else:
                text = "Can't add tag"
            self.lblInfo.setText(text)             
        
    def filterByTags(self):#push button
        global tagsFilter
        
        if tagsFilter == [""]:
            try:
                for item in self.lbTagsFilter.selectedIndexes():
                    tagsFilter.append(self.lbTagsFilter.item(item.row()).text())
                self.pbFilterByTags.setStyleSheet("background-color: #fff;") 
                text = "Filtering by tags"# + tags
                self.lblTagsFilter.setText(text)
                self.lblInfo.setText(text)                 
            except:
                tagsFilter = [""]
                self.pbFilterByTags.setStyleSheet("background-color: #080;")#green
                self.lblTagsFilter.setText("Select a tag before filtering")
                self.lblInfo.setText("Not filtering by tags")
        else:
            self.pbFilterByTags.setStyleSheet("background-color: #fff;")
            self.lblTagsFilter.setText("Not filtering by tags")
            self.lblInfo.setText("Not filtering by tags")
            tagsFilter = [""]
        self.populateProblemTable()        
    
    def populateComboBoxes(self):
        self.cbGrade.addItems(const.GRADES)
        self.cbGrade_2.addItems(const.GRADES)
        self.cbStars.addItems(const.STARS)
        self.cbStars_2.addItems(const.STARS)
        self.cbFootholdSet.addItems(const.FOOTHOLDSETS)
        self.cbEditStars.addItems(const.STARS)
        self.cbEditGrade.addItems(const.GRADES)
        self.cbEditFootholdSet.addItems(const.FOOTHOLDSETS)
        self.cbTags.addItems(const.TAGS)
        
    def populateFilterTab(self):
        try:
            #if a user is selected then keep them selected
            rowUser = self.lbUserFilter.selectedIndexes()[0].row()
            users = problemClass.getAllUsers()
            self.lbUserFilter.clear()
            if (len(users) > 0):
                self.lbUserFilter.addItems(users)
            self.lbUserFilter.setCurrentRow(rowUser)
        except:
            #populate listbox users and tags
            users = problemClass.getAllUsers()
            self.lbUserFilter.clear()
            if (len(users) > 0):
                self.lbUserFilter.addItems(users) 
        try:
            #if a tag is selected then keep them selected
            rowTags = self.lbTagsFilter.selectedIndexes()[0].row()
            tags = problemClass.getUniqueTags()
            self.lbTagsFilter.clear()
            if (len(tags) > 0):
                self.lbTagsFilter.addItems(tags)
            self.lbTagsFilter.setCurrentRow(rowTags)
        except:
            tags = problemClass.getUniqueTags()
            self.lbTagsFilter.clear()
            if (len(tags) > 0):
                self.lbTagsFilter.addItems(tags)                        
                
    def setDefaultBoard(self):
        boardPath = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '',"Board files (*.brd)")[0]
        const.setBOARDNAME(boardPath)
        self.lblDefaultBoard.setText(const.BOARDNAME)
        const.setIMAGEPATH(boardMaker.getBoardImagePath(boardPath))
        self.lblAdminState.setText("New Default Board set - press Apply to load new board")
        
    def deleteRow(self):
        model = self.tblEdit.model()
        indices = [self.tblEdit.selectedIndexes()[0]]
        #print("delete", indices)
        for index in sorted(indices):
            model.removeRow(index.row())
        
    def editSave(self):
        global adminFlag
        
        if adminFlag > 1:
            model = self.tblEdit.model()
            
            #need to add headers to the data - get from original data
            if adminFlag == 2:
                data = [userClass.readUsersFile()[0]]
            elif adminFlag == 3:
                data = [logClass.readLogFile()[0]]
            elif adminFlag == 4:
                data = [problemClass.readProblemFile()[0]]
            #get the data from the table
            for row in range(model.rowCount()):
              data.append([])
              for column in range(model.columnCount()):
                index = model.index(row, column)
                data[row+1].append(str(model.data(index)))
            #save the data to the correct file
            if adminFlag == 2:
                userClass.saveUsersFile(data)
                self.lblAdminState.setText("Saved users database - press Apply to load changes")
            elif adminFlag == 3:
                logClass.saveLogFile(data)
                self.lblAdminState.setText("Saved logbook database - press Apply to load changes")
            elif adminFlag == 4:
                problemClass.saveProblemFile(data)
                self.lblAdminState.setText("Saved problems database - press Apply to load changes")
            #set to logged in but no database loaded
            adminFlag = 1
            self.tblEdit.clear()
                
    def editProblems(self):
        global adminFlag
        
        if adminFlag > 0:
            adminFlag = 4
            problems = problemClass.readProblemFile()
            self.populateEditTable(problems)
            self.lblAdminState.setText("Loaded problems database - press Save to save changes")    
    
    def editLogs(self):
        global adminFlag
        
        if adminFlag > 0:
            adminFlag = 3
            log = logClass.readLogFile()
            self.populateEditTable(log)
            self.lblAdminState.setText("Loaded logbooks - press Save to save changes")
    
    def editUsers(self):
        global adminFlag
        
        if adminFlag > 0:
            adminFlag = 2
            users = userClass.readUsersFile()
            self.populateEditTable(users)
            self.lblAdminState.setText("Loaded users database - press Save to save changes")
            
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
                    
    def populateEditProblemList(self):
        self.lbEditProblemList.clear()
        problems = problemClass.getNameGradeStars()
        problems = MyApp.column(problems,0)
        del problems[0]
        if (len(problems) > 0):
                self.lbEditProblemList.addItems(problems)
        #self.lbEditInfo.setText('Select a problem and make changes')
                

    def loadEditProblem(self):
        try:
            rowN = self.lbEditProblemList.selectedIndexes()[0].row()+1
        except:
            rowN = -999
        if rowN != -999:
            problem = problemClass.getProblem(rowN)
            self.leEditProblemName.setText(problem[const.PROBNAMECOL])
            grade = int(problem[const.GRADECOL])
            stars = int(problem[const.STARSCOL])
            foothold = MyApp.find(const.FOOTHOLDSETS,problem[const.FOOTHOLDSETCOL])[0]
            if stars >= 0:
                self.cbEditStars.setCurrentIndex(stars)
            if grade >= 0:
                self.cbEditGrade.setCurrentIndex(grade)
            if foothold >= 0:
                self.cbEditFootholdSet.setCurrentIndex(foothold)
            self.tbEditComments.setText(problem[const.NOTESCOL])
            self.lbEditInfo.setText('Edit problem and press Save to save changes')

    def saveEditProblem(self):
        try:
            rowN = self.lbEditProblemList.selectedIndexes()[0].row()+1
        except:
            rowN = -999
        if rowN != -999:
            problem = problemClass.getProblem(rowN)
            problem[const.PROBNAMECOL] = self.leEditProblemName.text()
            problem[const.GRADECOL] = str(self.cbEditGrade.currentIndex())
            problem[const.STARSCOL] = str(self.cbEditStars.currentIndex())
            problem[const.FOOTHOLDSETCOL] = self.cbEditFootholdSet.currentText()
            comments = self.tbEditComments.toPlainText().replace('\n', ' ')
            comments = comments.replace(',', '-')
            problem[const.NOTESCOL] = comments
            #print('6',problem)
            problemClass.updateProblemFile(problem,rowN)
            self.lblAdminState.setText('Problem called - ' + problem[const.PROBNAMECOL] + ' - updated')
            self.lbEditInfo.setText('Problem called - ' + problem[const.PROBNAMECOL] + ' - updated\nPress Apply to reset and show changes')
            #self.leEditProblemName.clear()
            #self.cbEditStars.setCurrentIndex(0)
            #self.cbEditGrade.setCurrentIndex(0)
            #self.cbEditFootholdSet.setCurrentIndex(0)
            #self.tbEditComments.clear()
            #print('here')
            self.populateEditProblemList()
            #print('there')
            
    def populateEditConfig(self):
        self.cbAdminUser.clear()
        self.sbLEDBrightness.setValue(const.LED_VALUE)
        self.tbWelcomeMessage.setText(const.DEFAULTMSG)
        users = userClass.getUserNames()
        self.cbAdminUser.addItems(users)
        #set the dropdown to the current admin user
        index = MyApp.find(users, const.ADMIN)[0]
        self.cbAdminUser.setCurrentIndex(index)
        
    def saveEditConfig(self):
        #print('set new config')
        ##TODO - add in logout timeout field here
        const.setLED_VALUE(self.sbLEDBrightness.value())
        const.setDEFAULTMSG(self.tbWelcomeMessage.toPlainText())
        const.setADMIN(self.cbAdminUser.currentText())
        self.lblAdminState.setText('New config values saved - Press Appy to see changes')

    def adminLogout(self):
        global adminFlag
        adminFlag = 0
        self.lblAdminState.setText("Logged Out")
        self.tblEdit.clear()
        self.initAdminTab(False)
    
    def adminLogin(self):
        global adminFlag
        
        if adminFlag == 0:
            if self.leAdminPassword.text() == "admin":#CHANGE THIS!!!
                adminFlag = 1
                self.leAdminPassword.clear()
                self.lblAdminState.setText("Logged In")
                self.initAdminTab(True)
                self.populateEditProblemList()
                self.lbEditInfo.setText('Select a problem and make changes')
                self.populateEditConfig()
            else:
                self.lblInfo.setText("Oh no!\nI'm sorry your password is incorrect")
                
    def initAdminTab(self, loggedIn):
        self.tblEdit.setEnabled(loggedIn)
        self.pbEditUsers.setEnabled(loggedIn)
        self.pbEditLogs.setEnabled(loggedIn)
        self.pbEditProblems.setEnabled(loggedIn)
        self.pbDeleteRow.setEnabled(loggedIn)
        self.pbEditSave.setEnabled(loggedIn)
        self.lblDefaultBoard.setEnabled(loggedIn)
        self.lblDefaultBoard.setText(const.BOARDNAME)
        self.pbDefaultBoard.setEnabled(loggedIn)
        self.pbReset_1.setEnabled(loggedIn)
        self.pbReset_2.setEnabled(loggedIn)
        self.pbReset_3.setEnabled(loggedIn)
        self.pbReset_4.setEnabled(loggedIn)
        self.pbSetWallLogo.setEnabled(loggedIn)
        self.pbSetThemeColour.setEnabled(loggedIn)
        self.cbEditFootholdSet.setEnabled(loggedIn)
        self.cbEditGrade.setEnabled(loggedIn)
        self.cbEditStars.setEnabled(loggedIn)
        self.leEditProblemName.setEnabled(loggedIn)
        self.pbEditSaveProb.setEnabled(loggedIn)
        self.tbEditComments.setEnabled(loggedIn)
        self.tabAdmin.setEnabled(loggedIn)
    
    def sliderChange(self):
        global sliderFlag
        sliderFlag = 1
        
        start = const.GRADES[self.slider.getRange()[0]]
        end = const.GRADES[self.slider.getRange()[1] - 1]
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
        global S2P2StartMatches        
        global S2P2ProbMatches
        global S2P2FinMatches        
        #print("show two probs")
        
        if showTwoProbsFlag == 0:
            showTwoProbsFlag = 1
            text = "Showing two problems\n" + probName + "\nand\n" + S2PProbName
            self.lblInfo.setText(text)
            #change button colour to show "two prob" mode is active
            self.pbShowTwoProbs.setStyleSheet("background-color: rgba(0, 128, 0 100%)")#green
            #get holds for both problems
            self.lightTwoLEDs(startHolds, probHolds, finHolds, startHoldsS2P, probHoldsS2P, finHoldsS2P)
            #figure out any holds that are on both problems
            #these are handled in the quick timer
            S2PStartMatches = list(set(startHolds) & set(startHoldsS2P+probHoldsS2P+finHoldsS2P))     
            S2PProbMatches = list(set(probHolds) & set(startHoldsS2P+probHoldsS2P+finHoldsS2P))  
            S2PFinMatches = list(set(finHolds) & set(startHoldsS2P+probHoldsS2P+finHoldsS2P)) 
            S2P2StartMatches = list(set(startHoldsS2P) & set(startHolds+probHolds+finHolds))     
            S2P2ProbMatches = list(set(probHoldsS2P) & set(startHolds+probHolds+finHolds))  
            S2P2FinMatches = list(set(finHoldsS2P) & set(startHolds+probHolds+finHolds))            
        else:
            #turn off show two problem mode
            showTwoProbsFlag = 0
            self.pbShowTwoProbs.setStyleSheet("background-color: #fff;")
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
        #print('show2')
                   
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
            #get grade and stars - index of lookup table is value
            grade = MyApp.find(const.GRADES,self.cbGrade.currentText())[0]
            stars = MyApp.find(const.STARS,self.cbStars.currentText())[0]
            style = self.cbStyle.currentText()
            #create new log entry
            logProblem = [user,problem,grade,stars,date,comments,style]
            #print(logProblem)
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
        #print(rowN)
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
        realName = self.leAddRealName.text()
        email = self.leAddEmail.text()
        
        if (len(username) < 3):
            QtWidgets.QMessageBox.warning(self, "Easy now!", "Username must be at least 3 characters")
        elif (len(password) < 3):
            QtWidgets.QMessageBox.warning(self, "Easy now!", "Password must be at least 3 characters")
        else:
            text = "New user " + username + " added, you may now login"
            QtWidgets.QMessageBox.warning(self, "Easy now!", text)
            self.lblInfo.setText(text)
            userClass.addNewUser([username,password,date,realName,email])
            self.leAddUsername.clear()
            self.leAddPassword.clear()
            self.leAddRealName.clear()
            self.leAddEmail.clear()
            self.populateFilterTab()
              
    def start_timer(self):
        #timer with 1 minute timeout - auto logout
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.autoLogout())
        self.timer.start(60000)# 1 minute = 60000
        #timer with 250ms timeout - blinking LEDs in show2problem mode and showSequence
        self.timerQuick = QTimer()
        self.timerQuick.timeout.connect(lambda: self.timerQuickISR())
        self.timerQuick.start(300) # 400 ms     
        
    #log a user out
    def autoLogout(self):
        global usersLoggedIn
        #print("auto logout")
        for user,timeIn in usersLoggedIn:
            #if time since logged-in is 30mins (1800sec)
            #print(time.time() - timeIn)
            if ((time.time() - timeIn) > const.LOGOUTTIMEOUT):
                #log out that user
                index = MyApp.find(usersLoggedIn,user)[0]
                del usersLoggedIn[index]
                self.lbUsers.clear()
                if (len(usersLoggedIn) > 0):
                    self.lbUsers.addItems(MyApp.column(usersLoggedIn,0))
                self.updateLogLabel()
                text = user + " automatically logged out"
                self.lblInfo.setText(text)
                if user == const.ADMIN:
                    self.saveAdmin = self.tabWidget.widget( 5 )
                    self.saveBoardMaker = self.tabWidget.widget( 6 )
                    self.tabWidget.removeTab( 6 )
                    self.tabWidget.removeTab( 5 )
                    
    def timerQuickISR(self):
        global showSequenceFlag
        global showSequenceCounter
        global shownSequenceCount
        global S2PStartMatches        
        global S2PProbMatches
        global S2PFinMatches 
        global S2PStartMatches        
        global S2PProbMatches
        global S2PFinMatches        
        global sliderFlag
        
        if (showSequenceFlag == 1):
            #print('here')
            #get index of selected problem in table
            try:
                items = self.tblProblems.selectedIndexes()[0]
            except:
                items = -9999
            #print(items)
            if items != -9999:
                #get name of problem
                probName = self.tblProblems.item((items.row()),0).text()
                text = "Showing sequence of " + probName + "\n" + str(10 - shownSequenceCount)
                self.lblInfo.setText(text)
                if (shownSequenceCount < 10):
                    showSequenceCounter = showSequenceCounter + 1
                    if const.LINUX == 1:
                        for i in range(0,const.TOTAL_LED_COUNT,1):#turn all LED off
                            strip.setPixelColorRGB(i, 0, 0, 0)
                        for i in range(0,showSequenceCounter,1):#figure out where in sequence we are and light next LED
                            if (i < len(startHolds)):
                                hold = startHolds[i]
                                strip.setPixelColorRGB(hold-1, 0, const.LED_VALUE, 0)#green
                            elif (i < (len(startHolds)+len(probHolds))):
                                hold = probHolds[i-len(startHolds)]
                                strip.setPixelColorRGB(hold-1, 0, 0, const.LED_VALUE)#blue 
                            elif (i < (len(startHolds)+len(probHolds)+len(finHolds))):
                                hold = finHolds[i-len(startHolds)-len(probHolds)]
                                strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, 0)  #red                     
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
            MyApp.toggleLEDs(S2PStartMatches, S2PProbMatches, S2PFinMatches, S2P2StartMatches, S2P2ProbMatches, S2P2FinMatches)
        if (sliderFlag == 1):
            sliderFlag = 0
            self.populateProblemTable()
            start = self.slider.getRange()[0]
            end = self.slider.getRange()[1] - 1
            text = "Showing problems between grades - " + const.GRADES[start] + " and " + const.GRADES[end]
            self.lblInfo.setText(text)
                    
    #called when user does something - to stop auto logout
    def resetUserTimeIn(self,user):
        global usersLoggedIn
        index = MyApp.find(usersLoggedIn,user)[0]
        usersLoggedIn[index][1] = time.time()
        #print("time in",usersLoggedIn)
        
    #logout user selected in lbUsers listbox
    def logout(self):
        global usersLoggedIn
        if self.lbUsers.count() > 0:
            try:
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
                if user == const.ADMIN:
                    self.saveAdmin = self.tabWidget.widget( 5 )
                    self.saveBoardMaker = self.tabWidget.widget( 6 )
                    self.tabWidget.removeTab( 6 )
                    self.tabWidget.removeTab( 5 )
                self.lblLogbook.setText("Login and select a user to view logbook")
            except:
                self.lblInfo.setText("Select a user to logout")
        else:
            self.lblInfo.setText("No users to logout")    
    
    #returns a column from a list - list must be a matrix in dimensions
    def column(matrix, i):
        return [row[i] for row in matrix]
    
    def login(self):
        global usersLoggedIn
        
        usersDB = userClass.readUsersFile()
        login = userClass.checkPassword(usersDB, self.leUsername.text(), self.lePassword.text())
        if (login == -2):
            self.lblInfo.setText("Oh no!\nI'm sorry username not recognised")
        elif (login == -1):
            self.lblInfo.setText("Oh no!\nI'm sorry your password is incorrect")
        elif (login == 0):
            username = [self.leUsername.text()]
            #print(username)
            #check if already logged in
            if (MyApp.find(usersLoggedIn, username[0])[0] == -1):
                #QtWidgets.QMessageBox.warning(self, "Success!", "Well done, logged in!")
                text = username[0] +  " logged in"
                self.setThemeColour()
                self.lblInfo.setText(text)
                usersLoggedIn.append([username[0],time.time()])
                self.lbUsers.clear()
                self.lbUsers.addItems(MyApp.column(usersLoggedIn,0))
                #self.lbUsers.setCurrentRow(Count(usersLoggedIn))
                self.leUsername.clear()
                self.lePassword.clear()
                if username[0] == const.ADMIN:
                    self.tabWidget.insertTab( 5, self.saveAdmin, 'Admin' ) # restore
                    self.tabWidget.insertTab( 6, self.saveBoardMaker, 'Board Maker' ) # restore
                    #print("show tabs")
            else:
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
                            if j == 1:#convert grade for display
                                grade = const.GRADES[int(logbook[i][j])]
                                self.tblLogbook.setItem(i-1,j, QtWidgets.QTableWidgetItem(grade))    
                            elif j == 2:#convert stars for display
                                star = const.STARS[int(logbook[i][j])]
                                self.tblLogbook.setItem(i-1,j, QtWidgets.QTableWidgetItem(star))                    
                            else:
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
        
    def initProblemTable(self):
        problemList = problemClass.getGradeFilteredProblems(0, 0)
        self.tblProblems.setColumnCount(const.PROB_TBL_COL)
        self.tblProblems.horizontalHeader().setVisible(True)
        self.tblProblems.setHorizontalHeaderLabels(problemList[0])
        #set headers and column widths
        header = self.tblProblems.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
    
    def populateProblemTable(self):
        global userFilter
        global tagsFilter
        #populate problem list
        start = self.slider.getRange()[0]
        end = self.slider.getRange()[1] - 1
        #print(start, ",", end)
        problemList = problemClass.getGradeFilteredProblems(start, end)
        #print("FILTER1", problemList)
        problemList = problemClass.getUserFilteredProblems(problemList, userFilter)
        #print(tagsFilter)
        problemList = problemClass.getTagsFilteredProblems(problemList, tagsFilter)
        self.tblProblems.setSortingEnabled(False)
        self.tblProblems.setRowCount(len(problemList)-1)
        for i in range(1,len(problemList),1):
            for j in range(0,const.PROB_TBL_COL,1):
                if j == 1:#convert grade for display
                    grade = const.GRADES[int(problemList[i][j])]
                    #print(grade)
                    self.tblProblems.setItem(i-1,j, QtWidgets.QTableWidgetItem(grade))    
                elif j == 2:#convert stars for display
                    star = const.STARS[int(problemList[i][j])]
                    #print(star)
                    self.tblProblems.setItem(i-1,j, QtWidgets.QTableWidgetItem(star))                    
                else:
                    item = problemList[i][j]
                    #print(item)
                    self.tblProblems.setItem(i-1,j, QtWidgets.QTableWidgetItem(item))   
        self.tblProblems.setSortingEnabled(True)
        
    def resetAddProblemTab(self):
        global newProbCounter
        global newStartHolds
        global newProbHolds
        global undoCounter
        #reset button colours            
        for num in range (1,const.TOTAL_LED_COUNT+1):
            label = self.frame_6.findChild(QtWidgets.QPushButton, "pb{}".format(num))
            if label != None:
                label.setStyleSheet("background-color: rgba(240, 240, 240, 25%); border: none;")#f0f0f0(240,240,240) #efebe7(239,235,231)
                
        self.offLEDs()    
        #reset inputs
        self.leProblemName.clear()
        self.cbGrade_2.setCurrentIndex(0)
        self.cbStars_2.setCurrentIndex(0)
        self.cbFootholdSet.setCurrentIndex(0)
        self.tbComments.clear()
        
        self.lblInfoAddProb.setText("Create a new problem\nPress a hold to begin")
        
        #init new problem globals
        newProbCounter = 0
        newStartHolds = []
        newProbHolds = []
        undoCounter = 0
        
    def saveNewProb(self):
        #print('save')
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
            #append name, grade, stars & date
            probName = self.leProblemName.text()
            newProblem.append(probName)
            #print(const.GRADES, self.cbGrade_2.currentText())
            grade = MyApp.find(const.GRADES,self.cbGrade_2.currentText())[0]
            findResult = MyApp.find(const.GRADES,self.cbGrade_2.currentText())
            #print(findResult, grade)
            stars = MyApp.find(const.STARS,self.cbStars_2.currentText())[0]
            footholdSet = self.cbFootholdSet.currentText()
            newProblem.append(grade)
            newProblem.append(stars)
            now = datetime.datetime.now()
            newProblem.append(now.strftime("%Y-%m-%d"))        
            #append user & comment
            newProblem.append(user)   
            comments = self.tbComments.toPlainText().replace('\n', ' ')
            comments = comments.replace(',', '-')
            newProblem.append(comments)
            #append the selected foothold set
            newProblem.append(footholdSet)
            #append start holds
            newProblem.append(str(newStartHolds[0]))
            if (len(newStartHolds) == 2):
                newProblem.append(str(newStartHolds[1]))
            else:
                newProblem.append('')
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
            #save to file
            problemClass.addNewProb(newProblem)
            self.resetAddProblemTab()
            self.populateProblemTable()
            self.populateFilterTab()
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
            prevPb.setStyleSheet("background-color: rgba(240, 240, 240, 25%); border: none;")
            self.setLEDbyButton(prevPb,"off")
            newProbCounter -= 1
            undoCounter = 1
            #set prevPb (previously pushed button) back one
            #and delete last entry to new problem array (start or problem holds)
            if (len(newProbHolds) != 0):
                #prevPb = getattr(self, 'pb{}'.format(newProbHolds[-1]))
                prevPb = self.frame_6.findChild(QtWidgets.QPushButton, "pb{}".format(newProbHolds[-1]))
                del(newProbHolds[-1])
            elif (len(newStartHolds) != 0):
                #prevPb = getattr(self, 'pb{}'.format(newStartHolds[-1]))
                prevPb = self.frame_6.findChild(QtWidgets.QPushButton, "pb{}".format(newStartHolds[-1]))
                del(newStartHolds[-1])
            if (newProbCounter > 2):    
                self.lblInfoAddProb.setText("Removed last hold\nAdd another hold or Save problem")
            else:
                self.lblInfoAddProb.setText("Removed last hold\nAdd another hold")

        
    #extracts the number from the button pressed and uses it to light the correct LED
    def setLEDbyButton(self,button,colour):
        holdNumber = self.getHoldNumberFromButton(button)
        #print("hold Number -", holdNumber, "colour -", colour)
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
        global mirrorFlag
        global showTwoProbsFlag
        
        undoCounter = 0
        self.stopShowSequence()              
        mirrorFlag = 0
        if showTwoProbsFlag == 1:
            self.showTwoProbs()
        
        #first check if button already clicked by loading colour
        colour = self.sender().palette().button().color().name()
        if (colour != '#f0f0f0'): #is it NOT the default colour? #efebe7
            QtWidgets.QMessageBox.warning(self, "Hold Added", "To remove hold use the Undo button")      
        else:
            if (newProbCounter == 0):
                self.offLEDs()
                self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 50%); border: none;")#red
                self.setLEDbyButton(self.sender(),"red")
            elif (newProbCounter == 1):
                self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 50%); border: none;")#red
                self.setLEDbyButton(self.sender(),"red")
                #when a button is pressed we save the previous button to the new problem and change colour of previous button
                newStartHolds.append(self.getHoldNumberFromButton(prevPb))
                prevPb.setStyleSheet("background-color: rgba(0, 128, 0, 50%); border: none;")#green
                self.setLEDbyButton(prevPb,"green")
            elif (newProbCounter == 2):
                choice = QtWidgets.QMessageBox.question(self, 'Start Holds',
                                                    "Two start holds?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if (choice == QtWidgets.QMessageBox.Yes):
                    #two start holds
                    self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 50%); border: none;")#red
                    self.setLEDbyButton(self.sender(),"red")
                    newStartHolds.append(self.getHoldNumberFromButton(prevPb))
                    #print("start", newStartHolds)
                    prevPb.setStyleSheet("background-color: rgba(0, 128, 0, 50%); border: none;")#green
                    self.setLEDbyButton(prevPb,"green")
                else:
                    #only one start hold
                    self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 50%); border: none;")#red
                    self.setLEDbyButton(self.sender(),"red")
                    newProbHolds.append(self.getHoldNumberFromButton(prevPb))
                    prevPb.setStyleSheet("background-color: rgba(0, 0, 255, 25%); border: none;")#blue
                    self.setLEDbyButton(prevPb,"blue")
            elif (newProbCounter >= 3):
                #append hold to newProbHold array and change button and LED colours
                self.sender().setStyleSheet("background-color: rgba(255, 0, 0, 50%); border: none;")#red
                self.setLEDbyButton(self.sender(),"red")
                newProbHolds.append(self.getHoldNumberFromButton(prevPb))
                prevPb.setStyleSheet("background-color: rgba(0, 0, 255, 25%); border: none;")#blue
                self.setLEDbyButton(prevPb,"blue")
            newProbCounter += 1
            prevPb = self.sender()
        if (newProbCounter > 2):    
            self.lblInfoAddProb.setText("Added a hold\nAdd another hold or Save problem")
        else:
            self.lblInfoAddProb.setText("Added a hold\nAdd another hold")
    
    #this is for the rainbow effect for testLEDs    
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
        global showTwoProbsFlag
        
        text = "Test LEDs button pressed\nAll LEDs lit"
        self.lblInfo.setText(text)
        self.stopShowSequence()
        if showTwoProbsFlag == 1:
            self.showTwoProbs()     
        if (LEDState == 0):
            LEDState = 1
            if const.LINUX == 1:
#                for i in range(0,500,1):
#                    strip.setPixelColorRGB(i,int((255/100)*i), 0, 0)
#                for j in range(256*1):
                #500 is a guess at the max number of LEDs any system might have
                for i in range(const.TOTAL_LED_COUNT):
                    strip.setPixelColor(i, MyApp.wheel((i) & 255))
                strip.show()
        else:
            LEDState = 0
            self.offLEDs()
    
    #turn all LEDs off        
    def offLEDs(self):
        if const.LINUX == 1:
            for i in range(0,const.TOTAL_LED_COUNT,1):
                strip.setPixelColorRGB(i, 0, 0, 0)
            strip.show()
            
    def lightSingleLED(self, hold):
         if const.LINUX == 1:
            for i in range(0,const.TOTAL_LED_COUNT,1):
                strip.setPixelColorRGB(i, 0, 0, 0)
            strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, const.LED_VALUE)
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
        
    def lightTwoLEDs(self, startHolds, probHolds, finHolds, startHolds2, probHolds2, finHolds2):
        
        self.stopShowSequence()        
        if const.LINUX == 1:
            for i in range(0,const.TOTAL_LED_COUNT,1):
                strip.setPixelColorRGB(i, 0, 0, 0)
            for hold in startHolds:
                strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, int(const.LED_VALUE/2))#pink
            for hold in probHolds:
                strip.setPixelColorRGB(hold-1, const.LED_VALUE, const.LED_VALUE, 0)#yellow
            for hold in finHolds:
                strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, 0)#red 
            for hold in startHolds2:
                strip.setPixelColorRGB(hold-1, 0, const.LED_VALUE, int(const.LED_VALUE/2))#green-ish
            for hold in probHolds2:
                strip.setPixelColorRGB(hold-1, 0, int(const.LED_VALUE/2), const.LED_VALUE)#blue/teal
            for hold in finHolds2:
                strip.setPixelColorRGB(hold-1, int(const.LED_VALUE/2), 0,const.LED_VALUE )#purple
            strip.show()
    
    #used in show two prob mode to toggle colour of an LED that is on both problems
    def toggleLEDs(startHolds, probHolds, finHolds, startHolds2, probHolds2, finHolds2):
        global toggleLEDFlag
        
        if const.LINUX == 1:
            if toggleLEDFlag == 0:
                toggleLEDFlag = 1
                #print("toggle 0")
                for hold in startHolds2:
                    strip.setPixelColorRGB(hold-1, 0, 0, 0)
                for hold in probHolds2:
                    strip.setPixelColorRGB(hold-1, 0, 0, 0)
                for hold in finHolds2:
                    strip.setPixelColorRGB(hold-1, 0, 0, 0)                
                for hold in startHolds:
                    strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, int(const.LED_VALUE/2))#pink
                for hold in probHolds:
                    strip.setPixelColorRGB(hold-1, const.LED_VALUE, const.LED_VALUE, 0)#yellow
                for hold in finHolds:
                    strip.setPixelColorRGB(hold-1, const.LED_VALUE, 0, 0)#red                               
            elif toggleLEDFlag == 1:
                toggleLEDFlag = 0
                #print("toggle 1")
                for hold in startHolds:
                    strip.setPixelColorRGB(hold-1, 0, 0, 0)
                for hold in probHolds:
                    strip.setPixelColorRGB(hold-1, 0, 0, 0)
                for hold in finHolds:
                    strip.setPixelColorRGB(hold-1, 0, 0, 0)                
                for hold in startHolds2:
                    strip.setPixelColorRGB(hold-1, 0, const.LED_VALUE, int(const.LED_VALUE/2))#green-ish
                for hold in probHolds2:
                    strip.setPixelColorRGB(hold-1, 0, int(const.LED_VALUE/2), const.LED_VALUE)#blue/teal
                for hold in finHolds2:
                    strip.setPixelColorRGB(hold-1, int(const.LED_VALUE/2), 0,const.LED_VALUE )#purple                     
            strip.show()
    
    #find item elem in list l    
    def find(l, elem):
        for row, i in enumerate(l):
            try:
                #print(i)
                column = i.index(elem)
            except ValueError:
                continue
            if (column  == 0):
                return row, column
        return [-1,-1]
    
    #checks the grade and stars of the selected problem and updates the log problem dropdowns
    def updateLogProblemDropdowns(self,rowProb):
        problemsDB = problemClass.readProblemFile()
        grade = int(problemsDB[rowProb][const.GRADECOL])
        stars = int(problemsDB[rowProb][const.STARSCOL])
        if stars >= 0:
            self.cbStars.setCurrentIndex(stars)
        if grade >= 0:
            self.cbGrade.setCurrentIndex(grade)   
    
    def updateProbInfo(self,rowProb):
        problemsDB = problemClass.readProblemFile()
        probName = problemsDB[rowProb][const.PROBNAMECOL]
        grade = const.GRADES[int(problemsDB[rowProb][const.GRADECOL])]
        stars = const.STARS[int(problemsDB[rowProb][const.STARSCOL])]
        footholdSet = problemsDB[rowProb][const.FOOTHOLDSETCOL]
        date = problemsDB[rowProb][const.DATECOL]
        setter = problemClass.getUser(rowProb)
        notes = problemClass.getNotes(rowProb)
        
        tags = "TAGS: "
        for i in range(10):
            if problemsDB[rowProb][const.TAGSCOL+i] != "":
                tags += problemsDB[rowProb][const.TAGSCOL+i]
                tags += ", "
        
        formatName = "<span style=\" font-size:14pt; font-weight:400; color:#000;\" >"
        formatGrade = "<span style=\" font-size:14pt; font-weight:400; color:#ca3;\" >"
        formatGray = "<span style=\" font-size:12pt; font-weight:300; color:#333;\" >"
        formatInfo = "<span style=\" font-size:13pt; font-weight:300; color:#000;\" >"
        closeSpan = "</span>\n"
        
        infoText = formatName + probName + "&nbsp;&nbsp;&nbsp;&nbsp;" + closeSpan + formatGrade + grade + "&nbsp;" + stars + closeSpan + formatGray + "<br>Date added:&nbsp;&nbsp;" + closeSpan + formatInfo + date + closeSpan + formatGray + "<br>Set by:&emsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + closeSpan + formatInfo + setter + closeSpan + formatGray + "<br>Footholds:&nbsp;&nbsp;&nbsp;&nbsp;" + closeSpan + formatInfo + footholdSet + closeSpan + formatGray + "<br>Comments:&nbsp;&nbsp;" + closeSpan + formatInfo + notes + "<br>" + tags + closeSpan
        
        #get and present star votes
        starVotes = logClass.getStarVotes(probName)
        stars = []
        stars.append(starVotes.count('3'))
        stars.append(starVotes.count('2'))
        stars.append(starVotes.count('1'))
        stars.append(starVotes.count('0'))
        barRange = max(stars)
        if (barRange < 1):
            barRange = 1
        self.barStar3.setRange(0,barRange)
        self.barStar2.setRange(0,barRange)
        self.barStar1.setRange(0,barRange)
        self.barStar0.setRange(0,barRange)
        self.barStar3.setValue(starVotes.count('3'))
        self.barStar2.setValue(starVotes.count('2'))
        self.barStar1.setValue(starVotes.count('1'))
        self.barStar0.setValue(starVotes.count('0'))
        
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
                label.setText(const.GRADES[int(grade)])
                bar.setValue(count)
                
        #get problem ascents & display
        ascents = logClass.getProblemAscents(probName)
        self.populateAscents(ascents)
        
        #display problem info
        self.tbProblemInfo.setText(infoText)
 
    #populate table of ascents       
    def populateAscents(self, ascents):       
        self.tblAscents.setRowCount(len(ascents)-1)
        self.tblAscents.setColumnCount(6)
        self.tblAscents.horizontalHeader().setVisible(True)
        self.tblAscents.setHorizontalHeaderLabels(ascents[0])
        for i in range(1,len(ascents),1):
            for j in range(0,6,1):
                    #self.tblAscents.setItem(i-1,j, QtWidgets.QTableWidgetItem(ascents[i][j]))
                if j == 1:#convert grade for display
                    grade = const.GRADES[int(ascents[i][j])]
                    self.tblAscents.setItem(i-1,j, QtWidgets.QTableWidgetItem(grade))    
                elif j == 2:#convert stars for display
                    star = const.STARS[int(ascents[i][j])]
                    self.tblAscents.setItem(i-1,j, QtWidgets.QTableWidgetItem(star))                    
                else:
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
            probName = self.tblProblems.item((items.row()),const.PROBNAMECOL).text()        
            #find problem in problemDB using problem name from selected row
            rowProb = MyApp.find(problemsDB,probName)[0]
        except:
            rowProb = -1
        return rowProb
            
    def lightProblem(self):
        global mirrorFlag
        global startHoldsS2P
        global probHoldsS2P
        global finHoldsS2P
        global startHolds
        global probHolds
        global finHolds
        global showTwoProbsFlag
        global probName
        
        self.stopShowSequence()              
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
        self.clearDisplayProblem(startHoldsS2P, probHoldsS2P, finHoldsS2P)
        self.setDisplayProblem(startHolds, probHolds, finHolds)
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
    
