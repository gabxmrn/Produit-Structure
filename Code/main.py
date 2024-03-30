from datetime import datetime

from maturity import Maturity 
from rate import Rate
from zcBond import ZcBond
from bond import FixedBond
from brownianMotion import BrownianMotion
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

print("           ")

#### Test zcBond : 
zc_bond = ZcBond(rate=rate, maturity=maturity, nominal=100)
print(f"Prix zero coupon = {zc_bond.price()}")
# PS : on a le même résultat que le prof avec r = 0.03 :)

#### Test Bond : 
fixed_bond = FixedBond(coupon_rate=0.1, maturity=maturity, nominal=100, nb_coupon=22, rate=rate)
print(f"Prix de l'obligation à taux fixe = {fixed_bond.price()}")
print(f"YTM de l'obligation à taux fixe = {fixed_bond.ytm()}")
print(f"Duration de l'obligation à taux fixe = {fixed_bond.duration()}")
print(f"Convexité de l'obligation à taux fixe = {fixed_bond.convexite()}")

print("           ")

#### Test Call/Put : 
process = BrownianMotion({
    "nb_simulations":1000,
    "nb_steps":1,
    "spot":100,
    "rates":Rate(0.03, rate_type="continuous"),
    "volatility":0.2,
    "maturity":Maturity(0.5)
})
call_product = Call({"strike":102})
put_product = Put({"strike":102})
call = process.pricing(call_product) 
put = process.pricing(put_product)
print(f"Call : Prix = {call['price']}, proba d'exercice = {call['proba']}, Payoff = {call_product.payoff(call['price'])}")
print(f"Put : Prix = {put['price']}, proba d'exercice = {put['proba']}, Payoff = {put_product.payoff(put['price'])}")
    
    
"""
    Résumé : 
        - maturity : OK
        - rate : OK
        
            ### Obligations : ###
        - zcBond : OK
        - bond : OK
        - optim : OK
        
            ### Options : ###
        - brownianMotion : OK
        - products : fonctionne mais pas complet 
        
    PS : 
    - Les obligations à taux flottant sont pas à faire (il y a marqué que du taux fixe dans l'énoncé du projet) 
    
    
    Caro : 
    - j'ai tenter de rajouter la duration dans la classe bond mais vraiment pas sure de la formule (et des résultats) ??
    - pareil pour la convexite de l'obligation
    - on a une erreur quand maturité trop longue (problème de discount factor)
    
    
"""