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
        Initialize a VanillaOption object.
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


class Spread(AbstractProduct):
    """ A class representing a Spread (Call/Put) option financial product. """
    
    def __init__(self, type:str, inputs: dict) -> None:
        """ 
        Initialize a Spread object.
        Args: 
        - type (str) : Type of spread. 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)
        # Long leg (acheté)
        self._long_leg = self._inputs.get("long leg")
        self._long_leg_price = self._inputs.get("long leg price")

        # Short leg (vendu)
        self._short_leg = self._inputs.get("short leg")
        self._short_leg_price = self._inputs.get("short leg price")

        # Product type verification
        if type.lower() == "call spread":
            if (self._long_leg._option_type != "call" or self._short_leg._option_type != "call"):
                raise Exception("Input error : Call spread takes two calls as an argument.")
        elif type.lower() == "put spread":
            if (self._long_leg._option_type != "put" or self._short_leg._option_type != "put"):
                raise Exception("Input error : Put spread takes two puts as an argument.")
        else:
            raise Exception("Input error : Please enter 'put spread' or 'call spread'.")

        # Strike verification
        if type.lower() == "call spread":
            if self._short_leg._strike <= self._long_leg._strike:
                raise Exception("Input error : Short leg strike must be greater than long leg strike.")
        elif type.lower() == "put spread":
            if self._long_leg._strike <= self._short_leg._strike:
                raise Exception("Input error : Long leg strike must be greater than short leg strike.")
        else:
            raise Exception("Input error : Please enter 'put spread' or 'call spread'.")

    def payoff(self, spot) -> float:
        """ Calculate and returns the payoff of the spread. """
        payoff_long = max(spot - self._long_leg.strike, 0)
        payoff_short = max(spot - self._short_leg.strike, 0)
        return payoff_long - payoff_short

    def price(self) -> float:
        """ Calculate and returns the price of the spread. """
        return self._short_leg_price - self._long_leg_price


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