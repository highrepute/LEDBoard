
import configparser
import ast

class const:   
    #initialise these to some default values
    LINUX = 0
    LED_VALUE = 50
    DEFAULTMSG = "Welcome to the Board of High Repute"
    GRADES = ['6a', '6a+', '6b', '6b+', '6c', '6c+', '7a']
    STARS = ['-', '*', '**', '***']
    MIRRORTABLE = []
    TOTAL_LED_COUNT = 126
    IMAGEPATH = None
    
    def setConfigVariables():
        const.LINUX = int(const.getLINUX())
        const.LED_VALUE = int(const.getLED_VALUE())
        const.DEFAULTMSG = str(const.getDEFAULTMSG())
        const.GRADES = const.getGRADES()
        const.STARS = const.getSTARS()
        const.MIRRORTABLE = const.getMIRRORTABLE()
        const.TOTAL_LED_COUNT = int(const.getTOTAL_LED_COUNT())
        const.IMAGEPATH = str(const.getIMAGEPATH())
    
    def loadConfig():
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read('config.ini')
        return config
    
    def writeConfig(config):
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def getLINUX():
        config = const.loadConfig()
        return int(config.get('DEFAULT', 'LINUX'))
    
    def setLINUX(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'LINUX', str(value))
        const.writeConfig(config)
        const.LINUX = value

    def getTOTAL_LED_COUNT():
        config = const.loadConfig()
        return int(config.get('BOARD', 'TOTAL_LED_COUNT'))
    
    def setTOTAL_LED_COUNT(value):
        config = const.loadConfig()
        config.set('BOARD', 'TOTAL_LED_COUNT', str(value))
        const.writeConfig(config)
        const.TOTAL_LED_COUNT = value
    
    def getLED_VALUE():
        config = const.loadConfig()
        return int(config.get('DEFAULT', 'LED_VALUE'))   
    
    def setLED_VALUE(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'LED_VALUE', str(value))
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
    
    def getMIRRORTABLE():
        config = const.loadConfig()
        return ast.literal_eval(config.get('BOARD', 'MIRRORTABLE'))
    
    def setMIRRORTABLE(value):
        config = const.loadConfig()
        config.set('BOARD', 'MIRRORTABLE', str(value))
        const.writeConfig(config)  
        const.MIRRORTABLE = value
    
    def getIMAGEPATH():
        config = const.loadConfig()
        return config.get('BOARD', 'IMAGEPATH')
    
    def setIMAGEPATH(value):
        config = const.loadConfig()
        config.set('BOARD', 'IMAGEPATH', str(value))
        const.writeConfig(config)
        const.IMAGEPATH = value
    
#print(const.LINUX)
#const.setConfigVariables()
#print(const.GRADES[0])
#grades = ['6a', '6a+', '6b', '6b+', '6c', '6c+', '7a']
#print(str(grades))
#print(const.IMAGEPATH)
#print(const.LINUX)
#const.setIMAGEPATH("C:/Users/James.Jacobs/Desktop/Temp/LED/20180411_210921_2.jpg")
#const.setLINUX("1")
#print(const.MIRRORTABLE)
#print(const.IMAGEPATH)
