from datetime import datetime

from maturity import Maturity 
from rate import Rate
from zcBond import ZcBond
from bond import FixedBond
from gbmProcess import GbmProcess
from products import AbstractProduct, Call, Put


#### Test Maturity : 
# maturity = Maturity(maturity_in_years=4.5, day_count_convention="ACT/365")
maturity = Maturity(begin_date=datetime(2024, 3, 7), end_date=datetime(2025, 3, 7), day_count_convention="ACT/360")
print(f"Maturité (en année) = {maturity.maturity()}")


#### Test Rate : 
# rate = Rate(rate=0.03, rate_type="continuous")
curve = {Maturity(1.0/365.0):0.0075,
        Maturity(1.0/12.0):0.01,
        Maturity(3.0/12.0):0.015,
        Maturity(6.0/12.0):0.0175,
        Maturity(1.0):0.02,
        Maturity(5.0):0.03}
rate = Rate(rate_type="compounded", rate_curve=curve, interpol_type="linear")
print(f"Taux = {rate.rate(maturity)}")

#### Test zcBond : 
zc_bond = ZcBond(rate=rate, maturity=maturity, nominal=100)
print(f"Prix zero coupon = {zc_bond.price()}")
# PS : on a le même résultat que le prof avec r = 0.03 :)

#### Test Bond : 
fixed_bond = FixedBond(coupon_rate=0.1, maturity=maturity, nominal=100, nb_coupon=22, rate=rate)
print(f"Prix de l'obligation à taux fixe = {fixed_bond.price()}")
print(f"YTM de l'obligation à taux fixe = {fixed_bond.ytm()}")


#### Test Call/Put : 
process = GbmProcess({
    "nb_simulations":1000,
    "nb_steps":1,
    "spot":100,
    "rates":Rate(0.03, rate_type="continuous"),
    "volatility":0.2,
    "maturity":Maturity(0.5)
})
call = Call({"strike":100})
put = Put({"strike":100})
print(process.pricing(call))
print(process.pricing(put))
    
    
"""
    Résumé : 
        - Maturity : OK
        - Rate : OK
        - ZcBond : OK
        - FixedBond (Bond) : OK
        - Optim : OK
        - Option : je comprends rien 
    PS : les obligations à taux flottant sont pas à faire ? 
    Il y a marqué que du taux fixe dans l'énoncé du projet 
"""