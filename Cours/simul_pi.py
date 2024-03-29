
import numpy as np

# Pourquoi simuler pi ???? 

np.random.seed(272)
n=10000
z=np.random.random([2,n])
in_cercle=z[0]**2+z[1]**2<=1
ratio=np.count_nonzero(in_cercle)/n*4.0
print(ratio)

