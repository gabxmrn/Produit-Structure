import numpy as np

### A rajouter : 
# - Choix du sous jacent : action, indice ou taux de change 
# (avec leur attributs respectifs : dividende, taux de change, ...)
# - Ici la volatilité est unique, je crois qu'il faut aussi la vol stochastique 
# - Les grecques (je sais pas trop ou les foutre, le split option/mvt brownien du prof est bizarre)


class AbstractProduct:
    """ Abstract class representing a financial product. """
    _product_name = "product"
    _inputs = None

    def __init__(self, inputs):
        """ 
        Initialize an AbstractProduct object.
        Args: inputs (dict): Input parameters for the product.
        """
        self._inputs = inputs

    def payoff(self, spot):
        """
        Method to calculate the payoff of the product.

        Args:
            spot (float): Current spot price.

        Returns:
            float: Payoff of the product.
        """
        
        raise Exception("Not implemented")


class Call(AbstractProduct):
    """ A class representing a Call option financial product. """
    
    def __init__(self, inputs):
        """
        Initialize a Call option object.
        Args: inputs (dict): Input parameters for the option.
        """
        super().__init__(inputs)

    def _strike(self):
        """
        Get the strike price.

        Returns:
            float: Strike price.
        """
        return self._inputs.get("strike")

    def payoff(self, spot):
        """
        Calculate the payoff of the Call option.

        Args:
            spot (float): Current spot price.

        Returns:
            float: Payoff of the Call option.
        """
        return np.maximum(spot - self._strike(), 0)
    
    def greeks(self, spot):
        pass 
    
    
class Put(AbstractProduct):
    def __init__(self, inputs):
        """ A class representing a Put option financial product. """
        super().__init__(inputs)

    def _strike(self):
        """
        Get the strike price.

        Returns:
            float: Strike price.
        """
        return self._inputs.get("strike")

    def payoff(self, spot):
        """
        Calculate the payoff of the Put option.

        Args:
            spot (float): Current spot price.

        Returns:
            float: Payoff of the Put option.
        """
        return np.maximum(self._strike() - spot, 0)
