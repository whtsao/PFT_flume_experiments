import numpy as np
import matplotlib.pyplot as plt
import math

# load original experimental data
exp = np.loadtxt("detrend_341583.csv", comments="#", delimiter=",", unpack=False)

#calculate wg number
nwg = int(np.size(exp)/len(exp)) - 1

#adjust input files to wave heights
num = np.zeros((nwg,len(exp)))
for wg in range(1,nwg+1):
    for i in range(len(exp)):
        #num[wg-1,i]=0.322-exp[i,wg]
        num[wg-1,i]=exp[i,wg]

#calculate wave heights
for x in range(nwg):
    col=num[x]
    ns = 1
    nf = 4202
    idx=0
    new = np.zeros((nf-ns))
    for i in range(ns,nf):
        new[idx] = col[i]
        idx=idx+1
    zero_crossings = np.where(np.diff(np.sign(new)))[0]
    peaks = np.zeros(len(zero_crossings)-1)
    peak_idx = np.zeros(len(zero_crossings)-1)
    for i in range(len(zero_crossings)-1):
        first=zero_crossings[i]
        second=zero_crossings[i+1]
        values = np.zeros(second-first+1)
        x=0
        for idx in range(first,second+1):
            values[x]=new[idx]
            if x!=second-1:
                x=x+1
            else:
                pass
        if new[first]>0:
            peaks[i]=np.min(values)
            peak_idx[i]=np.argmin(values)+first
        elif new[first]<0:    
            peaks[i]=np.max(values)
            peak_idx[i]=np.argmax(values)+first

    height = []
    for idx in range(len(peaks)-1):
        mi=peaks[idx]
        ma=peaks[idx+1]
        if mi<0:
            height.append(ma-mi)
        if ma>0:
            pass

    H_3=np.sort(height)[len(height)-math.ceil(len(height)/3):]
    Hs=np.mean(H_3)
    Hs_std=np.std(H_3)
    Hs_min=np.min(H_3)
    Hs_max=np.max(H_3)
    
    print("Hs=",Hs,"Hs_min=",Hs_min,"Hs_max=",Hs_max,"Hs_std=",Hs_std)

    
    #plt.figure(1, figsize=(10,6), dpi=100)
    #plt.plot(new)
    #plt.plot(zero_crossings, new[zero_crossings],'kx')
    #plt.plot(peak_idx,peaks,'rx')
    #plt.plot(np.zeros_like(new), "--", color="gray")
    #plt.show()
