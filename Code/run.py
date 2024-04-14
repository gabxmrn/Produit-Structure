import datetime

from bond import FixedBond, ZcBond
from riskAnalysis import BondRisk, OptionRisk
from brownianMotion import BrownianMotion
from products import VanillaOption

SHARE_NO_DIV = "no dividend share"
SHARE_DIV = "dividend share"
FOREX = "forex rate"
CAPITALIZED_INDEX = "capitalized index"
NON_CAPITALIZED_INDEX = "non capitalized index"

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
        
        if underlying == SHARE_DIV or underlying == CAPITALIZED_INDEX :
            # For options on stocks with dividend and for options on capitalized index:  
            option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":strike})
            if "dividend_date" in inputs :
                process = process = BrownianMotion({
                    "nb_simulations":self._input("nb_simulations", inputs),
                    "nb_steps":self._input("nb_steps", inputs),
                    "spot":self._input("spot", inputs),
                    "rates":self._input("rates", inputs),
                    "volatility":self._input("volatility", inputs),
                    "maturity":self._input("maturity", inputs), 
                    "dividend":self._input("dividend", inputs),
                    "dividend_date":self._input("dividend_date", inputs)})   
            else :
                process = process = BrownianMotion({
                    "nb_simulations":self._input("nb_simulations", inputs),
                    "nb_steps":self._input("nb_steps", inputs),
                    "spot":self._input("spot", inputs),
                    "rates":self._input("rates", inputs),
                    "volatility":self._input("volatility", inputs),
                    "maturity":self._input("maturity", inputs), 
                    "dividend":self._input("dividend", inputs)})   
        
        elif underlying == FOREX :
            # For options on exchange rates:
            domestic_rate = self._input("domestic_rate", inputs)
            maturity = self._input("maturity", inputs)
            option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":strike, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)})
            process = process = BrownianMotion({
                "nb_simulations":self._input("nb_simulations", inputs),
                "nb_steps":self._input("nb_steps", inputs),
                "spot":self._input("spot", inputs),
                "rates":self._input("rates", inputs),
                "volatility":self._input("volatility", inputs),
                "maturity":maturity, 
                "forward_rate":self._input("forward_rate", inputs)})   
            
        elif underlying == SHARE_NO_DIV or underlying == NON_CAPITALIZED_INDEX :
            # For option on stocks without dividend and for options on non capitalized index
            option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":strike})
            process = process = BrownianMotion({
                "nb_simulations":self._input("nb_simulations", inputs),
                "nb_steps":self._input("nb_steps", inputs),
                "spot":self._input("spot", inputs),
                "rates":self._input("rates", inputs),
                "volatility":self._input("volatility", inputs),
                "maturity":self._input("maturity", inputs)}) 
            
        else :
            raise Exception("Unknown underlying.")
            
        option_process = process.pricing(option)
        risks = OptionRisk(option, process)
        
        return {"price":round(option_process['price'], 2), 
                "proba":round(option_process['proba'], 2), 
                "payoff":round(option.payoff(option_process['price']), 2),
                "delta":round(risks.delta(), 2), 
                "gamma":round(risks.gamma(), 2), 
                "vega":round(risks.vega(), 2), 
                "theta":round(risks.theta(), 2), 
                "rho":round(risks.rho(), 2)}
        
        
class StressTest:
    
    def __init__(self, 
                 new_spot:float, 
                 new_begin_date:datetime=None, 
                 new_maturity_in_years:float=None) -> None:
        self._new_spot = new_spot
        self._new_begin_date = new_begin_date 
        self._new_maturity_in_years = new_maturity_in_years
        
    def zc_bond(self, inputs:dict) -> dict :
        new_inputs = inputs.copy()
        new_inputs["maturity"] = inputs["maturity"].get_new_maturity(self._new_begin_date, self._new_maturity_in_years)
        new_inputs["nominal"] = self._new_spot
        
        old = Run().zc_bond(inputs=inputs)
        new = Run().zc_bond(inputs=new_inputs)
        return {"price":round(new["price"] - old["price"], 2)}
        
    def fixed_bond(self, inputs:dict) -> dict :
        new_inputs = inputs.copy()
        new_inputs["maturity"] = inputs["maturity"].get_new_maturity(self._new_begin_date, self._new_maturity_in_years)
        new_inputs["nominal"] = self._new_spot

        old = Run().fixed_bond(inputs=inputs)
        new = Run().fixed_bond(inputs=new_inputs)
        
        return {"price":round(new["price"] - old["price"], 2), 
                "ytm":round(new["ytm"] - old["ytm"], 2), 
                "duration":round(new["duration"] - old["duration"], 2), 
                "convexity":round(new["convexity"] - old["convexity"], 2)}
        
    def vanilla_option(self, inputs:dict) -> dict :      
        new_inputs = inputs.copy()
        new_inputs["maturity"] = inputs["maturity"].get_new_maturity(self._new_begin_date, self._new_maturity_in_years)
        new_inputs["spot"] = self._new_spot
        
        old = Run().vanilla_option(inputs=inputs)
        new = Run().vanilla_option(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2), 
                "proba":round(new["proba"] - old["proba"], 2), 
                "payoff":round(new["payoff"] - old["payoff"], 2), 
                "delta":round(new["delta"] - old["delta"], 2), 
                "gamma":round(new["gamma"] - old["gamma"], 2), 
                "vega":round(new["vega"] - old["vega"], 2), 
                "theta":round(new["theta"] - old["theta"], 2), 
                "rho":round(new["rho"] - old["rho"], 2)}
        