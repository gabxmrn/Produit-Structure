import datetime

from Execution.run import Run

class StressScenario:
    
    def __init__(self, 
                 new_spot:float, 
                 new_begin_date:datetime=None, 
                 new_maturity_in_years:float=None) -> None:
        """
        Initialize a StressScenario object.

        Args:
            new_spot (float): The new spot value.
            new_begin_date (datetime, optional): The new begin date. Defaults to None.
            new_maturity_in_years (float, optional): The new maturity value in years. Defaults to None.
        """
        self._new_spot = new_spot
        self._new_begin_date = new_begin_date 
        self._new_maturity_in_years = new_maturity_in_years
    
    def _get_new_inputs(self, inputs) :
        """
        Generate new inputs based on provided inputs and stress scenario.

        Args:
            inputs (dict): The original inputs.

        Returns:
            dict: The new inputs with updated spot value and maturity.
        """
        new_inputs = inputs.copy()
        new_inputs["maturity"] = inputs["maturity"].get_new_maturity(self._new_begin_date, self._new_maturity_in_years)
        new_inputs["nominal"] = self._new_spot
        return new_inputs
        
    def zc_bond(self, inputs:dict) -> dict :
        """Calculate the difference in data of a zero-coupon bond under stress."""
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().zc_bond(inputs=inputs)
        new = Run().zc_bond(inputs=new_inputs)
        return {"price":round(new["price"] - old["price"], 2)}
        
    def fixed_bond(self, inputs:dict) -> dict :
        """Calculate the difference in data of a fixed bond under stress."""
        new_inputs = self._get_new_inputs(inputs)

        old = Run().fixed_bond(inputs=inputs)
        new = Run().fixed_bond(inputs=new_inputs)
        
        return {"price":round(new["price"] - old["price"], 2), 
                "ytm":round(new["ytm"] - old["ytm"], 2), 
                "duration":round(new["duration"] - old["duration"], 2), 
                "convexity":round(new["convexity"] - old["convexity"], 2)}
        
    def vanilla_option(self, inputs:dict) -> dict :   
        """Calculate the difference in data of a vanilla option under stress."""   
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
        """Calculate the difference in data of a spread under stress."""  
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().spread(inputs=inputs)
        new = Run().spread(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2), 
                "delta":round(new["delta"] - old["delta"], 2), 
                "gamma":round(new["gamma"] - old["gamma"], 2), 
                "vega":round(new["vega"] - old["vega"], 2), 
                "theta":round(new["theta"] - old["theta"], 2), 
                "rho":round(new["rho"] - old["rho"], 2)}
        
    def butterfly(self, inputs:dict) -> dict :    
        """Calculate the difference in data of a butterfly under stress."""  
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().butterfly(inputs=inputs)
        new = Run().butterfly(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2), 
                "delta":round(new["delta"] - old["delta"], 2), 
                "gamma":round(new["gamma"] - old["gamma"], 2), 
                "vega":round(new["vega"] - old["vega"], 2), 
                "theta":round(new["theta"] - old["theta"], 2), 
                "rho":round(new["rho"] - old["rho"], 2)}
        
    def option_strategy(self, inputs:dict) -> dict :     
        """Calculate the difference in data of a optional strategy under stress.""" 
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().option_strategy(inputs=inputs)
        new = Run().option_strategy(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2), 
                "delta":round(new["delta"] - old["delta"], 2), 
                "gamma":round(new["gamma"] - old["gamma"], 2), 
                "vega":round(new["vega"] - old["vega"], 2), 
                "theta":round(new["theta"] - old["theta"], 2), 
                "rho":round(new["rho"] - old["rho"], 2)}
        
    def binary_option(self, inputs:dict) -> dict :
        """Calculate the difference in data of a binary option under stress."""
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().binary_option(inputs=inputs)
        new = Run().binary_option(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2), 
                "proba":round(new["proba"] - old["proba"], 2)}
        
    def barrier_option(self, inputs:dict) -> dict :
        """Calculate the difference in data of a barrier option under stress."""
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().barrier_option(inputs=inputs)
        new = Run().barrier_option(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2), 
                "proba":round(new["proba"] - old["proba"], 2)}
        
    def reverse_convertible(self, inputs:dict) -> dict :
        """Calculate the difference in data of a reverse convertible under stress."""
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().reverse_convertible(inputs=inputs)
        new = Run().reverse_convertible(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2),  
                "delta":round(new["delta"] - old["delta"], 2), 
                "gamma":round(new["gamma"] - old["gamma"], 2), 
                "vega":round(new["vega"] - old["vega"], 2), 
                "theta":round(new["theta"] - old["theta"], 2), 
                "rho":round(new["rho"] - old["rho"], 2)}
    
    def certificat_outperformance(self, inputs:dict) -> dict :
        """Calculate the difference in data of a certificat outperformance under stress."""
        new_inputs = self._get_new_inputs(inputs)
        
        old = Run().certificat_outperformance(inputs=inputs)
        new = Run().certificat_outperformance(inputs=new_inputs)
    
        return {"price":round(new["price"] - old["price"], 2),  
                "delta":round(new["delta"] - old["delta"], 2), 
                "gamma":round(new["gamma"] - old["gamma"], 2), 
                "vega":round(new["vega"] - old["vega"], 2), 
                "theta":round(new["theta"] - old["theta"], 2), 
                "rho":round(new["rho"] - old["rho"], 2)}
        