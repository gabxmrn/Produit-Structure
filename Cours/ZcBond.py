from maturity import Maturity
from rate import Rate


class ZcBond:
    """
    A class representing a zero-coupon bond.

    Attributes:
        __rate (Rate): The rate object representing the interest rate used for discounting.
        __maturity (Maturity): The maturity object representing the maturity of the bond.
        __nominal (float): The nominal value of the bond.
    """

    def __init__(self, rate:Rate, maturity:Maturity, nominal:float):
        self.__rate=rate
        self.__maturity=maturity
        self.__nominal=nominal

    def price(self, force_rate:float=None):
        return self.__nominal*self.__rate.discount_factor(
            self.__maturity,
            force_rate=force_rate
        )