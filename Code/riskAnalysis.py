from bond import FixedBond
from products import VanillaOption
from brownianMotion import BrownianMotion

from math import exp, log, sqrt, pi
from scipy.stats import norm

class BondRisk:
    def __init__ (self, bond:FixedBond) :
        self.__c = bond.coupon
        self.__m = bond.maturity.maturity() / bond.nb_coupon 
        self.__r_ytm = bond.ytm()
        self.__FV = bond.nominal
        self.__N = bond.nb_coupon
        self.__coupon_list = bond.run_coupon()
        self.__price = bond.price()
        
        
    def duration(self, force_rate:float=None):
        # Vraiment pas sure de la formule
        
        denominator = 0
        for coupon_t in self.__coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            denominator += coupon / self.__m * exp(-self.__r_ytm / self.__m * t) * t * self.__FV * exp(- self.__r_ytm / self.__m * self.__N) * t
        
        return denominator / self.__price
    
    def convexite(self, force_rate:float=None):
        # Vraiment pas sure de la formule 
        
        denominator = 0
        for coupon_t in self.__coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            denominator += coupon / self.__m * exp(-self.__r_ytm / self.__m * t) * t**2 * self.__FV * exp(- self.__r_ytm / self.__m * self.__N) * t**2
        
        return denominator 


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
                

    def _get_Nd1(self, spot, strike, rate, volatility, maturity) :
        d1 = (log(spot/strike) + (rate + volatility**2 / 2) * maturity) * (1/maturity * sqrt(maturity)) 
        return  norm.pdf(d1, loc=0, scale=1) 
    
    def _get_Nd2(self, spot, strike, rate, volatility, maturity) :
        d1 = (log(spot/strike) + (rate + volatility**2 / 2) * maturity) * (1/maturity * sqrt(maturity)) 
        d2 = d1 - volatility * sqrt(maturity)
        return norm.pdf(d2, loc=0, scale=1) 
    
    def _get_dNd1(self, spot, strike, rate, volatility, maturity) :
        d1 = (log(spot/strike) + (rate + volatility**2 / 2) * maturity) * (1/maturity * sqrt(maturity)) 
        return 1 / sqrt(2 * pi) * exp(-d1**2 / 2)
    
    def delta(self) :
        Nd1 = self._get_Nd1(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        if self.__type == "call" :
            return Nd1 ##### DIVIDENDE = * exp(-dT)
        elif self.__type == "put" : 
            return Nd1 - 1 ##### DIVIDENDE = * exp(-dT)
        
    def gamma(self) :
        dNd1 = self._get_dNd1(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        return dNd1 / (self.__spot * self.__volatility * sqrt(self.__maturity))
        
    def vega(self) :
        dNd1 = self._get_dNd1(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        return self.__spot * sqrt(self.__maturity) * dNd1
    
    def theta(self) : 
        dNd1 = self._get_Nd1(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        Nd2 = self._get_Nd2(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        if self.__type == "call" :
            return - (self.__spot * dNd1 * self.__volatility) / (2 * sqrt(self.__maturity)) - self.__rate * self.__strike * self.__df * Nd2
        elif self.__type == "put" : 
            return - (self.__spot * dNd1 * self.__volatility) / (2 * sqrt(self.__maturity)) + self.__rate * self.__strike * self.__df * (1 - Nd2)
    
    def rho(self) :
        Nd2 = self._get_Nd2(self.__spot, self.__strike, self.__rate, self.__volatility, self.__maturity)
        if self.__type == "call" :
            return self.__strike * self.__maturity * self.__df * Nd2 
        elif self.__type == "put" : 
            return - self.__strike * self.__maturity * self.__df * (1 - Nd2)