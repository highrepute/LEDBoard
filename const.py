
import configparser
import ast
import os

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
    TAGS = ['Tags','Tags']
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
    PROJECTSPATH = None
    LOGOUTTIMEOUT = 1800
    AUTOLOGIN = []
    
    def ensureDefaultFiles():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'config.ini')

        if not os.path.exists(config_path):
            config = configparser.ConfigParser()
            config.optionxform = str
            config['DEFAULT'] = {
                'LINUX': '1',
                'LEDBRIGHTNESS': '50',
                'DEFAULTMSG': 'Welcome to the Board',
                'BOARDLOGOPATH': '',
                'GRADES': "['6a', '6a+', '6b', '6b+', '6c', '6c+', '7a']",
                'STARS': "['-', '*', '**', '***']",
                'ADMIN': 'James',
                'THEMECOLOUR': '#fd4',
                'LOGOUTTIMEOUT': '1800',
                'AUTOLOGIN': "['James']",
            }
            config['BOARD'] = {
                'TOTALLEDCOUNT': '0',
                'IMAGEPATH': '',
                'BOARDNAME': '',
                'WALLLOGOPATH': '',
                'FOOTHOLDSETS': "['Standard']",
                'TAGS': "['Tags']",
                'BOARDLOGOPATH': '',
            }
            config['PATHS'] = {
                'USERSPATH': os.path.join(script_dir, 'users.csv'),
                'LOGPATH': os.path.join(script_dir, 'logs.csv'),
                'PROBPATH': os.path.join(script_dir, 'problems.csv'),
                'PROJECTSPATH': os.path.join(script_dir, 'projects.csv'),
            }
            with open(config_path, 'w') as f:
                config.write(f)

        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(config_path)

        import datetime
        today = datetime.date.today().strftime('%d/%m/%Y')
        csv_defaults = {
            config.get('PATHS', 'USERSPATH'):
                f'Username,Password,Date Reg, Real name, Email\nJames,123,{today},,\n',
            config.get('PATHS', 'LOGPATH'):
                'Username,Problem,Grade,Stars,Ascent Date,Comments,Attempts\n',
            config.get('PATHS', 'PROBPATH'):
                'Name,Grade,Stars,Added,User,Comments,Foothold,tag0,tag1,tag2,tag3,tag4,tag5,tag6,tag7,tag8,tag9,Start1,Start2,Fin1,Fin2,HoldNo\n',
            config.get('PATHS', 'PROJECTSPATH'):
                'Username,ProblemName\n',
        }
        for path, header in csv_defaults.items():
            if not os.path.exists(path):
                with open(path, 'w', newline='') as f:
                    f.write(header)

    def initConfigVariables():
        const.ensureDefaultFiles()
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
        const.PROJECTSPATH = str(const.getPROJECTSPATH())
        const.LOGOUTTIMEOUT = int(const.getLOGOUTTIMEOUT())
        const.TAGS = const.getTAGS()
        const.AUTOLOGIN = const.getAUTOLOGIN()

    def loadConfig():
        config = configparser.ConfigParser()
        config.optionxform = str
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct path to config.ini in the same directory
        config_path = os.path.join(script_dir, 'config.ini')
        config.read(config_path) #RasPi
        #config.read('config.ini') #Windows
        return config
    
    def writeConfig(config):
        #with open('config.ini', 'w') as configfile: #Windows
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct path to config.ini in the same directory
        config_path = os.path.join(script_dir, 'config.ini')
        with open(config_path, 'w') as configfile: #RasPi
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

    def getPROJECTSPATH():
        config = const.loadConfig()
        return config.get('PATHS', 'PROJECTSPATH')

    def setUSERSPATH(value):
        config = const.loadConfig()
        config.set('PATHS', 'USERSPATH', str(value))
        const.writeConfig(config)
        const.USERSPATH = value

    def setLOGPATH(value):
        config = const.loadConfig()
        config.set('PATHS', 'LOGPATH', str(value))
        const.writeConfig(config)
        const.LOGPATH = value

    def setPROBPATH(value):
        config = const.loadConfig()
        config.set('PATHS', 'PROBPATH', str(value))
        const.writeConfig(config)
        const.PROBPATH = value

    def setPROJECTSPATH(value):
        config = const.loadConfig()
        config.set('PATHS', 'PROJECTSPATH', str(value))
        const.writeConfig(config)
        const.PROJECTSPATH = value

    def getAUTOLOGIN():
        config = const.loadConfig()
        return ast.literal_eval(config.get('DEFAULT', 'AUTOLOGIN'))

    def setAUTOLOGIN(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'AUTOLOGIN', str(value))
        const.writeConfig(config)
        const.AUTOLOGIN = value

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
        const.ADMIN = value

    def getFOOTHOLDSETS():
        config = const.loadConfig()
        return ast.literal_eval(config.get('BOARD', 'FOOTHOLDSETS'))
    
    def setFOOTHOLDSETS(value):
        config = const.loadConfig()
        config.set('BOARD', 'FOOTHOLDSETS', value)
        const.writeConfig(config)    
        const.FOOTHOLDSETS = value        
        
    def getTAGS():
        config = const.loadConfig()
        return ast.literal_eval(config.get('BOARD', 'TAGS'))
    
    def setTAGS(value):
        config = const.loadConfig()
        config.set('BOARD', 'TAGS', value)
        const.writeConfig(config)    
        const.TAGS = value         
        
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
#print(const.TAGS[0])        
