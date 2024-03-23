from WienerProcess import WienerProcess
from maturity import Maturity


maturity=Maturity(1.0)
mvt=WienerProcess(
    drift=0,
    volatility=0.1,
    maturity=maturity,
    nb_simulations=10,
    nb_steps=2,
    seed=272
)
print(mvt.simul(True))
a=0