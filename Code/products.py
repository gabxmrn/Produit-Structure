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


class OptionProducts(AbstractProduct):
    """ A class representing a Straddle or a Strangle financial product. """

    def __init__(self, type:str, long_short:str, inputs: dict):
        """ 
        Initialize a Spread object.
        Args: 
        - type (str) : product type (straddle or strangle).
        - long_short (str) : Long or short product. 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)

        # Call
        self._call = self._inputs.get("call")
        self._call_price = self._inputs.get("call price")

        # Put
        self._put = self._inputs.get("put")
        self._put_price = self._inputs.get("put price")

        # Check product type
        if type.lower() not in ["straddle", "strangle", "strip", "strap"]:
            raise Exception("Input Error : Please select straddle, strangle, strip, or strap as a product.")
                    
        # Check if product is long or short
        self._longshort = long_short.lower()
        if self._longshort not in ["long", "short"]:
            raise Exception("Input Error : Please select if product is long or short.")
        
        # Check options type
        if self._call._option_type != "call" or self._put._option_type != "put":
            raise Exception("Input Error : Please enter a call and a put.")
        
        # Check strikes
        self._type = type
        if self._type == "straddle" or self._type == "strip" or self._type == "strap":
            if self._call._strike != self._put._strike:
                raise Exception("Input Error : For a straddle, the strike should be the same for the put and the call.")
        elif self._type == "strangle":
            if self._call._strike <= self._put._strike:
                raise Exception("Input Error : For a strangle, the call strike should be higher than the put strike.")

    def payoff(self, spot:float) -> float:
        """ Calculate and returns the payoff of an option product. """
        if self._type == "straddle" or self._type == "strangle":
            payoff = self._call.payoff(spot) + self._put.payoff(spot)
        elif self._type == "strip":
            payoff = self._call.payoff(spot) + self._put.payoff(spot) * 2
        elif self._type == "strap":
            payoff = self._call.payoff(spot) * 2 + self._put.payoff(spot)
            
        if self._longshort == "long":
            return payoff
        else:
            return -payoff

    def price(self) -> float:
        """ Calculate and returns the price of an option product. """
        if self._type == "straddle" or self._type == "strangle":
            price = self._call_price + self._put_price
        elif self._type == "strip":
            price = self._call_price + self._put_price * 2
        elif self._type == "strap":
            price = self._call_price * 2 + self._put_price
        
        if self._longshort == "long":
            return price
        else:
            return -price


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

        # Check option type
        self._type = type.lower()
        if self._type == "call spread":
            if (self._long_leg._option_type != "call" or self._short_leg._option_type != "call"):
                raise Exception("Input error : Call spread takes two calls as an argument.")
        elif self._type == "put spread":
            if (self._long_leg._option_type != "put" or self._short_leg._option_type != "put"):
                raise Exception("Input error : Put spread takes two puts as an argument.")
        else:
            raise Exception("Input error : Please enter 'put spread' or 'call spread'.")

        # Check strike
        if self._type == "call spread":
            if self._short_leg._strike <= self._long_leg._strike:
                raise Exception("Input error : Short leg strike must be greater than long leg strike.")
        elif self._type == "put spread":
            if self._long_leg._strike <= self._short_leg._strike:
                raise Exception("Input error : Long leg strike must be greater than short leg strike.")
        else:
            raise Exception("Input error : Please enter 'put spread' or 'call spread'.")

    def payoff(self, spot:float) -> float:
        """ Calculate and returns the payoff of the spread. """
        return self._long_leg.payoff(spot) - self._short_leg.payoff(spot)

    def price(self) -> float:
        """ Calculate and returns the price of the spread. """
        return self._short_leg_price - self._long_leg_price
    
    
class ButterflySpread(AbstractProduct):
    """ A class representing a Butterfly Spread financial product. """

    def __init__(self, inputs: dict):
        """ 
        Initialize a Butterfly Spread object.
        Args: 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)

        # Put spread
        self._put_spread = self._inputs.get("put spread")

        # Call spread
        self._call_spread = self._inputs.get("call spread")

        # Check product type
        if self._call_spread._type != "call spread" or self._put_spread._type != "put spread":
            raise Exception("Input error : please enter a put spread and a call spread.")

        # Check strikes
        if self._put_spread._short_leg._strike != self._call_spread._short_leg._strike:
            raise Exception("Input error : The strike of the put spread short leg should be equal to the strike of the call spread short leg.")

    def payoff(self, spot:float) -> float:
        """ Calculate and returns the payoff of the butterfly spread. """
        return self._put_spread.payoff(spot) + self._call_spread.payoff(spot)

    def price(self)  -> float:
        """ Calculate and returns the price of the butterfly spread. """
        return self._put_spread.price() + self._call_spread.price()


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