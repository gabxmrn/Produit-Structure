from datetime import datetime
from maturity import Maturity 
from rate import Rate
from bond import FixedBond, ZcBond
from brownianMotion import BrownianMotion
from products import VanillaOption, KnockInOption, KnockOutOption, BinaryOption, Spread, OptionProducts, ButterflySpread, ReverseConvertible, CertificatOutperformance

from riskAnalysis import BondRisk, OptionRisk, OptionProductsRisk, SpreadRisk, ButterflySpreadRisk


########################################### TEST MATURITY & RATE : ###########################################

#### MATURITY

maturity = Maturity(begin_date=datetime(2024, 3, 7), end_date=datetime(2025, 3, 7), day_count_convention="ACT/360")
print(f"Maturité (en année) = {round(maturity.maturity(), 2)}")

#### RATE

curve = {Maturity(1.0/365.0):0.0075,
        Maturity(1.0/12.0):0.01,
        Maturity(3.0/12.0):0.015,
        Maturity(6.0/12.0):0.0175,
        Maturity(1.0):0.02,
        Maturity(5.0):0.03}
rate = Rate(rate_type="compounded", rate_curve=curve, interpol_type="linear")
print(f"Taux = {round(rate.rate(maturity), 2)}")

print("           ")

################################################ TEST BONDS : ################################################

#### ZERO COUPON BOND

zc_bond = ZcBond(rate=rate, maturity=maturity, nominal=100)
print(f"Prix zero coupon bond = {round(zc_bond.price(), 2)}")

#### FIXED BOND

fixed_bond = FixedBond(coupon_rate=0.1, maturity=maturity, nominal=100, nb_coupon=22, rate=rate)
print(f"Prix de l'obligation à taux fixe = {round(fixed_bond.price(), 2)}")
print(f"YTM de l'obligation à taux fixe = {round(fixed_bond.ytm(), 2)}")
bond_risk = BondRisk(bond=fixed_bond)
print(f"Duration de l'obligation à taux fixe = {round(bond_risk.duration(), 2)}")
print(f"Convexité de l'obligation à taux fixe = {round(bond_risk.convexity(), 2)}")

print("           ")

########################################### TEST VANILLA OPTIONS : ###########################################

#### CALL / PUT

process = BrownianMotion({
    "nb_simulations":1000,
    "nb_steps":1000,
    "spot":100,
    "rates":Rate(0.03, rate_type="compounded"),
    "volatility":0.2,
    "maturity":Maturity(0.5)
})

call_product = VanillaOption("no dividend share", {"option_type":"call", "strike":102})
call_process = process.pricing(call_product) 
call_greeks = OptionRisk(call_product, process)

put_product = VanillaOption("non capitalized index", {"option_type":"put", "strike":102})
put_process = process.pricing(put_product)
put_greeks = OptionRisk(put_product, process)

print(f"Call : Prix = {round(call_process['price'], 2)}, proba d'exercice = {round(call_process['proba'], 2)}, Payoff = {call_product.payoff(call_process['price'])}")
print(f"Greeks -> {call_greeks.greeks()}")
print(f"Put : Prix = {round(put_process['price'])}, proba d'exercice = {round(put_process['proba'])}, Payoff = {put_product.payoff(put_process['price'])}")
print(f"Greeks -> {put_greeks.greeks()}")

print("           ")

# TEST SHARE + FX OPTIONS

process_share = BrownianMotion({
    "nb_simulations":1000,
    "nb_steps":50,
    "spot":100,
    "rates":Rate(0.03, rate_type="continuous"),
    "volatility":0.2,
    "maturity":Maturity(0.5), 
    "dividend":0.02})
call_share = VanillaOption("dividend share", {"option_type":"call", "strike":102})
call_process_share = process_share.pricing(call_share) 
greeks_share = OptionRisk(call_share, process_share)
print(f"Share Call : Prix = {round(call_process_share['price'], 2)}, proba d'exercice = {round(call_process_share['proba'], 2)}, Payoff = {round(call_share.payoff(call_process_share['price']), 2)}")
print(f"Greeks -> {greeks_share.greeks()}")

process_fx = BrownianMotion({
    "nb_simulations":1000,
    "nb_steps":1000,
    "spot":100,
    "rates":Rate(0.03, rate_type="continuous"),
    "volatility":0.2,
    "maturity":Maturity(0.5), 
    "forward_rate":0.2})
put_fx = VanillaOption("forex rate", {"option_type":"put", "strike":102, "domestic_rate":0.1, "maturity":Maturity(0.5)})
put_process_fx = process_fx.pricing(put_fx) 
greeks_fx = OptionRisk(put_fx, process_fx)
print(f"Forex Put : Prix = {round(put_process_fx['price'], 2)}, proba d'exercice = {round(put_process_fx['proba'], 2)}, Payoff = {round(put_fx.payoff(put_process_fx['price']), 2)}")
print(f"Greeks -> {greeks_fx.greeks()}")

print("           ")

########################################### TEST OPTION STRATEGY : ###########################################

############################# CALL SPREAD

# Call vendu (short)
short_call = VanillaOption("no dividend share", {"option_type":"call", "strike":105})
short_process = process.pricing(short_call)
print(f"Call short (strike 105) : Prix = {round(short_process['price'], 2)}")

# Call acheté (long)
long_call = VanillaOption("no dividend share", {"option_type":"call", "strike":95})
long_process = process.pricing(long_call)
print(f"Call long (strike 95) : Prix = {round(long_process['price'], 2)}")

call_spread = Spread("call spread",
                     {"long leg": long_call, "long leg price":long_process['price'], "short leg": short_call, "short leg price": short_process['price']})
print(f"Prix du call spread : {round(call_spread.price(),2)}")
call_spread_greeks = SpreadRisk(call_spread, process)
print(f"Greeks -> {call_spread_greeks.greeks()}")

print("           ")

############################# PUT SPREAD

# Put vendu (short)
short_put = VanillaOption("no dividend share", {"option_type":"put", "strike":105})
short_process2 = process.pricing(short_put)
print(f"Put short (strike 95) : Prix = {round(short_process2['price'], 2)}")

# Put acheté (long)
long_put = VanillaOption("no dividend share", {"option_type":"put", "strike":110})
long_process2 = process.pricing(long_put)
print(f"Put long (strike 105) : Prix = {round(long_process2['price'], 2)}")

put_spread = Spread("put spread",
                     {"long leg": long_put, "long leg price":long_process2['price'], "short leg": short_put, "short leg price": short_process2['price']})
print(f"Prix du put spread : {round(put_spread.price(),2)}")
put_spread_greeks = SpreadRisk(put_spread, process)
print(f"Greeks -> {put_spread_greeks.greeks()}")

print("           ")

############################# BUTTERFLY SPREAD

butterfly_spread = ButterflySpread({"put spread":put_spread, "call spread":call_spread})
print(f"Prix du butterfly spread : {round(butterfly_spread.price(),2)}")
butterfly_greeks = ButterflySpreadRisk(butterfly_spread, process)
print(f"Greeks -> {butterfly_greeks.greeks()}")

print("           ")

############################# STRADDLE

# Put
put_straddle = VanillaOption("no dividend share", {"option_type":"put", "strike":102})
put_straddle_process = process.pricing(put_straddle)
print(f"Put (strike 102) : Prix = {round(put_straddle_process['price'], 2)}")

# Call
call_straddle = VanillaOption("no dividend share", {"option_type":"call", "strike":102})
call_straddle_process = process.pricing(call_straddle)
print(f"Call (strike 102) : Prix = {round(call_straddle_process['price'], 2)}")

# Straddle
straddle = OptionProducts("straddle","long",{"call":call_straddle,"call price": call_straddle_process['price'],"put":put_straddle,"put price":put_straddle_process['price']})
print(f"Prix du straddle (long) : {round(straddle.price(),2)}")
straddle_greeks = OptionProductsRisk(straddle, process)
print(f"Greeks -> {straddle_greeks.greeks()}")

print("           ")

############################# STRANGLE

# Put
put_strangle = VanillaOption("no dividend share", {"option_type":"put", "strike":98})
put_strangle_process = process.pricing(put_strangle)
print(f"Put (strike 102) : Prix = {round(put_strangle_process['price'], 2)}")

# Call
call_strangle = VanillaOption("no dividend share", {"option_type":"call", "strike":102})
call_strangle_process = process.pricing(call_strangle)
print(f"Call (strike 102) : Prix = {round(call_strangle_process['price'], 2)}")

# Strangle
strangle = OptionProducts("strangle","long",{"call":call_strangle,"call price": call_strangle_process['price'],"put":put_strangle,"put price":put_strangle_process['price']})
print(f"Prix du strangle (long) : {round(strangle.price(),2)}")
strangle_greeks = OptionProductsRisk(strangle, process)
print(f"Greeks -> {strangle_greeks.greeks()}")

print("           ")

############################# STRIP

# Put
put_strip = VanillaOption("no dividend share", {"option_type":"put", "strike":102})
put_strip_process = process.pricing(put_strip)
print(f"Put (strike 102) : Prix = {round(put_strip_process['price'], 2)}")

# Call
call_strip = VanillaOption("no dividend share", {"option_type":"call", "strike":102})
call_strip_process = process.pricing(call_strip)
print(f"Call (strike 102) : Prix = {round(call_strip_process['price'], 2)}")

# Strip
strip = OptionProducts("strip","long",{"call":call_strip,"call price": call_strip_process['price'],"put":put_strip,"put price":put_strip_process['price']})
print(f"Prix du strip (long) : {round(strip.price(),2)}")
strip_greeks = OptionProductsRisk(strip, process)
print(f"Greeks -> {strip_greeks.greeks()}")

print("           ")

############################# STRAP

# Put
put_strap = VanillaOption("no dividend share", {"option_type":"put", "strike":102})
put_strap_process = process.pricing(put_strap)
print(f"Put (strike 102) : Prix = {round(put_strap_process['price'], 2)}")

# Call
call_strap = VanillaOption("no dividend share", {"option_type":"call", "strike":102})
call_strap_process = process.pricing(call_strap)
print(f"Call (strike 102) : Prix = {round(call_strap_process['price'], 2)}")

# Strap
strap = OptionProducts("strap","long",{"call":call_strap,"call price": call_strap_process['price'],"put":put_strap,"put price":put_strap_process['price']})
print(f"Prix du strap (long) : {round(strap.price(),2)}")
strap_greeks = OptionProductsRisk(strap, process)
print(f"Greeks -> {strap_greeks.greeks()}")

print("           ")

########################################## BINARY OPTIONS #####################################

high_low = BinaryOption({"strike":102, "option_type":"binary_call", "payoff_amount": 120})
high_low_process = process.pricing(high_low)
print(f"Prix du high_low : {round(high_low_process['price'],2)}")
print(f"proba du high_low : {round(high_low_process['proba'],2)}")

one_touch = BinaryOption({"strike":102, "option_type":"one_touch", "payoff_amount": 120, "barrier":110})
one_touch_process = process.pricing(one_touch)
print(f"Prix du one_touch : {round(one_touch_process['price'],2)}")
print(f"proba du one_touch : {round(one_touch_process['proba'],2)}")

double_one_touch =  BinaryOption({"strike":102, "option_type":"double_one_touch", "payoff_amount": 120, "upper_barrier":110, "lower_barrier":90})
double_one_touch_process = process.pricing(double_one_touch)
print(f"Prix du double_one_touch : {round(double_one_touch_process['price'],2)}")
print(f"proba du double_one_touch : {round(double_one_touch_process['proba'],2)}")

print("           ")

########################################### TEST BARRIER OPTIONS : ###########################################

# Test Knock Out Option (KO) : 
barrier_KO = KnockOutOption({"barrier":120, "strike":100})
KO_option = process.pricing(barrier_KO, monte_carlo=True)
print(f"KO Option : Prix = {round(KO_option['price'], 2)}, proba d'exercice = {round(KO_option['proba'], 2)}")

# Test Knock In Option (KI) : 
barrier_KI= KnockInOption({"barrier":120, "strike":100})
KI_option = process.pricing(barrier_KI, monte_carlo=True)
print(f"KI Option : Prix = {round(KI_option['price'], 2)}, proba d'exercice = {round(KI_option['proba'], 2)}")

########################################### TEST STRUCTURED PRODUCTS : #######################################

############################# REVERSE CONVERTIBLE

# Put
put_rc = VanillaOption("no dividend share", {"option_type":"put", "strike":102})
put_rc_process = process.pricing(put_rc)
print(f"Put (strike 102) : Prix = {round(put_rc_process['price'], 2)}")

# Bond
bond_rc = FixedBond(coupon_rate=0.1, maturity=maturity, nominal=100, nb_coupon=22, rate=rate)
print(f"Prix de l'obligation à taux fixe = {round(bond_rc.price(), 2)}")

# Reverse Convertible
rc = ReverseConvertible({"put":put_rc, "put price": put_rc_process["price"], 
                         "bond":bond_rc, "bond price": bond_rc.price(),
                         "coupon":0.05})
print(f"Reverse Convertible price -> {rc.price()}")

print("           ")

############################# CERTIFICAT OUTPERFORMANCE

# Call
call_co = VanillaOption("no dividend share", {"option_type":"call", "strike":100})
call_co_process = process.pricing(call_co)
print(f"Call (strike 100) : Prix = {round(call_co_process['price'], 2)}")

# Zero strike call
call_zs_co = VanillaOption("no dividend share", {"option_type":"call", "strike":0})
call_zs_co_process = process.pricing(call_zs_co)
print(f"Call (strike 0) : Prix = {round(call_zs_co_process['price'], 2)}")

# Certificat outperformance
co = CertificatOutperformance(spot=100,
                              inputs={"zero strike call": call_zs_co, "zero strike call price": call_zs_co_process["price"],
                               "call":call_co, "call price":call_co_process["price"]})
print(f"Certificat Outperformance price -> {co.price()}")

print("           ")

"""
    Résumé : 
        - maturity : OK
        - rate : OK
        
            ### Obligations : ###
        - zcBond : OK
        - bond : OK
        - optim : OK
        - risk : OK
        
            ### Options Vanilles : ###
        - brownianMotion : OK
        - products : OK
        - risk : OK
        - graphiques :
        
            ### Options à barrières : ###
        - brownianMotion : OK
        - products : OK
        - risk :

            ### Produits à stratégie optionnelle : ###
        - produits : OK
        - greeks : OK
        - proba d'exercice :
        - graphiques :

            ### Options binaires : ###
        - produits : OK
        - risk :

            ### Produits Structurés : ###
        - produits : OK
        - risk :

        Problème : run time error sur le discount factor "compounded"
    
"""