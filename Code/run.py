import datetime

from bond import FixedBond, ZcBond
from riskAnalysis import BondRisk, OptionRisk
from brownianMotion import BrownianMotion
from products import VanillaOption

CAPITALIZED_INDEX = "capitalized index"
SHARE_DIV = "dividend share"

class Run :
    
    def __init__(self) :
        pass 
        
    def _input(self, code, inputs):
        if code in inputs:
            return inputs[code]
        raise Exception("Missing inputs : " + code)
    
    def zc_bond(self, inputs:dict) -> dict :
        rate = self._input("rate", inputs)
        maturity = self._input("maturity", inputs)
        nominal = self._input("nominal", inputs)
        
        zc_bond = ZcBond(rate=rate, maturity=maturity, nominal=nominal)
        return {"price":round(zc_bond.price(), 2)}
        
    def fixed_bond(self, inputs:dict) -> dict :
        coupon_rate = self._input("coupon_rate", inputs)
        maturity = self._input("maturity", inputs)
        nominal = self._input("nominal", inputs)
        nb_coupon = self._input("nb_coupon", inputs)
        rate = self._input("rate", inputs)
        
        fixed_bond = FixedBond(coupon_rate=coupon_rate, maturity=maturity, nominal=nominal, nb_coupon=nb_coupon, rate=rate)
        price, ytm = fixed_bond.price(), fixed_bond.ytm()
        risk = BondRisk(bond=fixed_bond)
        duration, convexity = risk.duration(), risk.convexity()
        return {"price":round(price, 2), 
                "ytm":round(ytm, 2), 
                "duration":round(duration, 2), 
                "convexity":round(convexity, 2)}
        
    def vanilla_option(self, inputs:dict) -> dict : 
        underlying = self._input("underlying", inputs)
        strike = self._input("strike", inputs)
        option_type = self._input("option_type", inputs)
        
        process = process = BrownianMotion({
            "nb_simulations":self._input("nb_simulations", inputs),
            "nb_steps":self._input("nb_steps", inputs),
            "spot":self._input("spot", inputs),
            "rates":self._input("rates", inputs),
            "volatility":self._input("volatility", inputs),
            "maturity":self._input("maturity", inputs)
        })
        option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":strike})
        option_process = process.pricing(option)
        risks = OptionRisk(option, process)
        
        return {"price":round(option_process['price'], 2), 
                "proba":round(option_process['proba'], 2), 
                "payoff":round(option.payoff(option_process['price']), 2),
                "greeks":risks.greeks()}
        
    
class StressTest:
    
    def __init__(self, 
                 new_spot:float, 
                 new_begin_date:datetime=None, 
                 new_maturity_in_years:float=None) -> None:
        self._new_spot = new_spot
        self._new_begin_date = new_begin_date 
        self._new_maturity_in_years = new_maturity_in_years
        
    def _input(self, code, inputs):
        if code in inputs:
            return inputs[code]
        raise Exception("Missing inputs : " + code)
        
    def zc_bond(self, inputs:dict) -> dict :
        rate = self._input("rate", inputs)
        maturity = self._input("maturity", inputs)
        
        print(f"old (in) = {maturity.maturity()}")
        
        nominal = self._input("nominal", inputs)
        new_maturity = maturity.get_new_maturity(self._new_begin_date, self._new_maturity_in_years)
        
        print(f"new = {new_maturity.maturity()}, old = {maturity.maturity()}")
        
        old = Run().zc_bond(inputs={"rate":rate, "maturity":maturity, "nominal":nominal})
        new = Run().zc_bond(inputs={"rate":rate, "maturity":new_maturity, "nominal":self._new_spot})
        return {"price":round(new["price"] - old["price"], 2)}
        
    def fixed_bond(self, inputs:dict) -> dict :
        coupon_rate = self._input("coupon_rate", inputs)
        maturity = self._input("maturity", inputs)
        nominal = self._input("nominal", inputs)
        nb_coupon = self._input("nb_coupon", inputs)
        rate = self._input("rate", inputs)
        
        new_maturity = maturity.get_new_maturity(self._new_begin_date, self._new_maturity_in_years)
        
        old = Run().fixed_bond(inputs={"coupon_rate":coupon_rate, "maturity":maturity, "nominal":nominal, "nb_coupon":nb_coupon, "rate":rate})
        new = Run().fixed_bond(inputs={"coupon_rate":coupon_rate, "maturity":new_maturity, "nominal":self._new_spot, "nb_coupon":nb_coupon, "rate":rate})
        
        return {"price":round(new["price"] - old["price"], 2), 
                "ytm":round(new["ytm"] - old["ytm"], 2), 
                "duration":round(new["duration"] - old["duration"], 2), 
                "convexity":round(new["convexity"] - old["convexity"], 2)}
        
    def vanilla_option(self, inputs:dict) -> dict :
        maturity = self._input("maturity", inputs)
        spot = self._input("spot", inputs)
        new_maturity = maturity.get_new_maturity(self._new_begin_date, self._new_maturity_in_years)
        
        old = Run().vanilla_option(inputs={"underlying":self._input("underlying", inputs), 
                                        "option_type":self._input("option_type", inputs),
                                        "strike":self._input("strike", inputs), 
                                        "nb_simulations":self._input("nb_simulations", inputs),
                                        "nb_steps":self._input("nb_steps", inputs),
                                        "spot":spot,
                                        "rates":self._input("rates", inputs),
                                        "volatility":self._input("volatility", inputs),
                                        "maturity":maturity})
        new = Run().vanilla_option(inputs={"underlying":self._input("underlying", inputs), 
                                        "option_type":self._input("option_type", inputs),
                                        "strike":self._input("strike", inputs), 
                                        "nb_simulations":self._input("nb_simulations", inputs),
                                        "nb_steps":self._input("nb_steps", inputs),
                                        "spot":self._new_spot,
                                        "rates":self._input("rates", inputs),
                                        "volatility":self._input("volatility", inputs),
                                        "maturity":new_maturity})
    
        return {"price":round(new["price"] - old["price"], 2), 
                "proba":round(new["proba"] - old["proba"], 2), 
                "payoff":round(new["payoff"] - old["payoff"], 2)}
        