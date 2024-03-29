import numpy as np


class AbstractProduct:
    _product_name = "produit"
    _inputs = None

    def __init__(self, inputs):
        self._inputs = inputs

    def payoff(self, spot):
        raise Exception("Not implemented")


class Call(AbstractProduct):
    def __init__(self, inputs):
        super().__init__(inputs)

    def _strike(self):
        return self._inputs.get("strike")

    def payoff(self, spot):
        return np.maximum(spot - self._strike(), 0)
    
class Put(AbstractProduct):
    def __init__(self, inputs):
        super().__init__(inputs)

    def _strike(self):
        return self._inputs.get("strike")

    def payoff(self, spot):
        return np.maximum(self._strike() - spot, 0)
