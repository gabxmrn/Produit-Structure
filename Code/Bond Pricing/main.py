from datetime import datetime

from maturity import Maturity 
from rate import Rate
from zcBond import ZcBond
from bond import FixedBond


#### Test Maturity : 
# maturity = Maturity(maturity_in_years=4.5, day_count_convention="ACT/365")
maturity = Maturity(begin_date=datetime(2023, 1, 1), end_date=datetime(2023, 9, 6))
print(f"Maturité (en année) = {maturity.maturity()}")


#### Test Rate : 
# rate = Rate(rate=0.2, rate_type="continuous")
curve = {Maturity(0.5):0.1, Maturity(1):0.2, Maturity(2):0.3, Maturity(3):0.4}
rate = Rate(rate_type="compounded", rate_curve=curve, interpol_type="krogh")
print(f"Taux = {rate.rate(maturity)}")

#### Test zcBond : 
zc_bond = ZcBond(rate, maturity, 100)
print(f"Prix zero coupon = {zc_bond.price()}")

#### Test Bond : 
fixed_bond = FixedBond(0.1, maturity, 100, 12, rate)
print(f"Prix de l'obligation à taux fixe = {fixed_bond.price()}")
print(f"YTM de l'obligation à taux fixe = {fixed_bond.ytm()}")


    
    
"""
    Résumé : 
        - Maturity : OK
        - Rate : OK
        - ZcBond : OK
        - FixedBond (Bond) : OK
        - Optim : OK
    PS : les obligations à taux flottant sont pas à faire ? 
    Il y a marqué que du taux fixe dans l'énoncé du projet 
"""