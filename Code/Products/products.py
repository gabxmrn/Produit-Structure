import numpy as np


FOREX = "forex rate"
CALL = "call"
PUT = "put"

class AbstractProduct:
    """ Abstract class representing a financial product. """
    _product_name = "product"
    _inputs = None

    def __init__(self, inputs: dict) -> None: 
        """ 
        Initialize an AbstractProduct object.
        Args: 
        - inputs (dict): Input parameters for the product.
        """
        self._inputs = inputs


    def payoff(self, spot: float) -> float:
        """
        Method to calculate the payoff of the product.

        Args:
            spot (float): Current spot price.

        Returns:
            float: Payoff of the product.
        """
        
        raise Exception("Not implemented")


class VanillaOption(AbstractProduct):
    """ A class representing a Vanilla Option (Call/Put) option financial product.
    Arguments:
        _underlying (str): type of underlying asset for the option.
        _strike (float): strike of the option.
        _optio_type (str): type of option (call or put).
    """
    
    def __init__(self, underlying: str, inputs: dict) -> None :
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

    def _get_strike(self) -> float:
        """ Get the strike price. """
        if self._underlying == FOREX :
            if not "domestic_rate" in self._inputs :
                raise Exception("Missing inputs : domestic_rate" )
            elif not "maturity" in self._inputs :
                raise Exception("Missing inputs : maturity" )
            return self._inputs["strike"] * np.exp(self._inputs["domestic_rate"] * self._inputs["maturity"].maturity())
        else : 
            return self._inputs["strike"]
                
    def payoff(self, spot: float) -> float:
        """ Calculate and returns the payoff of the option. """
        if self._option_type == CALL : 
            return np.maximum(spot - self._strike, 0)
        elif self._option_type == PUT :
            return np.maximum(self._strike - spot, 0)
        else : 
            raise ValueError("Choose an option type (call or put)")


class OptionProducts(AbstractProduct):
    """ A class representing a Straddle or a Strangle financial product.
    Arguments:
        _call (VanillaOption) : call component of the strategy.
        _call_price (float): price of the call.
        _put (VanillaOption): put component of the strategy.
        _put_price (float): price of the put.
        _type (str): type of option strategy (straddle, strangle, strip, strap).
        _long_short (str) : if the product is long or short.
    """

    def __init__(self, type: str, long_short: str, inputs: dict) -> None:
        """ 
        Initialize a OptionProducts object.
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
        self._type = type.lower()
        if self._type not in ["straddle", "strangle", "strip", "strap"]:
            raise Exception("Input Error : Please select straddle, strangle, strip, or strap as a product.")
                    
        # Check if product is long or short
        self._longshort = long_short.lower()
        if self._longshort not in ["long", "short"]:
            raise Exception("Input Error : Please select if product is long or short.")
        
        # Check options type
        if self._call._option_type != "call" or self._put._option_type != "put":
            raise Exception("Input Error : Please enter a call and a put.")
        
        # Check strikes
        if self._type == "straddle" or self._type == "strip" or self._type == "strap":
            if self._call._strike != self._put._strike:
                raise Exception("Input Error : For a straddle, the strike should be the same for the put and the call.")
        elif self._type == "strangle":
            if self._call._strike <= self._put._strike:
                raise Exception("Input Error : For a strangle, the call strike should be higher than the put strike.")

    def payoff(self, spot: float) -> float:
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


class BinaryOption(AbstractProduct):
    """ A class representing binary option financial product.
    Arguments:
        _strike (float): strike of the financial product.
        _option_type (str): binary option type (binary call, binary put, one touch, no touch, double_one_touch, double_no_touch).
        _barrier (float) : barrier of the option.
        _lower_barrier (float) : lower barrier of the option.
        _upper_barrier (float) : upper barrier of the option.
        _payoff_amount (float): payoff amount.
    """

    def __init__(self, inputs: dict) -> None:
        """ 
        Initialize a Spread object.
        Args: 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)
        self._strike = self._inputs.get("strike")
        self._option_type = self._inputs.get("option_type").lower()
        self._barrier = self._inputs.get("barrier")
        self._lower_barrier =self._inputs.get("lower_barrier")
        self._upper_barrier =self._inputs.get("upper_barrier")
        self._payoff_amount =self._inputs.get("payoff_amount")    
    
    def __validate_parameters(self):
        """ Check for required parameters based on option type. """
        if self._option_type in ["one_touch", "no_touch"] and self._barrier is None:
            raise ValueError(f"Barrier value required for {self._option_type} option.")
        if self._option_type in ["double_one_touch", "double_no_touch"] and \
           (self._lower_barrier is None or self._upper_barrier is None):
            raise ValueError(f"Both lower and upper barrier values required for {self._option_type} option.")
    
    def payoff(self, spot: float)-> float:
        """
        Calculates the payoff of the binary option based on the final spot price.

        Parameters:
        - spot (float): The final spot price of the underlying asset at expiration.

        Returns:
        - float: The payoff of the option.
        """
        self.__validate_parameters()
        spot_array = np.asarray(spot)

        if self._option_type == "binary_call":
            return np.where(spot_array > self._strike, self._payoff_amount, 0)
        elif self._option_type == "binary_put":
            return np.where(spot_array < self._strike, self._payoff_amount, 0)
        elif self._option_type == "one_touch":
            return np.where(spot_array >= self._barrier, self._payoff_amount, 0)
        elif self._option_type == "no_touch":
            return np.where(spot_array < self._barrier, self._payoff_amount, 0) 
        elif self._option_type == "double_one_touch":
            return np.where((spot_array <= self._lower_barrier) | (spot_array >= self._upper_barrier), self._payoff_amount, 0)
        elif self._option_type == "double_no_touch":
            return np.where((spot_array > self._lower_barrier) & (spot_array < self._upper_barrier), self._payoff_amount, 0)
        else:
            raise ValueError("Unsupported option type")


class Spread(AbstractProduct):
    """ A class representing a Spread (Call/Put) option financial product.
    Attributes :
        _long_leg (VanillaOption) : long leg of the spread.
        _long_leg_price (float) : price of the long leg of the spread.
        _short_leg (VanillaOption): short leg of the spread.
        _short_leg_price (float) : price of the short leg of the spread.
        _type : if the spread is a call or a put spread.
    """
    
    def __init__(self, type: str, inputs: dict) -> None:
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

    def payoff(self, spot: float) -> float:
        """ Calculate and returns the payoff of the spread. """
        return self._long_leg.payoff(spot) - self._short_leg.payoff(spot)

    def price(self) -> float:
        """ Calculate and returns the price of the spread. """
        return self._long_leg_price - self._short_leg_price
        
    
class ButterflySpread(AbstractProduct):
    """ A class representing a Butterfly Spread financial product.
    Attributes :
        _put_spread (Spread): Put spread part of the butterfly.
        _call_spread(Spread): Call spread part of the butterfly.
    """

    def __init__(self, inputs: dict) -> None:
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

    def payoff(self, spot: float) -> float:
        """ Calculate and returns the payoff of the butterfly spread. """
        return self._put_spread.payoff(spot) + self._call_spread.payoff(spot)

    def price(self)  -> float:
        """ Calculate and returns the price of the butterfly spread. """
        return self._put_spread.price() + self._call_spread.price()


class KnockOutOption(AbstractProduct):
    """ A class representing a KO option financial product.
    Attributes :
        barrier (float): barrier of the strike.
        strike (float): option strike.
    """
    
    def __init__(self, inputs: dict) -> None:
        """ 
        Initialize a KnockOutOption object.
        Args: 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)
        self.barrier = inputs['barrier']
        self.strike = inputs['strike']
        self._option_type = None
    
    def payoff(self, paths) -> float:
        """ Calculates the payoff considering the barrier. 'paths' is a NumPy array of simulated end prices """
        payoffs = np.maximum(paths - self.strike, 0)  
        knock_out_mask = np.any(paths >= self.barrier, axis=1)
        payoffs[knock_out_mask] = 0
        return payoffs


class KnockInOption(AbstractProduct):
    """ A class representing a KI option financial product.
    Attributes :
        barrier (float): barrier of the strike.
        strike (float): option strike.
    """
    
    def __init__(self, inputs: dict) -> None:
        """ 
        Initialize a KnockInOption object.
        Args: 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)
        self.barrier = inputs['barrier']
        self.strike = inputs['strike']
        self._option_type = None

    def payoff(self, paths) -> float:
        """ For KI options, the option is only valid if the barrier is breached """
        payoffs = np.maximum(paths[:, -1] - self.strike, 0)  
        knock_in_mask = np.any(paths >= self.barrier, axis=1)
        payoffs[~knock_in_mask] = 0 
        return payoffs


class ReverseConvertible(AbstractProduct):
    """ A class representing a Structured Product.
    Attributes:
        _short_put (VanillaOption): Put.
        _short_put_price (float): Price of the put.
        _bond (FixedBond): Bond of same caracteristics as the put.
        _bond_price (float): Bond price.
        _coupon (float) : additional coupon provided.
     """

    def __init__(self, inputs: dict):
        """ 
        Initialize a Reverse Convertible object.
        Args: 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)

        # Short put
        self._short_put = self._inputs.get("put")
        self._short_put_price = self._inputs.get("put price")

        if self._short_put._option_type != "put":
            raise Exception("Input error: please enter a put option.")

        # Long bond
        self._bond = self._inputs.get("bond")
        self._bond_price = self._inputs.get("bond price")

    def payoff(self, spot: float) -> float:
        """ Calculate and returns the payoff of the reverse convertible. """
        return - self._short_put.payoff(spot) + self._bond.nominal

    def price(self) -> float:
        """ Calculate and returns the price of the reverse convertible. """
        return - self._bond.price() + self._short_put_price


class CertificatOutperformance(AbstractProduct):
    """ A class representing a Certificat Outperformance financial product.
    Arguments:
        _zs_call (VanillaOption): zero strike call object.
        _zs_call_price (float): price of the call with a zero strike.
        _call (VanillaOption): call object.
        _call_price (float): price of the call.
    """

    def __init__(self, inputs: dict) -> None:
        """ 
        Initialize a Certificat Outperformance object.
        Args: 
        - inputs (dict): Input parameters for the product.
        """
        super().__init__(inputs)

        # Zero-strike call (long)
        self._zs_call = self._inputs.get("zero strike call")
        self._zs_call_price = self._inputs.get("zero strike call price")

        if self._zs_call._strike != 0:
            raise Exception("Input error: The strike of this call must be zero.")
        
        # ATM Call (long)
        self._call = self._inputs.get("call")
        self._call_price = self._inputs.get("call price")

        # Check option type
        if self._zs_call._option_type != "call" or self._call._option_type != "call":
            raise Exception("Input error : the certificat outperformance must be composed of two calls.")
        
    def participation_level(self) -> float:
        """ Calculate and returns the participation level of the certificat outperformance. """
        return self._zs_call_price / self._call_price

    def payoff(self, spot: float) -> float:
        """ Calculate and returns the payoff of the certificat outperformance. """
        return self._zs_call.payoff(spot) + (self.participation_level() - 1) * self._call.payoff(spot)

    def price(self) -> float:
        """ Calculate and returns the price of the certificat outperformance. """
        return self._zs_call_price + (self.participation_level() - 1) * self._call_price
