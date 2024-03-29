
import numpy as np
import pandas as pd

from maturity import Maturity
from rate import Rate
from products import AbstractProduct

# GBM Process ???? 


class GbmProcess:
    
    def __init__(self, inputs):
        self._inputs=inputs
        self._z=None
        self._prices=None
    
    def _input(self, code):
        if code in self._inputs:
            return self._inputs[code]
        raise Exception("Missing inputs : " + code)
    
    def _generate_z(self):
        if self._z==None:
            nb_simulations=self._input("nb_simulations")
            nb_steps=self._input("nb_steps")
            maturity:Maturity=self._input("maturity")
            dt=maturity.maturity()/nb_steps
            np.random.seed(272)
            z = np.random.normal(0.0,1.0,[nb_simulations, nb_steps])*dt**0.5
            col=np.arange(1, nb_steps+1)*dt
            z=pd.DataFrame(
                z, 
                columns=col
            )
            z.insert(0, 0, 0)
            self._z=z
    
    def __generate_price(self):
        self._generate_z()
        if self._prices==None:
            spot = self._input("spot")
            print(f"spot = {spot}")
            maturity = self._input("maturity")
            print(f"maturity = {maturity.maturity()}")
            
            rates = self._input("rates")
            print(f"rate = {rates.rate()}")
            discount_factor = rates.discount_factor(maturity)
            # print(discount_factor)
            
            rate = -np.log(discount_factor)/maturity.maturity()
            volatility=self._input("volatility")
            nb_steps=self._input("nb_steps")
            dt=maturity.maturity()/nb_steps
            z=self._z
            
            
            drift_dt=(rate-0.5*volatility**2)*dt # Constante
            
            motion=z*volatility
            rdt=drift_dt+motion
            
            rdt[0]=0 # Exception here
            
            log_spot=np.log(spot)
            log_st=log_spot+np.cumsum(rdt, axis=1)
            st=np.exp(log_st)
            
            self._prices=st
        
    def pricing(self, product:AbstractProduct):
        self.__generate_price()
        st=self._prices
        last_values=st[st.columns[-1]]
        ct=product.payoff(last_values)
        rates=self._input("rates")
        maturity=self._input("maturity")
        c0=rates.discount_factor(maturity) \
             * np.sum(ct)/len(ct)
        
        return {
            "price":c0,
            "prob":(ct > 0).sum()/len(ct)
        }
            
