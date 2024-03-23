from Maturity import Maturity
from Rate import Rate
from Optim import Optim
from ZCbond import ZcBond

# Classe à finir + faire les obligations à taux variable

class FixedBond:

    def __init__(
            self,
            coupon_rate: float,
            maturity: Maturity,
            nominal: float,
            nb_coupon: int,
            rate: Rate
            ) -> None:
        
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal
        self.__coupon_rate = coupon_rate
        self.__nb_coupon = nb_coupon

        self.__price = None
        self.__ytm = None


    def price(
            self,
            force_rate: float = None):
        
        pass


    def ytm (self):
        pass


    def  __run_coupon(self):

        t = self.__maturity.maturity() # Get maturity in year
        step = t / self.__nb_coupon # Step size for each coupon payment

        # Get the period of each coupon payment
        terms = []
        while t > 0:
            terms[t]
            t -= step
        sorted(terms)

        # Coupon Frequency
        freq_coupon = float(self.__coupon_rate) / self.__nb_coupon * self.__nominal

        # Get the coupon payment for each term
        coupons = []
        for term in terms:
            coupons.append
            (
                {
                    'maturity': term,
                    'cf_type': 'coupon',
                    'zc_bond': ZcBond(
                        self.__rate,
                        Maturity(maturity_in_years = t),
                        freq_coupon + (
                            0.0
                            if t < self.__maturity.maturity()
                            else self.__nominal)
                        )
                }
            )

        return coupons
