from boardMaker import boardMaker
from const import const

class mirror:
    def getMirror(holdArr):
        mirrorHolds = []
        for item in holdArr:
            for holds in boardMaker.getBoardMirrorTable(const.BOARDNAME):
                if holds[0] == item:
                    mirrorHolds.append(holds[1])
        return mirrorHolds
    
const.initConfigVariables()
print(mirror.getMirror([128,8]))