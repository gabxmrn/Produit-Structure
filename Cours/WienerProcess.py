
from done.maturity import Maturity
import numpy as np
import pandas as pd


# ??????????????????????????????????????????????

class WienerProcess:
    
    def __init__(
        self, 
        drift:float, 
        volatility:float,
        maturity:Maturity,
        nb_simulations:int=1000,
        nb_steps:int=1,
        seed:float=272
    ) -> None:
        self.__drift=drift
        self.__volatility=volatility
        self.__maturity=maturity
        self.__nb_simulations=nb_simulations
        self.__nb_steps=nb_steps
        self.__seed=seed
        self.__z=None
        self.__dt=None
        
        # Generate numbers
        self.__generate()
    
    def __generate(self):
        if self.__z==None:
            if self.__seed!=None: 
                np.random.seed(self.__seed)
            self.__dt=self.__maturity.maturity()/self.__nb_steps
            self.__z = np.random.normal(0.0,1.0,[self.__nb_simulations, self.__nb_steps])*self.__dt**0.5
    
    def return_simulation(self, use_dataframe:bool=True):
        """Return simulations

        Returns:
            _type_: _description_
        """
        x=self.__z*self.__volatility+self.__drift*self.__dt
        if use_dataframe:
            col=np.arange(1, self.__nb_steps+1)*self.__dt
            return pd.DataFrame(
                x, 
                columns=col
            )
        return x

    def cumulative_simulation(self):
        rdt=self.return_simulation(use_dataframe=True)
        return rdt.cumsum(axis=1)
    
    def get_chart(self, simul_number:list):
        cumulative_returns=self.cumulative_simulation()
        df=cumulative_returns.loc[simul_number].T
        self.__chart(df, "processus_Wiener")
    
    def __chart(self, df:pd.DataFrame, file_name:str):
        plot=df.plot()
        fig = plot.get_figure()
        fig.savefig(file_name + ".png")
    
    def confidence_interval(self, level:float=.90, simulations:list=[]):
        from scipy.stats import norm
        cumylative_simulation=self.cumulative_simulation()
        maturities=cumylative_simulation.columns
        quantile=norm.ppf(1-(1-level)/2)
        ic = lambda coeff:self.__drift*maturities+quantile*self.__volatility \
                  *maturities**0.5*coeff
        up=ic(1)
        down=ic(-1)
        moy=ic(0)
        df=pd.DataFrame({
            "Up":up,
            "Moy":moy,
            "Down":down
        })
        
        for simulation in simulations:
            df[f'#{simulation}']=cumylative_simulation.loc[simulation, :]
        print(df)
        self.__chart(df, "IC")
        
        
        


        