import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from DMM import DMM34401A

def WB (Vout, R1, R2, R3, Vs):
    Rx = (R2*Vs - (R1+R2)*Vout)/(R1*Vs + (R1+R2)*Vout)*R3
    return Rx

a = DMM34401A.read_DMMs('DCV')
filename = "WheatStone_Vout.csv"
np.savetxt(filename, a, delimiter=",", fmt = '%10.8f')

df0 = pd.read_csv(filename, header=None, names=np.array(['time', 'volt']))
print(df0.head())

R1 = 550.748
R2 = 552.315
R3 = 550.801
Vs = 1
Rx1 = WB(df0['volt'], R1, R2, R3, Vs)

plt.figure()
plt.plot(df0['time'], Rx1)
plt.grid(True)
plt.show()