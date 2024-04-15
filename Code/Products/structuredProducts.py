from Products.optionalProducts import AbstractProduct

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
