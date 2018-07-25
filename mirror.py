from const import const

class mirror:
    #todo - complete this table for all holds!
    #MIRRORTABLE = [[1,11],[2,10],[3,9],[4,8],[5,7],[6,6],[7,5],[8,4],[9,3],[10,2],[11,1],[12,22],[13,23],[14,21],[15,19],[16,18],[17,17],[18,16],[19,15],[20,28],[21,14],[22,12],[23,13],[24,27],[25,26],[26,25],[27,24],[28,20],[29,37],[30,39],[31,40],[32,38],[33,41],[34,36],[35,35],[36,34],[37,29],[38,32],[39,30],[40,31],[41,33],[42,44],[43,43],[44,42],[45,56],[46,57],[47,58],[48,59],[49,60],[50,63],[51,55],[52,54],[53,53],[54,52],[55,51],[56,45],[57,46],[58,47],[59,48],[60,49],[61,70],[62,69],[63,50],[64,68],[65,67],[66,66],[67,65],[68,64],[69,62],[70,61],[71,84],[72,85],[73,86],[74,87],[75,83],[76,82],[77,81],[78,80],[79,79],[80,78],[81,77],[82,76],[83,75],[84,71],[85,72],[86,73],[87,74],[88,96],[89,95],[90,94],[91,93],[92,92],[93,91],[94,90],[95,89],[96,88],[97,110],[98,109],[99,108],[100,106],[101,107],[102,105],[103,103],[104,104],[105,102],[106,100],[107,101],[108,99],[109,98],[110,97],[111,117],[112,116],[113,115],[114,114],[115,113],[116,112],[117,111],[118,126],[119,125],[120,124],[121,123],[122,122],[123,121],[124,120],[125,119],[126,118]]
    
    def getMirror(holdArr):
        mirrorHolds = []
        for item in holdArr:
            for holds in const.MIRRORTABLE:
                if holds[0] == item:
                    mirrorHolds.append(holds[1])
        return mirrorHolds
    
#print(mirror.getMirror([2,8]))