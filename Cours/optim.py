import scipy.optimize as opt
 
class Optim:
 
    def __init__( 
        self,
        fct_pricing,
        target_value:float,
        epsilon:float=0.001,
        init_value:float=0.01
    ):
        self.__fct_pricing=fct_pricing
        self.__target_value=target_value
        self.__epsilon=epsilon
        self.__init_value=init_value
    
    def run(self):
        fct_obj=lambda x:(self.__target_value-self.__fct_pricing(x))**2
        x0=(self.__init_value)
        opt_res=opt.minimize(fct_obj, x0, method="SLSQP", tol=self.__epsilon)
        return opt_res
    
 
# Test Optim
# fct=lambda x : x**2
# obj=Optim(fct, 25.0, 0.0101)
# print(obj.run())