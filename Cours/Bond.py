from maturity import Maturity
from optim import Optim
from ZcBond import ZcBond
from rate import Rate


class FixedBond:
    def __init__(
        self,
        coupon_rate:float,
        maturity:Maturity,
        nominal:float,
        nb_coupon:int,
        rate:Rate):

        self.__rate=rate
        self.__maturity=maturity
        self.__nominal=nominal
        self.__coupon_rate=coupon_rate
        self.__nb_coupon=nb_coupon
        self.__components=self.__run_components()
        self.__price=None
        self.__ytm=None

    def price(self, force_rate:float=None):
        if self.__price==None or force_rate!=None:
            price= sum([
                zc_bond["zc_bond"].price(force_rate=force_rate)
                for zc_bond in self.__components
            ])
            if force_rate!=None:
                return price
            else:
                self.__price=price
        return self.__price

    def ytm(self):
        if self.__ytm==None:
            fct_obj=lambda rate: self.price(force_rate=rate)
            obj=Optim(
                fct_pricing=fct_obj,
                target_value=self.__price,
                init_value=0.01
            )
            opt_res= obj.run()
            if not opt_res["success"]:
                raise Exception("Not found YTM")
            self.__ytm=opt_res["x"][0]
        return self.__ytm


    def __run_components(self):
        t=self.__maturity.maturity()
        terms=[]
        step=1.0/self.__nb_coupon
        while t>0:
            terms.append(t)
            t-=step
        sorted(terms)
        freq_coupon=float(self.__coupon_rate)/self.__nb_coupon*self.__nominal
        coupons= [
            {
                "maturity":t,
                "cf_type":"coupon",
                "zc_bond":ZcBond(
                    self.__rate,
                    Maturity(maturity_in_years=t),
                    freq_coupon + (
                        0.0
                        if t<self.__maturity.maturity()
                        else self.__nominal
                    )
                )
            }
            for t in terms
        ]
        return coupons