import numpy as np

class AbstractProduct:
    """ Abstract class representing a financial product. """
    _product_name = "product"
    _inputs = None

    def __init__(self, inputs:dict, optional_inputs:dict = None):
        """ 
        Initialize an AbstractProduct object.
        Args: inputs (dict): Input parameters for the product.
        """
        self._inputs = inputs
        self._optional_inputs = optional_inputs
        

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
    
    def __init__(self, inputs):
        """
        Initialize a VanillaOption object.
        Args: inputs (dict): Input parameters for the option.
        """
        super().__init__(inputs)
        self.option_type = inputs['option_type'].lower()
        
    def _strike(self):
        """ Get the strike price. """
        if not self._optional_inputs is None and "domestic_rate" in self._optional_inputs :
            # Option sur taux de change 
            return self._inputs.get("strike") * np.exp(-self._optional_inputs("domestic_rate") * self._optional_inputs("maturity").maturity())
        else : 
            return self._inputs.get("strike")
        
    def payoff(self, spot):
        """ 
        Calculate and returns the payoff of the Call option.
        Args: spot (float): Current spot price.
        """
        if self._inputs.get("option_type").lower() == "call": # self.option_type == "call" :
            return np.maximum(spot - self._strike(), 0)
        elif self._inputs.get("option_type").lower() == "put" :
            return np.maximum(self._strike() - spot, 0)
        else : 
            raise ValueError("Choose an option type (call or put)")



class KnockOutOption(AbstractProduct):
    def __init__(self, inputs):
        """ A class representing a KO option financial product. """
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
    def __init__(self, inputs):
        """ A class representing a KI option financial product. """
        super().__init__(inputs)
        self.barrier = inputs['barrier']
        self.strike = inputs['strike']

    def payoff(self, paths):
        """ For KI options, the option is only valid if the barrier is breached """
        payoffs = np.maximum(paths[:, -1] - self.strike, 0)  
        knock_in_mask = np.any(paths >= self.barrier, axis=1)
        payoffs[~knock_in_mask] = 0 
        return payoffs