from WienerProcess import WienerProcess
from done.maturity import Maturity

# Je comprends pas ce que c'est ? 
# WienerProcess = mouvement brownien mais on a deja une classe GMB ???? 


maturity=Maturity(1.0)
mvt=WienerProcess(
    drift=0,
    volatility=0.1,
    maturity=maturity,
    nb_simulations=10,
    nb_steps=250, 
    seed=272
)
print("Cumulative simulation : ")
print(mvt.cumulative_simulation())
print("Return simulation : ")
print(mvt.return_simulation(True))
#mvt.get_chart([0,1,2])
print("Confidence interval : ")
print(mvt.confidence_interval(0.9, [1,2,3]))
a=0