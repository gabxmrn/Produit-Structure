
import numpy as np
import pandas as pd

from maturity import Maturity
from rate import Rate
from products import AbstractProduct

class BrownianMotion:
    """
    A class representing a Geometric Brownian Motion (GBM) process for financial simulations.

    Attributes:
        _inputs (dict): A dictionary containing input parameters required for the process.
        _optional_inputs (dict): A dictionary containing input parameters optional for the process. Default to None.
        _z (pd.DataFrame): DataFrame containing the random component of the process.
        _prices (np.array): Array containing simulated prices of the underlying asset.

    """
    
    def __init__(self, inputs:dict, optional_inputs:dict=None):
        """
        Initialize a BrownianMotion object.

        Args:
            inputs (dict): A dictionary containing input parameters required for the process.
            optional_inputs (dict): A dictionary containing input parameters optional for the process. Default to None.
        """
    
        self._inputs = inputs
        self._optional_inputs = optional_inputs
        self._z = None
        self._prices = None
    
    def input(self, code):
        """
        Helper method to retrieve input parameters.

        Args:
            code (str): Key for the input parameter.

        Returns:
            Any: Value of the input parameter.

        Raises:
            Exception: If the input parameter is missing.
        """
        
        if code in self._inputs:
            return self._inputs[code]
        raise Exception("Missing inputs : " + code)
    
    def check_optional_input(self, rate, spot):
        """
        Adjust optional inputs for spot and rate.

        Args:
            rate (float): The interest rate.
            spot (float): The current spot price.

        Returns:
            tuple: Updated spot and rate.
        """
        if self._optional_inputs is None : 
            return spot, rate
                
        # For options on stocks:
        if "dividend" in self._optional_inputs : 
            if "dividend_date" in self._optional_inputs :
                spot -= self._optional_inputs["dividend"] * np.exp(-rate * self._optional_inputs["dividend_date"])
            else :
                spot *= np.exp(-self._optional_inputs["dividend"] * self.input("maturity").maturity())
                rate -= self._optional_inputs["dividend"]
                 
        # For options on exchange rates:
        if "forward_rate" in self._optional_inputs :
            spot *= np.exp(-self._optional_inputs["forward_rate"] * self.input("maturity").maturity())
            
        return spot, rate
    
    def _generate_z(self):
        """
        Generate random component of the process.

        """
        if self._z is None:
            nb_simulations = self.input("nb_simulations")
            nb_steps = self.input("nb_steps")
            maturity : Maturity = self.input("maturity")
            dt = maturity.maturity() / nb_steps
            np.random.seed(272)
            z = np.random.normal(0.0,1.0,[nb_simulations, nb_steps]) * dt ** 0.5
            col = np.arange(1, nb_steps+1)*dt
            z = pd.DataFrame(z, columns=col)
            z.insert(0, 0, 0)
            self._z = z
        else:
            z = self._z
        return z
    
    def __generate_price(self):
        """
        Generate simulated prices of the underlying asset.
        
        """
        self._generate_z()
        if self._prices is None:
            
            spot = self.input("spot")
            maturity = self.input("maturity")         
            rates = self.input("rates")
            volatility = self.input("volatility")
            nb_steps = self.input("nb_steps")
            discount_factor = rates.discount_factor(maturity)
            rate = -np.log(discount_factor) / maturity.maturity()
            
            spot, rate = self.check_optional_input(rate, spot)

            dt = maturity.maturity()/nb_steps
            z = self._z
            drift_dt = (rate - 0.5 * volatility ** 2) * dt # Constante
            
            rdt = np.cumsum(drift_dt + z * volatility, axis=1)
            rdt = np.insert(rdt, 0, 0, axis=1) # Insert initial value 
        
            log_spot = np.log(spot)
            log_st = log_spot + rdt
            st = np.exp(log_st)
            
            self._prices = st
        
    def pricing(self, product:AbstractProduct, monte_carlo=False):
        """
        Calculate the price of a financial product based on the simulated prices.

        Args:
            product (AbstractProduct): Financial product to price.

        Returns:
            dict: Dictionary containing the calculated price and probability.
        """
        if monte_carlo:
            paths = self._generate_paths()
            payoffs = product.payoff(paths)
            maturity = self.input("maturity")
            discount_factor = self.input("rates").discount_factor(maturity)
            price = np.mean(payoffs) * discount_factor
            proba = np.mean(payoffs > 0)
            return {"price": price, "proba": proba}
        else:
            self.__generate_price()
            st = self._prices
            last_values = st[:, -1]
            ct = product.payoff(last_values)
            rates = self.input("rates")
            maturity = self.input("maturity")
            c0 = rates.discount_factor(maturity) \
                * np.sum(ct)/len(ct)
            self._z = None
            return {"price":c0, "proba":(ct > 0).sum()/len(ct)}
                

    def _generate_paths(self):
        """
        Generates asset price paths using the Geometric Brownian Motion model.
        Parameters:
            None - All necessary parameters are assumed to be available in `self._inputs`.

        Returns:
            None - The generated price paths are stored directly in `self._prices`.
    
        Raises:
            KeyError: If an expected key is missing from `self._inputs`.
            ValueError: If any of the numerical inputs are non-positive or otherwise invalid.
    
        Notes:
            - The simulation assumes a constant risk-free rate over the time to maturity.
            - Volatility is also assumed to be constant over the simulation period.
            - The number of steps determines the granularity of the simulation; more steps
            result in finer granularity but require more computational resources.
    
        """
        nb_simulations = self.input("nb_simulations")
        nb_steps = self.input("nb_steps")
        maturity = self.input("maturity").maturity()
        dt = maturity / nb_steps
        volatility = self.input("volatility")
        initial_spot = self.input("spot")
        rate = self.input("rates").rate(maturity)   # Assuming a constant rate

        z = self._generate_z().to_numpy()
        
        price_paths = np.zeros((nb_simulations, nb_steps + 1))
        price_paths[:, 0] = initial_spot
        
        for t in range(1, nb_steps + 1):
            price_paths[:, t] = price_paths[:, t-1] * np.exp((rate - 0.5 * volatility**2) * dt + volatility * z[:, t-1])

        self._prices = price_paths
        return self._prices