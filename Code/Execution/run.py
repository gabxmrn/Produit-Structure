from Products.bond import FixedBond, ZcBond
from Market.brownianMotion import BrownianMotion
from Products.optionalProducts import VanillaOption, Spread, ButterflySpread, OptionProducts, BinaryOption, KnockOutOption, KnockInOption
from Products.structuredProducts import CertificatOutperformance, ReverseConvertible
from RisksAnalysis.risks import BondRisk, OptionRisk, SpreadRisk, ButterflySpreadRisk, OptionProductsRisk, StructuredProductsRisk

### Option type : 
SHARE_NO_DIV, SHARE_DIV  = "no dividend share", "dividend share"
FOREX = "forex rate"
CAPITALIZED_INDEX, NON_CAPITALIZED_INDEX = "capitalized index", "non capitalized index"
BINARY_PUT, BINARY_CALL = "binary_call", "binary_put"
ONE_TOUCH, NO_TOUCH, DOUBLE_ONE_TOUCH, DOUBLE_NO_TOUCH = "one_touch", "no_touch", "double_one_touch", "double_no_touch"
KNOCKOUT, KNOCKIN = "knock_out", "knock_in"
STRADDLE, STRANGLE, STRIP, STRAP = "straddle", "strangle", "strip", "strap"



class Run :
    
    def __init__(self) :
        pass 
        
    def _input(self, code, inputs):
        """
        Retrieve input data from the inputs dictionary.

        Args:
            code (str): Key to retrieve the input value.
            inputs (dict): Dictionary containing input data.

        Returns:
            Any: Value corresponding to the provided key.

        Raises:
            Exception: If the key is not found in the inputs dictionary.
        """
        if code in inputs:
            return inputs[code]
        raise Exception("Missing inputs : " + code)

    def zc_bond(self, inputs: dict) -> dict:
        """ Returns data for a zero-coupon bond. """
        rate = self._input("rate", inputs)
        maturity = self._input("maturity", inputs)
        nominal = self._input("nominal", inputs)

        zc_bond = ZcBond(rate=rate, maturity=maturity, nominal=nominal)
        return {"price": round(zc_bond.price(), 2)}

    def fixed_bond(self, inputs: dict) -> dict:
        """ Returns data for a a fixed-rate bond. """
        coupon_rate = self._input("coupon_rate", inputs)
        maturity = self._input("maturity", inputs)
        nominal = self._input("nominal", inputs)
        nb_coupon = self._input("nb_coupon", inputs)
        rate = self._input("rate", inputs)

        fixed_bond = FixedBond(coupon_rate=coupon_rate, maturity=maturity, nominal=nominal,
                               nb_coupon=nb_coupon, rate=rate)
        price, ytm = fixed_bond.price(), fixed_bond.ytm()
        risk = BondRisk(bond=fixed_bond)
        duration, convexity = risk.duration(), risk.convexity()
        return {"price": round(price, 2),
                "ytm": round(ytm, 2),
                "duration": round(duration, 2),
                "convexity": round(convexity, 2)}
                
        
    def vanilla_option(self, inputs:dict) -> dict : 
        """ Returns data for a vanilla option product."""
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
    
    def butterfly(self, inputs:dict) -> dict :
        """ Returns data for a butterfly product."""
        strike_1 = self._input("strike_1", inputs)
        strike_2 = self._input("strike_2", inputs)
        strike_3 = self._input("strike_3", inputs)
        underlying = self._input("underlying", inputs)
        
        if underlying == FOREX :
            # For options on exchange rates:
            domestic_rate = self._input("domestic_rate", inputs)
            maturity = self._input("maturity", inputs)
            short_call = VanillaOption(underlying=underlying, inputs={"option_type":"call", "strike":strike_2, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)}) 
            long_call = VanillaOption(underlying=underlying, inputs={"option_type":"call", "strike":strike_1, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)})
            short_put = VanillaOption(underlying=underlying, inputs={"option_type":"put", "strike":strike_2, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)}) 
            long_put = VanillaOption(underlying=underlying, inputs={"option_type":"put", "strike":strike_3, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)})             
        else :
            # For every others option type :
            short_call = VanillaOption(underlying=underlying, inputs={"option_type":"call", "strike":strike_2}) 
            long_call = VanillaOption(underlying=underlying, inputs={"option_type":"call", "strike":strike_1})
            short_put = VanillaOption(underlying=underlying, inputs={"option_type":"put", "strike":strike_2}) 
            long_put = VanillaOption(underlying=underlying, inputs={"option_type":"put", "strike":strike_3}) 
        
        process = BrownianMotion(inputs=inputs)
        short_call_process, long_call_process = process.pricing(short_call), process.pricing(long_call)
        short_put_process, long_put_process = process.pricing(short_put), process.pricing(long_put)
        call_spread = Spread("call spread", {"long leg": long_call, "long leg price":long_call_process['price'], "short leg": short_call, "short leg price": short_call_process['price']})
        put_spread = Spread("put spread", {"long leg": long_put, "long leg price":long_put_process['price'], "short leg": short_put, "short leg price": short_put_process['price']})
        butterfly = ButterflySpread({"put spread":put_spread, "call spread":call_spread})
        risks = ButterflySpreadRisk(butterfly, process)
        
        return {"price":round(butterfly.price(), 2), 
                "delta":round(risks.delta(), 2), 
                "gamma":round(risks.gamma(), 2), 
                "vega":round(risks.vega(), 2), 
                "theta":round(risks.theta(), 2), 
                "rho":round(risks.rho(), 2)}
        
    def option_strategy(self, inputs:dict) -> dict :
        """ Returns data for a option strategy product."""
        call_strike = self._input("call_strike", inputs)
        put_strike = self._input("put_strike", inputs)
        underlying = self._input("underlying", inputs)
        option_type = self._input("option_type", inputs).lower()
        option_position = self._input("option_position", inputs).lower()
        
        if underlying == FOREX :
            # For options on exchange rates:
            domestic_rate = self._input("domestic_rate", inputs)
            maturity = self._input("maturity", inputs)
            call = VanillaOption(underlying=underlying, inputs={"option_type":"call", "strike":call_strike, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)}) 
            put = VanillaOption(underlying=underlying, inputs={"option_type":"put", "strike":put_strike, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)}) 
            
        else :
            # For every others option type :
            call = VanillaOption(underlying=underlying, inputs={"option_type":"call", "strike":call_strike}) 
            put = VanillaOption(underlying=underlying, inputs={"option_type":"put", "strike":put_strike}) 
        
        process = BrownianMotion(inputs=inputs)
        call_process = process.pricing(call)
        put_process = process.pricing(put)
        
        strategy = OptionProducts(option_type, option_position, {"call":call,"call price": call_process['price'],"put":put,"put price":put_process['price']})
        risks = OptionProductsRisk(strategy, process)
        
        return {"price":round(strategy.price(), 2), 
                "delta":round(risks.delta(), 2), 
                "gamma":round(risks.gamma(), 2), 
                "vega":round(risks.vega(), 2), 
                "theta":round(risks.theta(), 2), 
                "rho":round(risks.rho(), 2)}
        
    
    def binary_option(self, inputs:dict) -> dict :
        """ Returns data for a binary option product."""
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
        
    def barrier_option(self, inputs) -> dict :
        """ Returns data for a barrier option product."""
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
        
    def reverse_convertible(self, inputs) -> dict :
        """ Returns data for a reverse convertible product."""
        underlying = self._input("underlying", inputs)
        strike = self._input("strike", inputs)
        coupon_rate = self._input("coupon_rate", inputs)
        maturity = self._input("maturity", inputs)
        nominal = self._input("nominal", inputs)
        nb_coupon = self._input("nb_coupon", inputs)
        rate = self._input("rates", inputs)
        
        if underlying == FOREX :
            # For options on exchange rates:
            domestic_rate = self._input("domestic_rate", inputs)
            maturity = self._input("maturity", inputs)            
            put = VanillaOption(underlying, {"option_type":"put", "strike":strike, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)})
        else :
            # For every others option type :
            put = VanillaOption(underlying=underlying, inputs={"option_type":"put", "strike":strike}) 
        
        bond = FixedBond(coupon_rate=coupon_rate, maturity=maturity, nominal=nominal, nb_coupon=nb_coupon, rate=rate)
        
        process = BrownianMotion(inputs=inputs)
        put_process = process.pricing(put)
        
        product = ReverseConvertible({"put":put, "put price": put_process["price"], 
                         "bond":bond, "bond price": bond.price()})
        risks = StructuredProductsRisk(type="reverse convertible", process=process, convertible=product)
        
        return {"price":round(product.price(), 2), 
                "delta":round(risks.delta(), 2), 
                "gamma":round(risks.gamma(), 2), 
                "vega":round(risks.vega(), 2), 
                "theta":round(risks.theta(), 2), 
                "rho":round(risks.rho(), 2)}
        
    
    def certificat_outperformance(self, inputs) -> dict :
        """ Returns data for a certificat out performance product."""
        underlying = self._input("underlying", inputs)
        strike = self._input("strike", inputs)
        
        if underlying == FOREX :
            # For options on exchange rates:
            domestic_rate = self._input("domestic_rate", inputs)
            maturity = self._input("maturity", inputs)            
            call = VanillaOption(underlying, {"option_type":"call", "strike":strike, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)})
            call = VanillaOption(underlying, {"option_type":"call", "strike":0, "domestic_rate":domestic_rate, "maturity":self._input("maturity", inputs)})
        else :
            # For every others option type :
            call = VanillaOption(underlying=underlying, inputs={"option_type":"call", "strike":strike})
            zero_call = VanillaOption(underlying=underlying, inputs={"option_type":"call", "strike":0})  
        
        process = BrownianMotion(inputs=inputs)
        call_process = process.pricing(call)
        zero_process = process.pricing(zero_call)
        
        product = CertificatOutperformance({"zero strike call": zero_call, "zero strike call price": zero_process["price"],
                               "call":call, "call price":call_process["price"]})
        
        risks = StructuredProductsRisk(type="certificat outperformance", process=process, certificat=product)
        
        return {"price":round(product.price(), 2), 
                "delta":round(risks.delta(), 2), 
                "gamma":round(risks.gamma(), 2), 
                "vega":round(risks.vega(), 2), 
                "theta":round(risks.theta(), 2), 
                "rho":round(risks.rho(), 2)}