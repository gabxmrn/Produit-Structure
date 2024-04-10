from bond import FixedBond
from products import VanillaOption
from brownianMotion import BrownianMotion

from math import exp, log, sqrt, pi
from scipy.stats import norm

CAPITALIZED_INDEX = "capitalized index"
SHARE_DIV = "dividend share"


class BondRisk:
    """
    A class representing risk analysis for fixed-income securities.
    
    Attributes:
        __m (float): Time to next coupon payment.
        __r_ytm (float): Yield to maturity.
        __coupon_list (list): List of coupon payments.
        __price (float): Bond price.
    """
    
    def __init__ (self, bond:FixedBond) :
        """
        Initialize BondRisk object.

        Args:
            bond (FixedBond): The fixed-income bond to analyze.
        """
        self.__m = bond.maturity.maturity() / bond.nb_coupon 
        self.__r_ytm = bond.ytm()
        self.__coupon_list = bond.run_coupon()
        self.__price = bond.price()
        
        
    def duration(self, force_rate:float=None) -> float :     
        """
        Calculate and returns the duration of the bond.
        Args: force_rate (float, optional): An optional parameter to specify a specific rate for duration calculation.
        """ 
        numerator = 0
        for coupon_t in self.__coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            numerator += coupon * exp(-self.__r_ytm / self.__m * t) * t 
        return numerator / self.__price
    
    def convexity(self, force_rate:float=None) -> float :  
        """
        Calculate and returns the convexity of the bond.
        Args: force_rate (float, optional): An optional parameter to specify a specific rate for duration calculation.
        """       
        numerator = 0
        for coupon_t in self.__coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            numerator += coupon * exp(-self.__r_ytm / self.__m * t) * t**2
        
        return numerator


class OptionRisk:
    """
    A class representing risk analysis for options.
    
    Attributes:
        __type (str): The type of option (call or put).
        __strike (float): The strike price of the option.
        __spot (float): The current spot price.
        __maturity (float): The maturity of the option.
        __rate (float): The interest rate.
        __volatility (float): The volatility of the underlying asset.
        __df (float): The discount factor.
        __dividend (float): The coefficient for underlying with dividend .
    """
    
    
    def __init__ (self, option:VanillaOption, process:BrownianMotion) -> None :
        """
        Initialize OptionRisk object.

        Args:
            option (VanillaOption): The vanilla option to analyze.
            process (BrownianMotion): The Brownian motion process.
        """
        
        self.__type = option._option_type
        self.__strike = option._strike
        self.__spot = process.input("spot")
        self.__maturity = process.input("maturity").maturity()
        self.__rate = process.input("rates").rate(self.__maturity) 
        self.__volatility = process.input("volatility")
        self.__spot, self.__rate = process._check_underlying(option, self.__spot, self.__rate)
        self.__df = process.input("rates").discount_factor(maturity=process.input("maturity"), force_rate=self.__rate)
        
        self.__dividend = 1.0
        if option._underlying == CAPITALIZED_INDEX or option._underlying  == SHARE_DIV :
            self.__dividend = exp(-process.input("dividend") * self.__maturity) 
                
    def _get_d1(self) -> float : 
        """Calculate d1 parameter."""
        return (log(self.__spot/self.__strike) + (self.__rate + self.__volatility**2 / 2) * self.__maturity) / (self.__volatility * sqrt(self.__maturity)) 

    def _get_d2(self) -> float :
        """Calculate d2 parameter."""
        d1 = self._get_d1()
        return d1 - self.__volatility * sqrt(self.__maturity)

    def _get_Nd1(self) -> float :
        """Calculate N(d1)."""
        d1 = self._get_d1()
        return  norm.cdf(d1, loc=0, scale=1) 
    
    def _get_Nd2(self) -> float :
        """Calculate N(d2)."""
        d2 = self._get_d2()
        return norm.cdf(d2, loc=0, scale=1) 
    
    def _get_dNd1(self) -> float :
        """Calculate dN(d1)."""
        d1 = self._get_d1()
        return 1 / sqrt(2 * pi) * exp(-d1**2 / 2)
    
    def greeks(self) -> str : 
        """Return all option greeks."""
        return f"Delta = {round(self.delta(), 2)}, gamma = {round(self.gamma(), 2)}, vega = {round(self.vega(), 2)}, theta = {round(self.theta(), 2)}, rho = {round(self.rho(), 2)}"
    
    def delta(self) -> float :
        """Calculate option delta."""
        Nd1 = self._get_Nd1()
        if self.__type == "call" :
            return  self.__dividend * Nd1 
        elif self.__type == "put" : 
            return self.__dividend * (Nd1 - 1)
        
    def gamma(self) -> float :
        """Calculate option gamma."""
        dNd1 = self._get_dNd1()
        return self.__dividend * (dNd1 / (self.__spot * self.__volatility * sqrt(self.__maturity)))
        
    def vega(self) -> float :
        """Calculate option vega."""
        dNd1 = self._get_dNd1()
        return self.__dividend * self.__spot * sqrt(self.__maturity) * dNd1
    
    def theta(self) -> float : 
        """Calculate option theta."""
        dNd1, Nd2 = self._get_dNd1(), self._get_Nd2()
        if self.__type == "call" :
            return self.__dividend * (- (self.__spot * dNd1 * self.__volatility) / (2 * sqrt(self.__maturity)) - self.__rate * self.__strike * self.__df * Nd2)
        elif self.__type == "put" : 
            return self.__dividend * (- (self.__spot * dNd1 * self.__volatility) / (2 * sqrt(self.__maturity)) + self.__rate * self.__strike * self.__df * (1 - Nd2))
    
    def rho(self) -> float :
        """Calculate option rho."""
        Nd2 = self._get_Nd2()
        if self.__type == "call" :
            return self.__dividend * (self.__strike * self.__maturity * self.__df * Nd2)
        elif self.__type == "put" : 
            return self.__dividend * (- self.__strike * self.__maturity * self.__df * (1 - Nd2))