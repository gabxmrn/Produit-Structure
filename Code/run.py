import datetime

from bond import FixedBond, ZcBond
from brownianMotion import BrownianMotion
from products import VanillaOption, Spread, BinaryOption, KnockOutOption, KnockInOption
from riskAnalysis import BondRisk, OptionRisk, SpreadRisk

### Option type : 
SHARE_NO_DIV, SHARE_DIV  = "no dividend share", "dividend share"
FOREX = "forex rate"
CAPITALIZED_INDEX, NON_CAPITALIZED_INDEX = "capitalized index", "non capitalized index"
BINARY_PUT, BINARY_CALL = "binary_call", "binary_put"
ONE_TOUCH, NO_TOUCH, DOUBLE_ONE_TOUCH, DOUBLE_NO_TOUCH = "one_touch", "no_touch", "double_one_touch", "double_no_touch"
KNOCKOUT, KNOCKIN = "knock_out", "knock_in"


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
        
        process = BrownianMotion(inputs=inputs)
       
        if underlying == FOREX :
            # For options on exchange rates:
            domestic_rate = self._input("domestic_rate", inputs)
            maturity = self._input("maturity", inputs)
            option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":strike, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)}) 
            
        else :
            # For every others option type :
            option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":strike})
            
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
        
    def spread(self, inputs:dict) -> dict :
        option_type = self._input("option_type", inputs)
        short_strike = self._input("short_strike", inputs)
        long_strike = self._input("long_strike", inputs)
        underlying = self._input("underlying", inputs)
        
        if underlying == FOREX :
            # For options on exchange rates:
            domestic_rate = self._input("domestic_rate", inputs)
            maturity = self._input("maturity", inputs)
            short_option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":short_strike, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)}) 
            long_option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":long_strike, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)}) 
            
        else :
            # For every others option type :
            short_option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":short_strike}) 
            long_option = VanillaOption(underlying=underlying, inputs={"option_type":option_type, "strike":long_strike}) 
        
        process = BrownianMotion(inputs=inputs)
        short_process = process.pricing(short_option)
        long_process = process.pricing(long_option)
        
        spread_type = option_type + " spread"
        spread = Spread(spread_type, {"long leg": long_option, "long leg price":long_process['price'], "short leg": short_option, "short leg price": short_process['price']})
        risks = SpreadRisk(spread, process)
        
        return {"price":round(spread.price(), 2), 
                "delta":round(risks.delta(), 2), 
                "gamma":round(risks.gamma(), 2), 
                "vega":round(risks.vega(), 2), 
                "theta":round(risks.theta(), 2), 
                "rho":round(risks.rho(), 2)}
        
    
    def binary_option(self, inputs:dict) -> dict :
        strike = self._input("strike", inputs)
        option_type = self._input("option_type", inputs).lower()
        payoff_amount = self._input("payoff_amount", inputs)
        
        process = BrownianMotion(inputs=inputs)
        
        if option_type == BINARY_CALL or option_type == BINARY_PUT:
            option = BinaryOption({"strike":strike, "option_type":option_type, "payoff_amount": payoff_amount})
                
        elif option_type == ONE_TOUCH or option_type == NO_TOUCH:
            barrier = self._input("barrier", inputs)
            option = BinaryOption({"strike":strike, "option_type":option_type, "payoff_amount": payoff_amount, "barrier":barrier})
            
        elif option_type == DOUBLE_ONE_TOUCH or option_type == DOUBLE_NO_TOUCH :
            upper_barrier = self._input("upper_barrier", inputs)
            lower_barrier = self._input("lower_barrier", inputs)
            option = BinaryOption({"strike":strike, "option_type":option_type, "payoff_amount": payoff_amount, "upper_barrier":upper_barrier, "lower_barrier":lower_barrier})
        
        option_process = process.pricing(option)
        
        return {"price":round(option_process['price'], 2), 
                "proba":round(option_process['proba'], 2)}
        
    def barrier_option(self, inputs) :
        strike = self._input("strike", inputs)
        barrier = self._input("barrier", inputs)
        option_type = self._input("option_type", inputs).lower()
        
        if option_type == KNOCKOUT :
            option = KnockOutOption({"barrier":barrier, "strike":strike})
        elif option_type == KNOCKIN :
            option = KnockInOption({"barrier":barrier, "strike":strike})
            
        process = BrownianMotion(inputs=inputs)
        option_process = process.pricing(option, monte_carlo=True)
        price_paths = process.paths_plot        
        return {"price":round(option_process['price'], 2), 
                "proba":round(option_process['proba'], 2), 
                "paths": price_paths}
        
        
class StressTest:
    
    def __init__(self, 
                 new_spot:float, 
                 new_begin_date:datetime=None, 
                 new_maturity_in_years:float=None) -> None:
        self._new_spot = new_spot
        self._new_begin_date = new_begin_date 
        self._new_maturity_in_years = new_maturity_in_years
    
    def _get_new_inputs(self, inputs) :
        new_inputs = inputs.copy()
        new_inputs["maturity"] = inputs["maturity"].get_new_maturity(self._new_begin_date, self._new_maturity_in_years)
        new_inputs["nominal"] = self._new_spot
        return new_inputs
        
    def zc_bond(self, inputs:dict) -> dict :
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().zc_bond(inputs=inputs)
        new = Run().zc_bond(inputs=new_inputs)
        return {"price":round(new["price"] - old["price"], 2)}
        
    def fixed_bond(self, inputs:dict) -> dict :
        new_inputs = self._get_new_inputs(inputs)

        old = Run().fixed_bond(inputs=inputs)
        new = Run().fixed_bond(inputs=new_inputs)
        
        return {"price":round(new["price"] - old["price"], 2), 
                "ytm":round(new["ytm"] - old["ytm"], 2), 
                "duration":round(new["duration"] - old["duration"], 2), 
                "convexity":round(new["convexity"] - old["convexity"], 2)}
        
    def vanilla_option(self, inputs:dict) -> dict :      
        new_inputs = self._get_new_inputs(inputs)
        
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
        
    def spread(self, inputs:dict) -> dict :      
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().vanilla_option(inputs=inputs)
        new = Run().vanilla_option(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2), 
                "delta":round(new["delta"] - old["delta"], 2), 
                "gamma":round(new["gamma"] - old["gamma"], 2), 
                "vega":round(new["vega"] - old["vega"], 2), 
                "theta":round(new["theta"] - old["theta"], 2), 
                "rho":round(new["rho"] - old["rho"], 2)}
        
    def binary_option(self, inputs:dict) -> dict :
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().binary_option(inputs=inputs)
        new = Run().binary_option(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2), 
                "proba":round(new["proba"] - old["proba"], 2)}
        
    def barrier_option(self, inputs:dict) -> dict :
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().barrier_option(inputs=inputs)
        new = Run().barrier_option(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2), 
                "proba":round(new["proba"] - old["proba"], 2)}
        