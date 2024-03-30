from scipy import interpolate
import math

from maturity import Maturity


class Rate:
    """
    A class representing rate information for financial calculations.
    
    Attributes:
        __rate (float): The rate value.
        __rate_curve (dict): The rate curve.
        __interpol_type (str): The type of interpolation used.
        __rate_type (str): The type of rate (continuous or compounded).
        __interpol (callable): The interpolation function.
    """
    
    def __init__(
            self,
            rate: float = None,
            rate_type: str = "continuous",
            rate_curve: dict = None,
            interpol_type: str = None
            ) -> None:
        """
        Initialize a Rate object.

        Args:
            rate (float, optional): The rate value. Defaults to None.
            rate_type (str, optional): The type of rate (continuous or compounded). Defaults to continuous.
            rate_curve (dict, optional): The rate curve. Defaults to None.
            interpol_type (str, optional): The type of interpolation used. Defaults to None.

        Raises:
            Exception: If rate_type is not 'continuous' or 'compounded'.
            Exception: If interpol_type is not 'linear', 'cubic', 'barycentric', or 'krogh'.
        """
        
        self.__rate = rate
        self.__rate_curve = rate_curve
        
        if rate_type not in ["continuous", "compounded"]:
            raise Exception("Unknown rate type, should be continuous or compounded.")
        self.__rate_type = rate_type.lower()
        if interpol_type is not None : 
            self.__interpol_type = interpol_type.lower()
        
        if self.__rate_curve is not None:            
            if self.__interpol_type in ["linear", "cubic"]:
                if self.__interpol_type == "cubic" and len(rate_curve) < 4:
                    raise Exception("Not enought information in rate curve")
                self.__interpol = interpolate.interp1d(
                    x=[mat.maturity()for mat in rate_curve.keys()], 
                    y=list(rate_curve.values()),
                    fill_value="extrapolate",
                    kind=self.__interpol_type
                )
                
            elif self.__interpol_type == "barycentric":
                self.__interpol = interpolate.BarycentricInterpolator(
                    xi=[mat.maturity() for mat in rate_curve.keys()], 
                    yi=list(rate_curve.values())
                )
            
            elif self.__interpol_type == "krogh":
                self.__interpol = interpolate.KroghInterpolator(
                    xi=[mat.maturity() for mat in rate_curve.keys()], 
                    yi=list(rate_curve.values())
                )
                
            else:
                raise Exception("Unknown interpolation type, should be linear, cubic, barycentric, or krogh.")


    def rate(self, maturity: Maturity) -> float:
        """
        Determine the rate based on the provided maturity.

        Inputs:
            maturity (Maturity): The maturity of the financial instrument.

        Returns:
            float: The determined rate.
        """

        if self.__rate!=None:
            return self.__rate
        return float(self.__interpol(maturity.maturity()))
    

    def discount_factor(self, maturity: Maturity, force_rate: float = None) -> float:
        """
        Calculate the discount factor based on the given maturity and optional rate.

        Inputs:
            maturity (Maturity): The maturity of the financial instrument.
            force_rate (float, optional): An optional parameter to specify a specific rate for discount factor calculation. 
                If not provided, the rate will be determined based on an interpolation of the rate curve.

        Returns:
            float: The calculated discount factor.
        """

        if force_rate != None:
            rate = force_rate
        else:
            rate = self.rate(maturity)
            
        if self.__rate_type == "continuous":
            return math.exp(- rate * maturity.maturity())
        elif self.__rate_type == "compounded":
            return 1.0 / (1 + rate) ** maturity.maturity()
