from maturity import Maturity
from Bond import FixedBond
from rate import Rate


class FloatingBond:
    def __init__(
        self,
        libor_rate:float,
        maturity:Maturity,
        nominal:float,
        nb_coupon:int,
        rate:Rate):

        self.__libor_rate=libor_rate
        self.__libor_maturity=maturity
        self.__nominal=nominal
        self.__nb_coupon=nb_coupon
        self.__rate=rate
        self.__equivalent_fixed_bond=FixedBond(libor_rate, maturity, nominal, nb_coupon, rate)
        self.__price=None

    def price(self):
        if self.__price==None:
            #self.__price=self.__nominal*(1+self.__libor_rate/self.__nb_coupon) \
            #                *rate.discount_factor(self.__libor_maturity)
            self.__price=self.__equivalent_fixed_bond.price()
        return self.__price