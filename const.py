
import configparser
import ast

class const:   
    def loadConfig():
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read('config.ini')
        return config
    
    def writeConfig(config):
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def LINUX():
        config = const.loadConfig()
        return int(config.get('DEFAULT', 'LINUX'))
    
    def setLINUX(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'LINUX', value)
        const.writeConfig(config)

    def TOTAL_LED_COUNT():
        config = const.loadConfig()
        return int(config.get('BOARD', 'TOTAL_LED_COUNT'))
    
    def LED_VALUE():
        config = const.loadConfig()
        return int(config.get('DEFAULT', 'LED_VALUE'))   
        
    def DEFAULTMSG():
        config = const.loadConfig()
        return str(config.get('DEFAULT', 'DEFAULTMSG')) 

    def GRADES():
        config = const.loadConfig()
        return ast.literal_eval(config.get('DEFAULT', 'GRADES'))

    def STARS():
        config = const.loadConfig()
        return ast.literal_eval(config.get('DEFAULT', 'STARS'))
    
    def MIRRORTABLE():
        config = const.loadConfig()
        return ast.literal_eval(config.get('BOARD', 'MIRRORTABLE'))
    
    def BOARDIMAGEPATH():
        config = const.loadConfig()
        return ast.literal_eval(config.get('BOARD', 'MIRRORTABLE'))        
    
    def setBOARDIMAGEPATH(path):
        config = const.loadConfig()
        config.set('BOARD', 'BOARDIMAGEPATH', path)
    
#print(const.TOTAL_LED_COUNT())
#const.setLINUX("0")