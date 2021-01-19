import numpy as np
from copy import deepcopy
# Todo
# 1. Add conditional power boosts (like weapon swap at certaint stat levels)
# 2. Include defense as an optional stat ( crown with recklessness )
class OptCombat:
    '''
    Use estimated combat parameters to determine an optimal
    leveling path to reach a desired level.
    Challenge: include gear swaps at target levels
    '''
    def __init__(self, data):
        self.data = data
        lvls  = np.linspace(1,99,99)
        self.delta = 0.25*np.floor((lvls-1+300*2**((lvls-1)/7)))
        self.delta[0] = 0
        self.totalxp = np.cumsum(self.delta)
        # Defaults
        self.zone      = "farm"
        self.targetStr = 99
        self.targetAtt = 99
        self.patience  = 0
        self.reckless  = 0
        self.speed     = 2.4
        self.strLevel  = 1
        self.attLevel  = 1
        self.strBonus  = 0
        self.attBonus  = 1
        self.attType   = 0
        self.pval      = 0.5
        self.bestTime  = 1e10

    def setPlayer(self, strL, attL, strB, attB):
        self.strLevel = strL
        self.strBonus = strB
        self.attLevel = attL
        self.attBonus = attB

    def setTarget(self, strength, attack):
        self.targetStr = strength
        self.targetAtt = attack

    def selectZone(self, zone):
        if zone in self.data:
            self.zone = zone
        else:
            raise KeyError(f'{zone} is not an available zone in the database')

    def averageDamage(self):
        patdmg = self.patience * 0.3 * (self.speed - 1)**2
        maxhit = np.floor(1.3 + self.strLevel/10 + self.strBonus/80 + self.strLevel*self.strBonus/640)
        avgdmg = (maxhit+1 + patdmg + self.reckless)/2.0
        return avgdmg

    def maxhitThreshold(self):
        mh = np.linspace(1, 60, 60)
        return np.ceil((( mh - 1.3 )*10 - self.strBonus/8)/(1+self.strBonus/64))

    def tohit(self):
        playerAccuracy = self.attLevel * (self.attBonus + 64)
        defset = (np.array(self.data[self.zone]["def"]).T)[self.attType]
        chance = [ (playerAccuracy / d / 2) if d>playerAccuracy else (1 - d/playerAccuracy/2) for d in defset ]
        return chance

    def damagePerTime(self):
        # Get average hit damage
        return np.sum(self.tohit() * np.array(self.data[self.zone]["chance"]) * self.averageDamage())

    def calculatePenalty(self):
        I = sum(((self.x - np.roll(self.x, 1))*self.y)[1:])
        a = self.targetStr
        b = self.startingStrLevel
        c = self.startingAttLevel
        d = self.targetAtt
        pval = 1 - (I - (a-b)*c)/( (a-b)*(d-c) )
        self.pval = pval

    def simulatedOutcome(self, **kwargs):
        penaltySize = kwargs.get("penalty", 1000)
        penx = np.array(kwargs.get("penx", np.linspace(1,99,99)))
        peny = np.array(kwargs.get("peny", np.linspace(1,99,99)))
        p = kwargs.get("p", 0.5)
        memory = kwargs.get("memory", False)
        if memory:
            p = self.pval

        # What is the plan here? Random, brute force, MCMC?
        self.startingStrLevel = self.strLevel
        self.startingAttLevel = self.attLevel
        x, y = [], []
        timer = 0
        # Lets see what the outcome of coinflip is
        while( (self.strLevel < self.targetStr) or (self.attLevel < self.targetAtt) ):
            # Get probability and apply weight
            x.append(self.strLevel)
            y.append(self.attLevel)
            #p = 1 - min(1, abs((0.5 - min(peny[penx == self.strLevel] - self.attLevel)**2/2/penaltySize**2)))
            if( (np.random.rand() < p or (self.attLevel == self.targetAtt)) and (self.strLevel < self.targetStr) ):
                ## Level Strength
                timer += self.delta[self.strLevel] / self.damagePerTime()
                self.strLevel += 1
            else:
                ## Level Attack
                timer += self.delta[self.attLevel] / self.damagePerTime()
                self.attLevel += 1

        # Reset
        self.strLevel = self.startingStrLevel
        self.attLevel = self.startingAttLevel

        self.x, self.y = x, y
        if timer < self.bestTime:
            self.calculatePenalty()
            self.bestTime = timer

        return timer, x, y

    def simXYtoOrder(self, x, y):
        thing = []
        lx, ly = x[0], y[0]
        for (i, j) in zip(x, y):
            if i != lx:
                thing.append(1)
            if j != ly:
                thing.append(0)
            lx = i
            ly = j
        return np.array(thing)

    def orderedOutcome(self, order, **kwargs):
        # Order should be something like [0, 1, 1, 0, 0, ..., 1]
        # Where 0: Level Attack, and 1: Level Strength
        self.startingStrLevel = self.strLevel
        self.startingAttLevel = self.attLevel
        x, y = [], []
        timer = 0
        for choice in order:
            x.append( self.strLevel )
            y.append( self.attLevel )
            if( choice == 0 ):
                timer += self.delta[self.attLevel] / self.damagePerTime()
                self.attLevel += 1
            else:
                timer += self.delta[self.strLevel] / self.damagePerTime()
                self.strLevel += 1
        self.strLevel = self.startingStrLevel
        self.attLevel = self.startingAttLevel

        return timer, np.array(x), np.array(y)

    def _swapOrder(self, order, count=1):
        for c in range(count):
            lmt = np.random.randint(0, len(order)-1)
            x = order[lmt]
            order[lmt] = order[lmt+1]
            order[lmt+1] = x
        return order

    def perturbedSystem(self, initorder, **kwargs):
        trials = kwargs.get('trials', 1000)
        debug  = kwargs.get('debug', False)
        count  = kwargs.get('count', 1)
        #bestorder = initorder
        t, x, y = self.orderedOutcome(initorder)
        for trr in range(trials):
            testorder = self._swapOrder(deepcopy(initorder), count)
            nt, nx, ny = self.orderedOutcome(testorder)
            if( nt <= t ):
                initorder = deepcopy(testorder)
                t = nt
                if debug:
                    print(f"t: {t:0.03f}")
        return initorder

    def _batchSwap(self, order):
        lmt = np.random.randint(0, len(order)-1)

    def scalePerturb(self, initorder, **kwargs):
        '''
        Like the perturbative method, but looks to move
        large flat regions since we know that is where 
        real optimization power comes from.
        '''
        trials = kwargs.get('trials', 1000)
        debug  = kwargs.get('debug', False)
        count  = kwargs.get('count', 1)
        t, x, y = self.orderedOutcome(initorder)
        #for trr in range(trials):

