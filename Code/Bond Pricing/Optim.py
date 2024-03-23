import scipy.optimize as opt
 

class Optim:
    """
    A class for optimizing a function to achieve a target value using the SciPy optimization library.

    Attributes:
        __fct_pricing (callable): The pricing model function to be optimized.
        __target_value (float): The target value that the optimization aims to achieve.
        __epsilon (float): A small positive scalar representing the tolerance for convergence.
        __init_value (float): The initial guess for the optimizer.
    """
 
    def __init__( 
        self,
        fct_pricing,
        target_value: float,
        epsilon: float = 0.001,
        init_value: float = 0.01
        ) -> None:
        """
        Initialize an instance of the Optim class.

        Args:
            fct_pricing (callable): A function representing the pricing model to be optimized.
            target_value (float): The target value that the optimization aims to achieve.
            epsilon (float, optional): A small positive scalar representing the tolerance for convergence. Defaults to 0.001.
            init_value (float, optional): The initial guess for the optimizer. Defaults to 0.01.
        """

        self.__fct_pricing = fct_pricing
        self.__target_value = target_value
        self.__epsilon = epsilon
        self.__init_value = init_value
    

    def run(self):
        """
        Execute the optimization process.

        Returns:
            scipy.optimize.OptimizeResult: The optimization result.
        """
        
        fct_obj = lambda x:(self.__target_value - self.__fct_pricing(x)) ** 2
        x0 = (self.__init_value)
        opt_res = opt.minimize(fct_obj, x0, method = "SLSQP", tol = self.__epsilon)
        return opt_res
