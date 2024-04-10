import numpy as np

FOREX = "forex rate"
CALL = "call"
PUT = "put"

class AbstractProduct:
    """ Abstract class representing a financial product. """
    _product_name = "product"
    _inputs = None

    def __init__(self, inputs:dict): 
        """ 
        Initialize an AbstractProduct object.
        Args: 
        - inputs (dict): Input parameters for the product.
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


class VanillaOption(AbstractProduct):
    """ A class representing a Vanilla Option (Call/Put) option financial product. """
    
    def __init__(self, underlying:str, inputs:dict) -> None :
        """ 
        Initialize an VanillaOption object.
        Args: 
        - underlying (str) : Underlying type for the option. 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)
        self._underlying = underlying.lower()
        self._strike = self._get_strike()
        self._option_type = self._inputs.get("option_type").lower()
    
    def _get_strike(self):
        """ Get the strike price. """
        if self._underlying == FOREX :
            if not "domestic_rate" in self._inputs :
                raise Exception("Missing inputs : domestic_rate" )
            elif not "maturity" in self._inputs :
                raise Exception("Missing inputs : maturity" )
            return self._inputs["strike"] * np.exp(self._inputs["domestic_rate"] * self._inputs["maturity"].maturity())
        else : 
            return self._inputs["strike"]
                
    def payoff(self, spot):
        """ Calculate and returns the payoff of the option. """
        if self._option_type == CALL : 
            return np.maximum(spot - self._strike, 0)
        elif self._option_type == PUT :
            return np.maximum(self._strike - spot, 0)
        else : 
            raise ValueError("Choose an option type (call or put)")



class KnockOutOption(AbstractProduct):
    """ A class representing a KO option financial product. """
    
    def __init__(self, inputs):
        """ 
        Initialize a KnockOutOption object.
        Args: 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)
        self.barrier = inputs['barrier']
        self.strike = inputs['strike']
    
    def payoff(self, paths):
        """ Calculates the payoff considering the barrier. 'paths' is a NumPy array of simulated end prices """
        payoffs = np.maximum(paths - self.strike, 0)  
        knock_out_mask = np.any(paths >= self.barrier, axis=1)
        payoffs[knock_out_mask] = 0
        return payoffs


class KnockInOption(AbstractProduct):
    """ A class representing a KI option financial product. """
    
    def __init__(self, inputs):
        """ 
        Initialize a KnockInOption object.
        Args: 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)
        self.barrier = inputs['barrier']
        self.strike = inputs['strike']

    def payoff(self, paths):
        """ For KI options, the option is only valid if the barrier is breached """
        payoffs = np.maximum(paths[:, -1] - self.strike, 0)  
        knock_in_mask = np.any(paths >= self.barrier, axis=1)
        payoffs[~knock_in_mask] = 0 
        return payoffs