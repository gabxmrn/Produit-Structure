from done.Bond import FixedBond
from done.FloatingBond import FloatingBond
from done.maturity import Maturity
from done.rate import Rate
 
 
class IRSwap:
 
    def __init__( 
        self,
        contract_maturity:Maturity,
        rates:Rate,
        nominal:float,
        libor_rate:float,
        fixed_coupon:float,
        fixed_nb_coupon:float,
        float_nb_coupon:float,
        libor_maturity:Maturity,
        fixed_pay:bool=True
        ):
        self.__contract_maturity=contract_maturity
        self.__rates=rates
        self.__nominal=nominal
        self.__libor_rate=libor_rate
        self.__fixed_nb_coupon=fixed_nb_coupon
        self.__float_nb_coupon=float_nb_coupon
        self.__libor_maturity=libor_maturity
        self.__fixed_pay=fixed_pay
        self.__fixed_coupon=fixed_coupon
        self.__components=self._components()
        self.__price=None
 
    def _components(self):
        return [
            {
                "quantity":-1 if self.__fixed_pay else 1,
                "product":FixedBond(
                    self.__fixed_coupon,
                    self.__contract_maturity,
                    self.__nominal,
                    self.__fixed_nb_coupon,
                    self.__rates
                )
            },
            {
                "quantity":1 if self.__fixed_pay else -1,
                "product":FloatingBond(
                    self.__libor_rate,
                    self.__libor_maturity,
                    self.__nominal,
                    self.__float_nb_coupon,
                    self.__rates
                )
            },
        ]
 
    def price(self):
        if self.__price==None:
            self.__price=sum([
                p["quantity"]*p["product"].price()
                for p in self.__components
            ])
        return self.__price