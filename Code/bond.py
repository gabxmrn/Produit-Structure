from maturity import Maturity
from rate import Rate
from optim import Optim
from zcBond import ZcBond

from math import exp 

# TO DO : rajouter une méthode pour calculer la sensibilité / la duration de l'obligation

class FixedBond:
    """
    A class representing a fixed-rate bond for financial calculations.
    
    Attributes:
       __rate (Rate): The rate object representing the interest rate.
       __maturity (Maturity): The maturity object representing the bond's maturity.
       __nominal (float): The nominal value of the bond.
       __coupon_rate (float): The coupon rate of the bond.
       __nb_coupon (int): The number of coupon payments.
       __coupon (list): List of coupon payments as zero-coupon bonds.
       __price (float): The price of the bond.
       __ytm (float): The yield to maturity of the bond.
    """

    def __init__(
            self,
            coupon_rate: float,
            maturity: Maturity,
            nominal: float,
            nb_coupon: int,
            rate: Rate
            ) -> None:
        """
        Initialize a FixedBond object.

        Args:
            coupon_rate (float): The coupon rate of the bond.
            maturity (Maturity): The maturity of the bond.
            nominal (float): The nominal value of the bond.
            nb_coupon (int): The number of coupon payments.
            rate (Rate): The interest rate object used for calculations.
        """
        
        self.__rate = rate
        self.__maturity = maturity
        self.__nominal = nominal
        self.__coupon_rate = coupon_rate
        self.__nb_coupon = nb_coupon
        
        # # Generate coupon payments :
        self.__coupon = self.__run_coupon()

        self.__price = None
        self.__ytm = None


    def price(self, force_rate:float = None):
        """
        Calculate the price of the bond.

        Args:
            force_rate (float, optional): An optional parameter to specify a specific rate for price calculation. Defaults to None.

        Returns:
            float: The price of the bond.
        """
        
        if self.__price is None or force_rate is not None:
            price = sum([zc_bond["zc_bond"].price(force_rate=force_rate) for zc_bond in self.__coupon])
            
            if force_rate is not None:
                return price
            else:
                self.__price = price
                
        return self.__price


    def ytm (self):
        """
        Calculate the yield to maturity of the bond.

        Returns:
            float: The yield to maturity of the bond.
        """

        
        if self.__ytm == None:
            # Define an optimization function to find the yield to maturity :
            fct_obj = lambda rate: self.price(force_rate=rate)
            obj = Optim(fct_pricing=fct_obj, target_value=self.__price, init_value=0.01)
            opt_res = obj.run()
            if not opt_res["success"]:
                raise Exception("Not found YTM")
            self.__ytm = opt_res["x"][0]
            
        return self.__ytm
    
    
    def duration(self, force_rate:float=None):
        # Vraiment pas sure de la formule 
        
        m = self.__maturity.maturity() / self.__nb_coupon 
        c = self.__coupon
        r_ytm = self.ytm()
        FV = self.__nominal
        N = self.__nb_coupon
        coupon_list = self.__run_coupon()
        
        denominator = 0
        
        for coupon_t in coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            denominator += coupon / m * exp(-r_ytm / m * t) * t * FV * exp(- r_ytm / m * N) * t
        
        return denominator / self.price()
    
    def convexite(self, force_rate:float=None):
        # Vraiment pas sure de la formule 
        
        m = self.__maturity.maturity() / self.__nb_coupon 
        c = self.__coupon
        r_ytm = self.ytm()
        FV = self.__nominal
        N = self.__nb_coupon
        coupon_list = self.__run_coupon()
        
        denominator = 0
        
        for coupon_t in coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            denominator += coupon / m * exp(-r_ytm / m * t) * t**2 * FV * exp(- r_ytm / m * N) * t**2
        
        return denominator 
    


    def  __run_coupon(self):
        """
        Generate coupon payments represented as zero-coupon bonds.

        Returns:
            list: List of dictionaries containing coupon payments.
        """

        t = self.__maturity.maturity() # Get maturity in year
        step = t / self.__nb_coupon # Step size for each coupon payment

        # Get the period of each coupon payment
        terms = sorted([abs(t - i * step) for i in range(self.__nb_coupon)], reverse=True) + [0.0]

        # Coupon Frequency
        freq_coupon = float(self.__coupon_rate) / self.__nb_coupon * self.__nominal

        # Get the coupon payment for each term
        coupons= [
            {
                "maturity" : term,
                "cf_type" : "coupon",
                "zc_bond" : ZcBond(
                    self.__rate, 
                    Maturity(maturity_in_years=term), 
                    freq_coupon + (0.0 if term < self.__maturity.maturity() else self.__nominal))
            }
            for term in terms
        ]
        
        return coupons
