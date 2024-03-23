from Maturity import Maturity
from Rate import Rate


class ZcBond:
    """
    A class representing a zero-coupon bond.

    Attributes:
        __rate (Rate): The rate object representing the interest rate used for discounting.
        __maturity (Maturity): The maturity object representing the maturity of the bond.
        __nominal (float): The nominal value of the bond.

    """

    def __init__(
            self, 
            rate: Rate, 
            maturity: Maturity, 
            nominal: float):
        """
        Initialize a ZcBond object.

        Args:
            rate (Rate): The rate object representing the interest rate used for discounting.
            maturity (Maturity): The maturity object representing the maturity of the bond.
            nominal (float): The nominal value of the bond.
        """
        
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal


    def price(
            self,
            force_rate: float = None
            ) -> float:
        """
        Calculate the price of the zero-coupon bond.

        Args:
            force_rate (float, optional): An optional parameter to specify a specific rate for discount factor calculation.
                If provided, the price will be calculated using the given rate.
                If not provided, the price will be calculated using the rate associated with the bond.

        Returns:
            float: The calculated price of the zero-coupon bond.
        """
        return self.__nominal * self.__rate.discount_factor(self.__maturity, force_rate = force_rate)