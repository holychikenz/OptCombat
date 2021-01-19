from OptCombat import OptCombat
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors

with open("zones.json") as jj:
    data = json.load(jj)

def f(m, b):
    return np.ceil(((m-1.3)*10-b/8)/(1+b/64))

mh = np.linspace(1, 30,30)
h = f(mh, 35)

player = OptCombat(data)
player.selectZone("city")
player.setTarget(99, 99)
player.setPlayer(29, 29, 35, 42)
print(f'Avg damage: {player.averageDamage()}')
print(f'Chance to hit: {player.tohit()}')
print(f'DPT: {player.damagePerTime()}')
print(f'Time: {player.simulatedOutcome()}')

#manytimes = [player.simulatedOutcome() for t in range(1000)]
#times = [x[0] for x in manytimes]
#bigTime = max(times)
#littleTime = min(times)
#norm = colors.LogNorm(vmin=littleTime, vmax=bigTime)
#cmap = cm.viridis
#m = cm.ScalarMappable(norm=norm, cmap=cmap)
#
#best_idx = 0
#best_t = manytimes[0][0]
#best_x = manytimes[0][1]
#best_y = manytimes[0][2]
#for (idx,ds) in enumerate(manytimes):
#    t, x, y = ds
#    if(t < best_t):
#        best_t = t
#        best_idx = idx
#        best_x = x
#        best_y = y
#    plt.plot(x, y, color=m.to_rgba(t))
#pval = 1 - sum(best_y)/len(best_y)*(99-30) /( (99-30)*(99-30) )/2
#plt.colorbar(m)
#plt.xlabel("Strength")
#plt.ylabel("Attack")
#plt.show()
#
#for i in range(10):
#    manytimes = [player.simulatedOutcome(p=pval) for t in range(1000)]
#    times = [x[0] for x in manytimes]
#    bigTime = max(times)
#    littleTime = min(times)
#    bigTime = littleTime*1.01
#    norm = colors.LogNorm(vmin=littleTime, vmax=bigTime)
#    m = cm.ScalarMappable(norm=norm, cmap=cmap)
#    best_idx = 0
#    best_t = manytimes[0][0]
#    best_x = []
#    best_y = []
#    for (idx,ds) in enumerate(manytimes):
#        t, x, y = ds
#        if(t < best_t):
#            best_t = t
#            best_idx = idx
#            best_x = x
#            best_y = y
#        #plt.plot(x, y, color=m.to_rgba(t))
#    pval = 1 - ( sum(best_y)/len(best_y)*(99-30) - (99-30)*30 )/( (99-30)*(99-30) )
#    print(pval)
#    #plt.colorbar(m)
#    #plt.xlabel("Strength")
#    #plt.ylabel("Attack")
#    #plt.show()
#
## Best of the best
#plt.plot(best_x, best_y)
#plt.xlim(min(best_x), max(best_x))
#for l in h:
#    plt.axvline(l, color='black')
#plt.show()
#
#plt.hist(times, bins=100)
#plt.show()
