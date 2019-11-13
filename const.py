
import configparser
import ast

class const:
    PROBNAMECOL = 0
    GRADECOL = 1
    STARSCOL = 2
    DATECOL = 3
    USERCOL = 4
    NOTESCOL = 5
    FOOTHOLDSETCOL = 6
    TAGSCOL = 7
    STARTHOLDSINDEX = 17
    FINHOLDSINDEX = 19  
    NOHOLDSINDEX = 21
    HOLDSINDEX = 22
    #initialise these to some default values
    LINUX = 0
    LED_VALUE = 50
    DEFAULTMSG = "Welcome to the Board of High Repute"
    GRADES = ['6a', '6a+', '6b', '6b+', '6c', '6c+', '7a']
    STARS = ['-', '*', '**', '***']
    TOTAL_LED_COUNT = 126
    IMAGEPATH = None
    BOARDNAME = None
    PROB_TBL_COL = 5
    ADMIN = None
    WALLLOGOPATH = None
    BOARDLOGOPATH = None
    THEMECOLOUR = "#fd4"
    FOOTHOLDSETS = ['Standard']
    USERSPATH = None
    LOGPATH = None
    PROBPATH = None
    LOGOUTTIMEOUT = 1800
    
    def initConfigVariables():
        const.LINUX = int(const.getLINUX())
        const.BOARDNAME = str(const.getBOARDNAME())
        const.LED_VALUE = int(const.getLED_VALUE())
        const.DEFAULTMSG = str(const.getDEFAULTMSG())
        const.GRADES = const.getGRADES()
        const.STARS = const.getSTARS()
        const.TOTAL_LED_COUNT = int(const.getTOTAL_LED_COUNT())
        const.IMAGEPATH = str(const.getIMAGEPATH())
        const.BOARDNAME = str(const.getBOARDNAME())
        const.ADMIN = str(const.getADMIN())
        const.WALLLOGOPATH = str(const.getWALLLOGOPATH())
        const.BOARDLOGOPATH = str(const.getBOARDLOGOPATH())
        const.THEMECOLOUR = str(const.getTHEMECOLOUR())
        const.FOOTHOLDSETS = const.getFOOTHOLDSETS()
        const.USERSPATH = str(const.getUSERSPATH())
        const.LOGPATH = str(const.getLOGPATH())
        const.PROBPATH = str(const.getPROBPATH())
        const.LOGOUTTIMEOUT = int(const.getLOGOUTTIMEOUT())
    
    def loadConfig():
        config = configparser.ConfigParser()
        config.optionxform = str
        #config.read('/home/pi/Desktop/LEDBoard-2/config.ini') #RasPi
        config.read('config.ini') #Windows
        return config
    
    def writeConfig(config):
        with open('config.ini', 'w') as configfile: #Windows
        #with open('/home/pi/Desktop/LEDBoard-2/config.ini', 'w') as configfile: #RasPi
            config.write(configfile)

    def getLINUX():
        config = const.loadConfig()
        return int(config.get('DEFAULT', 'LINUX'))
    
    def setLINUX(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'LINUX', str(value))
        const.writeConfig(config)
        const.LINUX = value
        
    def getLOGOUTTIMEOUT():
        config = const.loadConfig()
        return int(config.get('DEFAULT', 'LOGOUTTIMEOUT'))
    
    def setLOGOUTTIMEOUT(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'LOGOUTTIMEOUT', str(value))
        const.writeConfig(config)
        const.LOGOUTTIMEOUT = value
        
    def getUSERSPATH():
        config = const.loadConfig()
        return config.get('PATHS', 'USERSPATH')

    def getLOGPATH():
        config = const.loadConfig()
        return config.get('PATHS', 'LOGPATH')

    def getPROBPATH():
        config = const.loadConfig()
        return config.get('PATHS', 'PROBPATH')        
        
    def getBOARDNAME():
        config = const.loadConfig()
        return str(config.get('BOARD', 'BOARDNAME'))
    
    def setBOARDNAME(value):
        config = const.loadConfig()
        config.set('BOARD', 'BOARDNAME', str(value))
        const.writeConfig(config)
        const.BOARDNAME = value   

    def getTOTAL_LED_COUNT():
        config = const.loadConfig()
        return int(config.get('BOARD', 'TOTALLEDCOUNT'))
    
    def setTOTAL_LED_COUNT(value):
        config = const.loadConfig()
        config.set('BOARD', 'TOTALLEDCOUNT', str(value))
        const.writeConfig(config)
        const.TOTAL_LED_COUNT = value
    
    def getLED_VALUE():
        config = const.loadConfig()
        return int(config.get('DEFAULT', 'LEDBRIGHTNESS'))   
    
    def setLED_VALUE(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'LEDBRIGHTNESS', str(value))
        const.writeConfig(config)
        const.LED_VALUE = value
        
    def getDEFAULTMSG():
        config = const.loadConfig()
        return str(config.get('DEFAULT', 'DEFAULTMSG')) 
    
    def setDEFAULTMSG(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'DEFAULTMSG', str(value))
        const.writeConfig(config)
        const.DEFAULTMSG = value

    def getGRADES():
        config = const.loadConfig()
        return ast.literal_eval(config.get('DEFAULT', 'GRADES'))
    
    def setGRADES(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'GRADES', value)
        const.writeConfig(config)    
        const.GRADES = value

    def getSTARS():
        config = const.loadConfig()
        return ast.literal_eval(config.get('DEFAULT', 'STARS'))
    
    def setSTARS(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'STARS', value)
        const.writeConfig(config)    
        const.STARS = value
    
    def getIMAGEPATH():
        config = const.loadConfig()
        return config.get('BOARD', 'IMAGEPATH')
    
    def setIMAGEPATH(value):
        config = const.loadConfig()
        config.set('BOARD', 'IMAGEPATH', str(value))
        const.writeConfig(config)
        const.IMAGEPATH = value
        
    def getWALLLOGOPATH():
        config = const.loadConfig()
        return config.get('BOARD', 'WALLLOGOPATH')
    
    def setWALLLOGOPATH(value):
        config = const.loadConfig()
        config.set('BOARD', 'WALLLOGOPATH', str(value))
        const.writeConfig(config)
        const.WALLLOGOPATH = value
        
    def getBOARDLOGOPATH():
        config = const.loadConfig()
        return config.get('BOARD', 'BOARDLOGOPATH')
    
    def setBOARDLOGOPATH(value):
        config = const.loadConfig()
        config.set('BOARD', 'BOARDLOGOPATH', str(value))
        const.writeConfig(config)
        const.BOARDLOGOPATH = value

    def getTHEMECOLOUR():
        config = const.loadConfig()
        return config.get('DEFAULT', 'THEMECOLOUR')
    
    def setTHEMECOLOUR(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'THEMECOLOUR', str(value))
        const.writeConfig(config)
        const.THEMECOLOUR = value         

    def getADMIN():
        config = const.loadConfig()
        return str(config.get('DEFAULT', 'ADMIN'))
    
    def setADMIN(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'ADMIN', str(value))
        const.writeConfig(config)
        const.LINUX = value        

    def getFOOTHOLDSETS():
        config = const.loadConfig()
        return ast.literal_eval(config.get('BOARD', 'FOOTHOLDSETS'))
    
    def setFOOTHOLDSETS(value):
        config = const.loadConfig()
        config.set('BOARD', 'FOOTHOLDSETS', value)
        const.writeConfig(config)    
        const.FOOTHOLDSETS = value        
        
#print(const.LINUX)
#const.initConfigVariables()
#print(const.LOGOUTTIMEOUT)
#print(const.FOOTHOLDSETS)
#grades = ['6a', '6a+', '6b', '6b+', '6c', '6c+', '7a']
#print(str(const.GRADES))
#print(const.LOGPATH)
#const.setIMAGEPATH("C:/Users/James.Jacobs/Desktop/Temp/LED/20180411_210921_2.jpg")
#const.setLINUX("1")
#print(const.IMAGEPATH)
#print(const.ADMIN)        
