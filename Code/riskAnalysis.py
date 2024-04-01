from bond import FixedBond
from products import VanillaOption
from brownianMotion import BrownianMotion

from math import exp, log
from scipy.stats import norm

class Risk:
    
    def __init__ (self, 
                  bond:FixedBond=None) :
        self.__bond = bond

    
    def delta(self, option:VanillaOption, process:BrownianMotion) :
        spot = process.input("spot")
        strike = option._strike()
        maturity = process.input("maturity").maturity()
        rate = process.input("rates").rate(maturity) 
        volatility = process.input("volatility")
        rate, spot = process.check_optional_input(rate, spot)        
        
        d1 = log(spot/strike) + (rate + volatility/2) * maturity
        if option.option_type == "call" :
            return norm(d1)
            ##### DIVIDENDE = * exp(-dT)
        elif option.option_type == "put" : 
            return norm(d1) - 1
        
    
    def duration(self, force_rate:float=None):
        # Vraiment pas sure de la formule
        
        if self.__bond is None:
            raise ValueError("Please initialize a valid bond.")
        
        c = self.__bond.coupon
        m = self.__bond.maturity.maturity() / self.__bond.nb_coupon 
        r_ytm = self.__bond.ytm()
        FV = self.__bond.nominal
        N = self.__bond.nb_coupon
        coupon_list = self.__bond.run_coupon()
        
        denominator = 0
        
        for coupon_t in coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            denominator += coupon / m * exp(-r_ytm / m * t) * t * FV * exp(- r_ytm / m * N) * t
        
        return denominator / self.__bond.price()
    
    def convexite(self, force_rate:float=None):
        # Vraiment pas sure de la formule 
        
        if self.__bond is None:
            raise ValueError("Please initialize a valid bond.")
        
        m = self.__bond.maturity.maturity() / self.__bond.nb_coupon 
        c = self.__bond.coupon
        r_ytm = self.__bond.ytm()
        FV = self.__bond.nominal
        N = self.__bond.nb_coupon
        coupon_list = self.__bond.run_coupon()
        
        denominator = 0
        
        for coupon_t in coupon_list :
            t = coupon_t["maturity"]
            coupon = coupon_t["zc_bond"].price(force_rate=force_rate)
            denominator += coupon / m * exp(-r_ytm / m * t) * t**2 * FV * exp(- r_ytm / m * N) * t**2
        
        return denominator 