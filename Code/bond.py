from maturity import Maturity
from rate import Rate
from optim import Optim


class FixedBond:
    """
    A class representing a fixed-rate bond for financial calculations.
    
    Attributes:
       rate (Rate): The rate object representing the interest rate.
       maturity (Maturity): The maturity object representing the bond's maturity.
       nominal (float): The nominal value of the bond.
       coupon_rate (float): The coupon rate of the bond.
       nb_coupon (int): The number of coupon payments.
       coupon (list): List of coupon payments as zero-coupon bonds.
       price (float): The price of the bond.
       ytm (float): The yield to maturity of the bond.
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
        
        self.rate = rate
        self.maturity = maturity
        self.nominal = nominal
        self.coupon_rate = coupon_rate
        self.nb_coupon = nb_coupon
        
        # # Generate coupon payments :
        self.coupon = self.run_coupon()
        
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
            price = sum([zc_bond["zc_bond"].price(force_rate=force_rate) for zc_bond in self.coupon])
            
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


    def  run_coupon(self):
        """
        Generate coupon payments represented as zero-coupon bonds.

        Returns:
            list: List of dictionaries containing coupon payments.
        """

        t = self.maturity.maturity() # Get maturity in year
        step = t / self.nb_coupon # Step size for each coupon payment

        # Get the period of each coupon payment
        terms = sorted([abs(t - i * step) for i in range(self.nb_coupon)], reverse=True) + [0.0]

        # Coupon Frequency
        freq_coupon = float(self.coupon_rate) / self.nb_coupon * self.nominal

        # Get the coupon payment for each term
        coupons= [
            {
                "maturity" : term,
                "cf_type" : "coupon",
                "zc_bond" : ZcBond(
                    self.rate, 
                    Maturity(maturity_in_years=term), 
                    freq_coupon + (0.0 if term < self.maturity.maturity() else self.nominal))
            }
            for term in terms
        ]
        
        return coupons


class ZcBond:
    """
    A class representing a zero-coupon bond.

    Attributes:
        rate (Rate): The rate object representing the interest rate used for discounting.
        maturity (Maturity): The maturity object representing the maturity of the bond.
        nominal (float): The nominal value of the bond.

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


    def price(self, force_rate: float = None) -> float:
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