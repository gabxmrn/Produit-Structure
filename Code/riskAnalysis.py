from math import exp, log, sqrt, pi
from scipy.stats import norm

from bond import FixedBond
from products import VanillaOption, Spread, ButterflySpread, OptionProducts, ReverseConvertible, CertificatOutperformance
from brownianMotion import BrownianMotion


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
        

class OptionProductsRisk:
    """
    A class representing risk analysis for option products.
    
    Attributes:
        _call (VanillaOption): The call part of the financial product.
        _put (VanillaOption): The put part of the financial product.
        _longshort (str) : If the product is long or short.
        _type (str) : The product type (straddle, strangle, strip or strap).
    """ 
    
    def __init__ (self, product:OptionProducts, process:BrownianMotion) -> None :
        """
        Initialize OptionProductsRisk object.

        Args:
            option (OptionProducts): The option to analyze.
            process (BrownianMotion): The Brownian motion process.
        """
        
        # Product caracteristics
        self._call = product._call
        self._put = product._put
        self._longshort = product._longshort
        self._type = product._type

        # Greeks
        self._call_greeks = OptionRisk(self._call, process)
        self._put_greeks = OptionRisk(self._put, process)

        # Check product type
        if self._type not in ["straddle", "strangle", "strip", "strap"]:
            raise Exception("Input error : Please enter a straddle, strangle, strap or strip product.")
    
    def greeks(self) -> str : 
        """Return all product greeks."""
        return f"Delta = {round(self.delta(), 2)}, gamma = {round(self.gamma(), 2)}, vega = {round(self.vega(), 2)}, theta = {round(self.theta(), 2)}, rho = {round(self.rho(), 2)}"
    
    def delta(self) -> float :
        """Calculate product delta."""
        if self._type in ["straddle", "strangle"]:
            return self._call_greeks.delta() + self._put_greeks.delta()
        elif self._type == "strap":
            return self._call_greeks.delta() + self._put_greeks.delta() * 2
        elif self._type == "strip":
            return self._call_greeks.delta() * 2 + self._put_greeks.delta()
        
    def gamma(self) -> float :
        """Calculate product gamma."""
        if self._type in ["straddle", "strangle"]:
            return self._call_greeks.gamma() + self._put_greeks.gamma()
        elif self._type == "strap":
            return self._call_greeks.gamma() + self._put_greeks.gamma() * 2
        elif self._type == "strip":
            return self._call_greeks.gamma() * 2 + self._put_greeks.gamma()
    
    def vega(self) -> float :
        """Calculate product vega."""
        if self._type in ["straddle", "strangle"]:
            return self._call_greeks.vega() + self._put_greeks.vega()
        elif self._type == "strap":
            return self._call_greeks.vega() + self._put_greeks.vega() * 2
        elif self._type == "strip":
            return self._call_greeks.vega() * 2 + self._put_greeks.vega()
     
    def theta(self) -> float :
        """Calculate product theta."""
        if self._type in ["straddle", "strangle"]:
            return self._call_greeks.theta() + self._put_greeks.theta()
        elif self._type == "strap":
            return self._call_greeks.theta() + self._put_greeks.theta() * 2
        elif self._type == "strip":
            return self._call_greeks.theta() * 2 + self._put_greeks.theta()
        
    def rho(self) -> float :
        """Calculate product rho."""
        if self._type in ["straddle", "strangle"]:
            return self._call_greeks.rho() + self._put_greeks.rho()
        elif self._type == "strap":
            return self._call_greeks.rho() + self._put_greeks.rho() * 2
        elif self._type == "strip":
            return self._call_greeks.rho() * 2 + self._put_greeks.rho()
   

class SpreadRisk:
    """
    A class representing risk analysis for spread options.
    
    Attributes:
        _type (str): The type of spread (call or put).
        _long_leg (VanillaOption): The long leg of the spread.
        _short_leg (VanillaOption): The short leg of the spread.
    """    

    def __init__(self, spread:Spread, process:BrownianMotion) -> None:
        """
        Initialize SpreadRisk object.

        Args:
            option (Spread): The spread option to analyze.
            process (BrownianMotion): The Brownian motion process.
        """
        
        # Spread caracteristics
        self._long_leg = spread._long_leg
        self._short_leg = spread._short_leg
        self._type = spread._type

        # Check product type
        if self._type not in ["call spread", "put spread"]:
            raise Exception("Input error : Please enter a call spread or a put spread.")

        # Greeks
        self._long_leg_greeks = OptionRisk(self._long_leg, process)
        self._short_leg_greeks = OptionRisk(self._short_leg, process)

    def greeks(self) -> str : 
        """Return all spread greeks."""
        return f"Delta = {round(self.delta(), 2)}, gamma = {round(self.gamma(), 2)}, vega = {round(self.vega(), 2)}, theta = {round(self.theta(), 2)}, rho = {round(self.rho(), 2)}"
    
    def delta(self) -> float :
        """Calculate spread delta."""
        return self._long_leg_greeks.delta() - self._short_leg_greeks.delta()
    
    def gamma(self) -> float :
        """Calculate spread gamma."""
        return self._long_leg_greeks.gamma() - self._short_leg_greeks.gamma()
    
    def vega(self) -> float :
        """Calculate spread vega."""
        return self._long_leg_greeks.vega() - self._short_leg_greeks.vega()
    
    def theta(self) -> float :
        """Calculate spread theta."""
        return self._long_leg_greeks.theta() - self._short_leg_greeks.theta()
    
    def rho(self) -> float :
        """Calculate spread rho."""
        return self._long_leg_greeks.rho() - self._short_leg_greeks.rho()


class ButterflySpreadRisk:
    """
    A class representing risk analysis for a butterfly spread option.
    
    Attributes:
        _call_spread (Spread): The call spread of the butterfly.
        _put_spread (Spread): The put spread of the butterfly.
    """    

    def __init__(self, butterfly:ButterflySpread, process:BrownianMotion) -> None:
        """
        Initialize SpreadRisk object.

        Args:
            butterfly (ButterflySpread): The butterfly spread option to analyze.
            process (BrownianMotion): The Brownian motion process.
        """

        # Greeks
        self._put_spread_greeks = SpreadRisk(butterfly._put_spread, process)
        self._call_spread_greeks = SpreadRisk(butterfly._call_spread, process)
    
    def greeks(self) -> str : 
        """Return all butterfly spread greeks."""
        return f"Delta = {round(self.delta(), 2)}, gamma = {round(self.gamma(), 2)}, vega = {round(self.vega(), 2)}, theta = {round(self.theta(), 2)}, rho = {round(self.rho(), 2)}"
    
    def delta(self) -> float :
        """Calculate butterfly spread delta."""
        return self._put_spread_greeks.delta() + self._call_spread_greeks.delta()
    
    def gamma(self) -> float :
        """Calculate butterfly spread gamma."""
        return self._put_spread_greeks.gamma() + self._call_spread_greeks.gamma()
    
    def vega(self) -> float :
        """Calculate butterfly spread vega."""
        return self._put_spread_greeks.vega() + self._call_spread_greeks.vega()
    
    def theta(self) -> float :
        """Calculate butterfly spread theta."""
        return self._put_spread_greeks.theta() + self._call_spread_greeks.theta()
    
    def rho(self) -> float :
        """Calculate butterfly spread rho."""
        return self._put_spread_greeks.rho() + self._call_spread_greeks.rho()


class StructuredProductsRisk:
    """
    A class representing risk analysis for structured products.
    
    Attributes:
        _conv (ReverseConvertible): a reverse convertible structured product.
        _certif (CertificatOutperformance): a certificat outperformance structured product.
        _type (str): type of product to compute the greeks for.
    """

    def __init__(self, type: str, process: BrownianMotion, 
                 convertible: ReverseConvertible = None, certificat: CertificatOutperformance = None) -> None:
        """
        Initialize StructuredProductsRisk object.

        Args:
            type (str): the type of structured product.
            process (BrownianMotion): The Brownian motion process.
            convertible (ReverseConvertible, optionnal): a structured product. Defaults to None.
            certificat (CertificatOutperformance, optionnal): a structured product. Defaults to None.
        """
        
        self._conv = convertible
        self._certif = certificat

        self._type = type.lower()
        if self._type == "reverse convertible":
            self._conv_greeks = OptionRisk(self._conv._short_put, process)
        elif self._type == "certificat outperformance":
            self._call_greeks = OptionRisk(self._certif._call, process)
        else:
            raise Exception("Input error: Please enter a certificat outperformance or a reverse convertible.")

    def greeks(self) -> str : 
        """Return all butterfly spread greeks."""
        return f"Delta = {round(self.delta(), 2)}, gamma = {round(self.gamma(), 2)}, vega = {round(self.vega(), 2)}, theta = {round(self.theta(), 2)}, rho = {round(self.rho(), 2)}"
    
    def delta(self) -> float :    
        """Calculate a structured product delta."""
        if self._type == "reverse convertible":
            return self._conv_greeks.delta()
        else:
            return (1 - self._certif.participation_level()) * self._call_greeks.delta()        

    def gamma(self) -> float :
        """Calculate a structured product gamma."""
        if self._type == "reverse convertible":
            return self._conv_greeks.gamma()
        else:
            return (1 - self._certif.participation_level()) * self._call_greeks.gamma()        
        

    def vega(self) -> float :
        """Calculate a structured product vega."""
        if self._type == "reverse convertible":
            return self._conv_greeks.vega()
        else:
            return (1 - self._certif.participation_level()) * self._call_greeks.vega()        
        

    def theta(self) -> float :
        """Calculate a structured product theta."""
        if self._type == "reverse convertible":
            return self._conv_greeks.theta()
        else:
            return (1 - self._certif.participation_level()) * self._call_greeks.theta()        
        

    def rho(self) -> float :
        """Calculate a structured product rho."""
        if self._type == "reverse convertible":
            return self._conv_greeks.rho()
        else:
            return (1 - self._certif.participation_level()) * self._call_greeks.rho()        
    
        
    
    
