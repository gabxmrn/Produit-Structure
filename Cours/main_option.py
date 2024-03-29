from WienerProcess import WienerProcess
from maturity import Maturity



maturity=Maturity(1.0)
mvt=WienerProcess(
    drift=0,
    volatility=0.1,
    maturity=maturity,
    nb_simulations=10,
    nb_steps=250, 
    seed=272
)
print(mvt.cumulative_simulation())
print(mvt.return_simulation(True))
#mvt.get_chart([0,1,2])
print(mvt.confidence_interval(0.9, [1,2,3]))
a=0