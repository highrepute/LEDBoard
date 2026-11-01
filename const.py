
import configparser
import ast
import os
import shutil
import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.ini')


# --- config value parsers: return the parsed value or raise ValueError
def _intRange(lo, hi=None):
    def parse(text):
        value = int(text)
        if value < lo or (hi is not None and value > hi):
            raise ValueError('out of range')
        return value
    return parse


def _strList(allowEmpty):
    def parse(text):
        value = ast.literal_eval(text)
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValueError('not a list of text')
        if not value and not allowEmpty:
            raise ValueError('empty list')
        return value
    return parse


def _text(text):
    return str(text)


def _path(text):
    if not text.strip():
        raise ValueError('empty path')
    return text


# every config key: (section, key, default text, parser)
CONFIG_SPEC = [
    ('DEFAULT', 'LINUX', '1', _intRange(0, 1)),
    ('DEFAULT', 'LEDBRIGHTNESS', '50', _intRange(0, 255)),
    ('DEFAULT', 'DEFAULTMSG', 'Welcome to the Board', _text),
    ('DEFAULT', 'GRADES', "['6a', '6a+', '6b', '6b+', '6c', '6c+', '7a']", _strList(False)),
    ('DEFAULT', 'STARS', "['-', '*', '**', '***']", _strList(False)),
    ('DEFAULT', 'ADMIN', 'James', _text),
    ('DEFAULT', 'THEMECOLOUR', '#fd4', _text),
    ('DEFAULT', 'LOGOUTTIMEOUT', '1800', _intRange(0)),
    ('DEFAULT', 'AUTOLOGIN', "['James']", _strList(True)),
    ('BOARD', 'TOTALLEDCOUNT', '0', _intRange(0)),
    ('BOARD', 'IMAGEPATH', '', _text),
    ('BOARD', 'BOARDNAME', '', _text),
    ('BOARD', 'WALLLOGOPATH', '', _text),
    ('BOARD', 'BOARDLOGOPATH', '', _text),
    ('BOARD', 'FOOTHOLDSETS', "['Standard']", _strList(False)),
    ('BOARD', 'TAGS', "['Tags']", _strList(False)),
    ('PATHS', 'USERSPATH', os.path.join(SCRIPT_DIR, 'users.csv'), _path),
    ('PATHS', 'LOGPATH', os.path.join(SCRIPT_DIR, 'logs.csv'), _path),
    ('PATHS', 'PROBPATH', os.path.join(SCRIPT_DIR, 'problems.csv'), _path),
    ('PATHS', 'PROJECTSPATH', os.path.join(SCRIPT_DIR, 'projects.csv'), _path),
]
CONFIG_SPEC_BY_KEY = dict(((sec, key), (default, parse)) for sec, key, default, parse in CONFIG_SPEC)


def _newConfig():
    config = configparser.ConfigParser(strict=False, interpolation=None)
    config.optionxform = str
    return config


def _defaultConfig():
    config = _newConfig()
    for sec, key, default, parse in CONFIG_SPEC:
        if sec != 'DEFAULT' and not config.has_section(sec):
            config.add_section(sec)
        config.set(sec, key, default)
    return config


def _timestamp():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


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
    BOARDFRAMEWIDTH = 781   # frmBoard / frame_6 width in DiscoBoard.ui
    BOARDFRAMEHEIGHT = 761  # frmBoard / frame_6 height in DiscoBoard.ui
    HOLDBUTTONSIZE = 31     # DragButton size in DiscoMain.py
    
    CONFIGMESSAGES = []  # what the last config check fixed, for the UI

    def ensureConfig():
        """Make sure config.ini exists, parses, and has a valid value for
        every key. Bad or missing values are reset to their defaults, with
        the original file backed up first. Never raises."""
        msgs = []
        if not os.path.exists(CONFIG_PATH):
            _defaultConfig().write(open(CONFIG_PATH, 'w'))
            const.CONFIGMESSAGES = ['config.ini: not found, created with defaults']
            return

        config = _newConfig()
        try:
            config.read(CONFIG_PATH)
        except (configparser.Error, UnicodeDecodeError) as e:
            backup = CONFIG_PATH.replace('.ini', '_unrecognised_%s.ini' % _timestamp())
            shutil.copy2(CONFIG_PATH, backup)
            with open(CONFIG_PATH, 'w') as f:
                _defaultConfig().write(f)
            const.CONFIGMESSAGES = ['config.ini: could not be read (%s) - moved to %s, using defaults'
                                    % (type(e).__name__, os.path.basename(backup))]
            return

        for sec, key, default, parse in CONFIG_SPEC:
            if sec != 'DEFAULT' and not config.has_section(sec):
                config.add_section(sec)
            if not config.has_option(sec, key):
                config.set(sec, key, default)
                msgs.append('%s missing' % key)
                continue
            value = config.get(sec, key)
            try:
                parse(value)
            except (ValueError, SyntaxError, TypeError):
                config.set(sec, key, default)
                msgs.append('%s "%s" invalid' % (key, value))

        if msgs:
            backup = CONFIG_PATH.replace('.ini', '_backup_%s.ini' % _timestamp())
            shutil.copy2(CONFIG_PATH, backup)
            with open(CONFIG_PATH, 'w') as f:
                config.write(f)
            msgs = ['config.ini: ' + ', '.join(msgs) + ' - reset to defaults']
        for m in msgs:
            print('Config check - ' + m)
        const.CONFIGMESSAGES = msgs

    def ensureDefaultFiles():
        #create any missing data files (dataCheck.py does the full check)
        for key, kind in (('USERSPATH', 'USERS'), ('LOGPATH', 'LOGS'),
                          ('PROBPATH', 'PROBLEMS'), ('PROJECTSPATH', 'PROJECTS')):
            try:
                path = const._value('PATHS', key)
                folder = os.path.dirname(path)
                if folder and not os.path.isdir(folder):
                    os.makedirs(folder)
                if not os.path.exists(path):
                    with open(path, 'w', newline='') as f:
                        f.write(const.defaultCsvText(kind))
            except OSError as e:
                print('Could not create %s: %s' % (key, e))

    def defaultCsvText(kind):
        #default contents for a new data file of the given kind
        import datetime
        today = datetime.date.today().strftime('%d/%m/%Y')
        return {
            'USERS': 'Username,Password,Date Reg, Real name, Email\nJames,123,%s,,\n' % today,
            'LOGS': 'Username,Problem,Grade,Stars,Ascent Date,Comments,Attempts\n',
            'PROBLEMS': 'Name,Grade,Stars,Added,User,Comments,Foothold,tag0,tag1,tag2,tag3,tag4,tag5,tag6,tag7,tag8,tag9,Start1,Start2,Fin1,Fin2,HoldNo\n',
            'PROJECTS': 'Username,ProblemName\n',
        }[kind]

    def initConfigVariables():
        const.ensureConfig()
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
        config = _newConfig()
        try:
            config.read(CONFIG_PATH)
        except (configparser.Error, UnicodeDecodeError):
            config = _defaultConfig()
        for sec in ('BOARD', 'PATHS'):
            if not config.has_section(sec):
                config.add_section(sec)
        return config

    def _value(section, key):
        #read one config value, falling back to its default if missing/invalid
        default, parse = CONFIG_SPEC_BY_KEY[(section, key)]
        raw = const.loadConfig().get(section, key, fallback=default)
        try:
            return parse(raw)
        except (ValueError, SyntaxError, TypeError):
            return parse(default)
    
    def writeConfig(config):
        #with open('config.ini', 'w') as configfile: #Windows
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct path to config.ini in the same directory
        config_path = os.path.join(script_dir, 'config.ini')
        with open(config_path, 'w') as configfile: #RasPi
            config.write(configfile)

    def getLINUX():
        return const._value('DEFAULT', 'LINUX')
    
    def setLINUX(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'LINUX', str(value))
        const.writeConfig(config)
        const.LINUX = value
        
    def getLOGOUTTIMEOUT():
        return const._value('DEFAULT', 'LOGOUTTIMEOUT')
    
    def setLOGOUTTIMEOUT(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'LOGOUTTIMEOUT', str(value))
        const.writeConfig(config)
        const.LOGOUTTIMEOUT = value
        
    def getUSERSPATH():
        return const._value('PATHS', 'USERSPATH')

    def getLOGPATH():
        return const._value('PATHS', 'LOGPATH')

    def getPROBPATH():
        return const._value('PATHS', 'PROBPATH')

    def getPROJECTSPATH():
        return const._value('PATHS', 'PROJECTSPATH')

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
        return const._value('DEFAULT', 'AUTOLOGIN')

    def setAUTOLOGIN(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'AUTOLOGIN', str(value))
        const.writeConfig(config)
        const.AUTOLOGIN = value

    def getBOARDNAME():
        return const._value('BOARD', 'BOARDNAME')
    
    def setBOARDNAME(value):
        config = const.loadConfig()
        config.set('BOARD', 'BOARDNAME', str(value))
        const.writeConfig(config)
        const.BOARDNAME = value   

    def getTOTAL_LED_COUNT():
        return const._value('BOARD', 'TOTALLEDCOUNT')
    
    def setTOTAL_LED_COUNT(value):
        config = const.loadConfig()
        config.set('BOARD', 'TOTALLEDCOUNT', str(value))
        const.writeConfig(config)
        const.TOTAL_LED_COUNT = value
    
    def getLED_VALUE():
        return const._value('DEFAULT', 'LEDBRIGHTNESS')
    
    def setLED_VALUE(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'LEDBRIGHTNESS', str(value))
        const.writeConfig(config)
        const.LED_VALUE = value
        
    def getDEFAULTMSG():
        return const._value('DEFAULT', 'DEFAULTMSG')
    
    def setDEFAULTMSG(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'DEFAULTMSG', str(value))
        const.writeConfig(config)
        const.DEFAULTMSG = value

    def getGRADES():
        return const._value('DEFAULT', 'GRADES')
    
    def setGRADES(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'GRADES', value)
        const.writeConfig(config)    
        const.GRADES = value

    def getSTARS():
        return const._value('DEFAULT', 'STARS')
    
    def setSTARS(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'STARS', value)
        const.writeConfig(config)    
        const.STARS = value
    
    def getIMAGEPATH():
        return const._value('BOARD', 'IMAGEPATH')
    
    def setIMAGEPATH(value):
        config = const.loadConfig()
        config.set('BOARD', 'IMAGEPATH', str(value))
        const.writeConfig(config)
        const.IMAGEPATH = value
        
    def getWALLLOGOPATH():
        return const._value('BOARD', 'WALLLOGOPATH')
    
    def setWALLLOGOPATH(value):
        config = const.loadConfig()
        config.set('BOARD', 'WALLLOGOPATH', str(value))
        const.writeConfig(config)
        const.WALLLOGOPATH = value
        
    def getBOARDLOGOPATH():
        return const._value('BOARD', 'BOARDLOGOPATH')
    
    def setBOARDLOGOPATH(value):
        config = const.loadConfig()
        config.set('BOARD', 'BOARDLOGOPATH', str(value))
        const.writeConfig(config)
        const.BOARDLOGOPATH = value

    def getTHEMECOLOUR():
        return const._value('DEFAULT', 'THEMECOLOUR')
    
    def setTHEMECOLOUR(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'THEMECOLOUR', str(value))
        const.writeConfig(config)
        const.THEMECOLOUR = value         

    def getADMIN():
        return const._value('DEFAULT', 'ADMIN')
    
    def setADMIN(value):
        config = const.loadConfig()
        config.set('DEFAULT', 'ADMIN', str(value))
        const.writeConfig(config)
        const.ADMIN = value

    def getFOOTHOLDSETS():
        return const._value('BOARD', 'FOOTHOLDSETS')
    
    def setFOOTHOLDSETS(value):
        config = const.loadConfig()
        config.set('BOARD', 'FOOTHOLDSETS', value)
        const.writeConfig(config)    
        const.FOOTHOLDSETS = value        
        
    def getTAGS():
        return const._value('BOARD', 'TAGS')
    
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
