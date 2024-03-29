
import numpy as np
import pandas as pd

from maturity import Maturity
from rate import Rate
from products import AbstractProduct

# PS : c'est le fichier GbmProcess du cours :) 

class BrownianMotion:
    """
    A class representing a Geometric Brownian Motion (GBM) process for financial simulations.

    Attributes:
        _inputs (dict): A dictionary containing input parameters required for the process.
        _z (pd.DataFrame): DataFrame containing the random component of the process.
        _prices (np.array): Array containing simulated prices of the underlying asset.

    """
    
    def __init__(self, inputs):
        """
        Initialize a BrownianMotion object.

        Args:
            inputs (dict): A dictionary containing input parameters required for the process.
        """
        
        self._inputs = inputs
        self._z = None
        self._prices = None
    
    def _input(self, code):
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
    
    def _generate_z(self):
        """
        Generate random component of the process.

        """
        
        if self._z is None:
            nb_simulations = self._input("nb_simulations")
            nb_steps = self._input("nb_steps")
            maturity : Maturity = self._input("maturity")
            dt = maturity.maturity() / nb_steps
            np.random.seed(272)
            z = np.random.normal(0.0,1.0,[nb_simulations, nb_steps]) * dt ** 0.5
            col = np.arange(1, nb_steps+1)*dt
            z = pd.DataFrame(z, columns=col)
            z.insert(0, 0, 0)
            self._z = z
    
    def __generate_price(self):
        """
        Generate simulated prices of the underlying asset.
        
        """
        self._generate_z()
        if self._prices is None:
            spot = self._input("spot")
            maturity = self._input("maturity")         
            rates = self._input("rates")
            discount_factor = rates.discount_factor(maturity)
            rate = -np.log(discount_factor) / maturity.maturity()
            volatility = self._input("volatility")
            nb_steps = self._input("nb_steps")
            dt = maturity.maturity()/nb_steps
            z = self._z
            drift_dt = (rate - 0.5 * volatility ** 2) * dt # Constante
            
            motion = z * volatility
            rdt = drift_dt + motion
            
            rdt[0] = 0 # Exception here
            
            log_spot = np.log(spot)
            log_st = log_spot + np.cumsum(rdt, axis=1)
            st = np.exp(log_st)
            
            self._prices = st
        
    def pricing(self, product:AbstractProduct):
        """
        Calculate the price of a financial product based on the simulated prices.

        Args:
            product (AbstractProduct): Financial product to price.

        Returns:
            dict: Dictionary containing the calculated price and probability.
        """
        
        self.__generate_price()
        st = self._prices
        last_values = st[st.columns[-1]]
        ct = product.payoff(last_values)
        rates = self._input("rates")
        maturity = self._input("maturity")
        c0 = rates.discount_factor(maturity) \
             * np.sum(ct)/len(ct)
        
        self._z = None
        
        return {"price":c0, "proba":(ct > 0).sum()/len(ct)}
            
