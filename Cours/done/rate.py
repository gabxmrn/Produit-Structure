import math
from done.maturity import Maturity
from scipy import interpolate
 
class Rate:
    def __init__( 
        self, 
        rate:float=None,
        rate_type:str="continuous",
        rate_curve:dict=None,
        interpol_type:str="linear"
        ) -> None:
        self.__rate_curve=rate_curve
        self.__rate=rate
        self.__rate_type=rate_type
        self.__interpol_type=interpol_type
        if rate_curve!=None:
            if self.__interpol_type not in ["linear", "cubic"]:
                raise Exception("Bad interpolation type")
            self.__interpol=interpolate.interp1d(
                [
                    mat.maturity() 
                    for mat in rate_curve.keys()
                ], 
                list(rate_curve.values()),
                fill_value="extrapolate",
                kind=self.__interpol_type
            )
    
    def rate( 
        self,
        maturity:Maturity
        ):
        if self.__rate!=None:
            return self.__rate
        return float(self.__interpol(maturity.maturity()))
        
    def discount_factor( 
        self,
        maturity:Maturity,
        force_rate:float=None
    ):
        rate=self.rate(maturity)
        if force_rate!=None:
            rate=force_rate
        if self.__rate_type=="continous":
            return math.exp(-rate*maturity.maturity())
        elif self.__rate_type=="compounded":
            return 1.0/(1+rate)**maturity.maturity()