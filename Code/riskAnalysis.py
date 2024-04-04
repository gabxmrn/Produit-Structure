from bond import FixedBond
from products import VanillaOption
from brownianMotion import BrownianMotion

from math import exp, log, sqrt, pi
from scipy.stats import norm

class BondRisk:
    def __init__ (self, bond:FixedBond) :
        self.__m = bond.maturity.maturity() / bond.nb_coupon 
        self.__r_ytm = bond.ytm()
        self.__coupon_list = bond.run_coupon()
        self.__price = bond.price()
        
        
    def duration(self, force_rate:float=None):      
        numerator = 0
        for coupon_t in self.__coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            numerator += coupon * exp(-self.__r_ytm / self.__m * t) * t 
        return round(numerator / self.__price, 2)
    
    def convexite(self, force_rate:float=None):        
        numerator = 0
        for coupon_t in self.__coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            numerator += coupon * exp(-self.__r_ytm / self.__m * t) * t**2
        
        return round(numerator, 2)


class OptionRisk:
    
    def __init__ (self, option:VanillaOption, process:BrownianMotion) :
        self.__type = option.option_type
        self.__strike = option._strike()
        self.__spot = process.input("spot")
        self.__maturity = process.input("maturity").maturity()
        self.__rate = process.input("rates").rate(self.__maturity) 
        self.__volatility = process.input("volatility")
        rate, spot = process.check_optional_input(self.__rate, self.__spot)
        self.__df = process.input("rates").discount_factor(maturity=process.input("maturity"), force_rate=rate)
                
                
    def _get_d1(self, spot, strike, rate, volatility, maturity) : 
        return (log(spot/strike) + (rate + volatility**2 / 2) * maturity) / (volatility * sqrt(maturity)) 

    def _get_Nd1(self, spot, strike, rate, volatility, maturity) :
        d1 = self._get_d1(spot, strike, rate, volatility, maturity)
        return  norm.cdf(d1, loc=0, scale=1) 
    
    def _get_Nd2(self, spot, strike, rate, volatility, maturity) :
        d1 = self._get_d1(spot, strike, rate, volatility, maturity)
        d2 = d1 - volatility * sqrt(maturity)
        return norm.cdf(d2, loc=0, scale=1) 
    
    def _get_dNd1(self, spot, strike, rate, volatility, maturity) :
        d1 = self._get_d1(spot, strike, rate, volatility, maturity)
        return 1 / sqrt(2 * pi) * exp(-d1**2 / 2)
    
    def delta(self) :
        Nd1 = self._get_Nd1(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        if self.__type == "call" :
            return round(Nd1, 2) ##### DIVIDENDE = * exp(-dT)
        elif self.__type == "put" : 
            return round(Nd1 - 1, 2) ##### DIVIDENDE = * exp(-dT)
        
    def gamma(self) :
        dNd1 = self._get_dNd1(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        return round(dNd1 / (self.__spot * self.__volatility * sqrt(self.__maturity)), 2)
        
    def vega(self) :
        dNd1 = self._get_dNd1(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        return round(self.__spot * sqrt(self.__maturity) * dNd1, 2)
    
    def theta(self) : 
        dNd1 = self._get_dNd1(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        Nd2 = self._get_Nd2(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        if self.__type == "call" :
            return round(- (self.__spot * dNd1 * self.__volatility) / (2 * sqrt(self.__maturity)) - self.__rate * self.__strike * self.__df * Nd2, 2)
        elif self.__type == "put" : 
            return round(- (self.__spot * dNd1 * self.__volatility) / (2 * sqrt(self.__maturity)) + self.__rate * self.__strike * self.__df * (1 - Nd2), 2)
    
    def rho(self) :
        Nd2 = self._get_Nd2(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        if self.__type == "call" :
            return round(self.__strike * self.__maturity * self.__df * Nd2, 2)
        elif self.__type == "put" : 
            return round(- self.__strike * self.__maturity * self.__df * (1 - Nd2), 2)