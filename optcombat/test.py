from OptCombat import OptCombat
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors

plt.style.use("snoplus")

with open("zones.json") as jj:
    data = json.load(jj)

def f(m, b):
    return np.ceil(((m-1.3)*10-b/8)/(1+b/64))

base_trials = 5_000
pert_trials = 10_000

wAtt = 59
wStr = 45
mh = np.linspace(1, 30,30)
h = f(mh, wStr)

player = OptCombat(data)
player.selectZone("farm")
sAtt = 60 
sStr = 60
eAtt = 99
eStr = 99
player.setTarget(eAtt, eStr)
player.setPlayer(sStr, sAtt, wStr, wAtt)
player.reckless = 5
print(f'Avg damage: {player.averageDamage()}')
print(f'Chance to hit: {player.tohit()}')
print(f'DPT: {player.damagePerTime()}')
print(f'Time: {player.simulatedOutcome()}')

manytimes = [player.simulatedOutcome(verbose=True, memory=True) for t in range(base_trials)]
times = [x[0] for x in manytimes]
pp = 1
bigTime = max(times)**pp
littleTime = min(times)**pp
norm = colors.LogNorm(vmin=littleTime, vmax=bigTime)
cmap = cm.gist_earth
m = cm.ScalarMappable(norm=norm, cmap=cmap)

best_idx = 0
best_t = manytimes[0][0]
best_x = manytimes[0][1]
best_y = manytimes[0][2]
for (idx,ds) in enumerate(manytimes):
    t, x, y = ds
    if(t < best_t):
        best_t = t
        best_idx = idx
        best_x = x
        best_y = y
    plt.plot(x, y, color=m.to_rgba(t**pp))
print(best_y)
pval = 1 - ( sum(best_y)/len(best_y)*(eAtt-sAtt) - (eStr-sStr)*sAtt )/( (eStr-sStr)*(eAtt-sAtt) )
plt.colorbar(m)
plt.xlabel("Strength")
plt.ylabel("Attack")
plt.show()

for i in range(0):
    manytimes = [player.simulatedOutcome(p=pval) for t in range(base_trials)]
    times = [x[0] for x in manytimes]
    bigTime = max(times)
    littleTime = min(times)
    bigTime = littleTime*1.01
    norm = colors.LogNorm(vmin=littleTime, vmax=bigTime)
    m = cm.ScalarMappable(norm=norm, cmap=cmap)
    best_idx = 0
    best_t = manytimes[0][0]
    best_x = manytimes[0][1] 
    best_y = manytimes[0][2]
    for (idx,ds) in enumerate(manytimes):
        t, x, y = ds
        if(t < best_t):
            best_t = t
            best_idx = idx
            best_x = x
            best_y = y
        #plt.plot(x, y, color=m.to_rgba(t))
    pval = 1 - ( sum(best_y)/len(best_y)*(eAtt-sAtt) - (eStr-sStr)*sAtt )/( (eStr-sStr)*(eAtt-sAtt) )
    print(f'{i}/100 -- {pval:0.2f}')
    #plt.colorbar(m)
    #plt.xlabel("Strength")
    #plt.ylabel("Attack")
    #plt.show()

# Best of the best
best_x = np.array(best_x)
best_y = np.array(best_y)
plt.plot(best_x, best_y)
plt.xlim(min(best_x), max(best_x))
for l in h:
    plt.axvline(l, color='black')
nx = np.linspace(min(best_x), max(best_x), max(best_x)-min(best_x)+1)
plt.plot(nx, nx, '--')
# Cleanup based on breakpoints
ny = []

fset = []
lastAtt = sAtt
lastStr = sStr
for l in h:
    try:
        atk = np.min(best_y[best_x>l])
    except:
        if l > max(best_x):
            atk = eAtt
        else:
            atk = 0
    if (l > sStr) and (atk >= sAtt) and (l <= eStr):
        newset = np.ones(int(l-lastStr))
        fset = np.concatenate([fset, newset])
        newset = np.zeros(int( atk - lastAtt ))
        fset = np.concatenate([fset, newset])
        lastStr = l
        lastAtt = atk
    ny.append(atk)
print("!", fset)
t, x, y = player.orderedOutcome(fset)
simpOrder = player.simXYtoOrder(x, y)
plt.plot(x, y, '.')

plt.plot(h, ny, '+')
plt.ylim(sAtt, eAtt)
#plt.show()

neworder = player.simXYtoOrder(best_x, best_y)
print(neworder)

t, x, y = player.orderedOutcome(neworder)
plt.plot(x, y)
print(t)
plt.grid()
plt.show()

nts, nx, ny = player.orderedOutcome(neworder)
plt.plot(nx, ny, label=f'{nts:0.0f}')
count = 0
for i in range(20):
    forder = player._swapOrder(neworder, count=1000)
    nt, nx, ny = player.orderedOutcome(forder)
    if( nt == nts ):
        continue
    count += 1
    plt.plot(nx, ny, ':', label=f'{nt:0.0f}')
    if count > 5:
        break
plt.legend()
plt.show()

# Try for better -- still doesn't get there
bestorder = player.perturbedSystem( neworder, trials=pert_trials, debug=False, count=10 )
bestorder = player.perturbedSystem( bestorder, trials=pert_trials, debug=False, count=1 )
plt.plot(x, y, ":", label="Stochastic System")
t, x, y = player.orderedOutcome(bestorder)
plt.plot(x, y, label="Perturbed System")
for l in h:
    plt.axvline(l, color='black', dashes=[1,3])
    try:
        if(l >= sAtt):
            t_y = y[x==l][-1]
            txt = f'({l}, {t_y})'
            plt.text(l, sAtt+(eAtt-sAtt)*1.01, txt)
    except:
        pass
plt.plot(x, x, "--")
plt.ylim(sAtt, eAtt)
plt.xlim(min(best_x), max(best_x))
plt.xlabel("Str")
plt.ylabel("Atk")
plt.legend(loc=6)
plt.show()

plt.hist(times, bins=100)
plt.axvline(t, color='xkcd:maroon')
plt.show()
