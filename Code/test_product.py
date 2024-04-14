from datetime import datetime

from maturity import Maturity 
from rate import Rate
from run import Run, StressTest

########################################### TEST MATURITY, RATE & ST : ###########################################

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

#### STRESS TEST

# stress_test = StressTest(new_spot=120, new_begin_date=datetime(2024, 7, 7))
stress_test = StressTest(new_spot=120, new_maturity_in_years=0.5)

### BASICS INPUTS : 

inputs_dict = {"strike":102, 
                "nb_simulations":1000,
                "nb_steps":1000,
                "spot":100,
                "rates":Rate(0.03, rate_type="compounded"),
                "volatility":0.2,
                "maturity":Maturity(0.5)}

################################################ TEST BONDS : ################################################

#### ZERO COUPON BOND

print("OBLIGATION ZERO COUPON : ")
zc_bond = Run().zc_bond(inputs={"rate":rate, "maturity":maturity, "nominal":100})
print(zc_bond)
st_zc_bond = stress_test.zc_bond(inputs={"rate":rate, "maturity":maturity, "nominal":100})
print(st_zc_bond)

#### FIXED BOND

print("OBLIGATION A TAUX FIXE : ")
fixed_bond = Run().fixed_bond(inputs={"coupon_rate":0.1, "maturity":maturity, "nominal":100, "nb_coupon":22, "rate":rate})
print(fixed_bond)
st_fixed_bond = stress_test.fixed_bond(inputs={"coupon_rate":0.1, "maturity":maturity, "nominal":100, "nb_coupon":22, "rate":rate})
print(st_fixed_bond)

print("           ")


########################################### TEST VANILLA OPTIONS : ###########################################

#### CALL / PUT (simple)

print("CALL (No dividend share) : ")
simple_call = Run().vanilla_option(inputs={**inputs_dict, **{"underlying":"no dividend share", "option_type":"call"}})
print(simple_call)
st_simple_call = stress_test.vanilla_option(inputs={**inputs_dict, **{"underlying":"no dividend share", "option_type":"call"}})
print(st_simple_call)

print("PUT (Non capitalized index) : ")
simple_put = Run().vanilla_option(inputs={**inputs_dict, **{"underlying":"non capitalized index", "option_type":"put"}})
print(simple_put)
st_simple_put = stress_test.vanilla_option(inputs={**inputs_dict, **{"underlying":"non capitalized index", "option_type":"put"}})
print(st_simple_put)

#### CALL / PUT (share & forex)

print("CALL (Dividend share) : ")
dividend_call = Run().vanilla_option(inputs={**inputs_dict, **{"underlying":"dividend share", "option_type":"call", "dividend":0.02}}) 
print(dividend_call)
st_dividend_call = stress_test.vanilla_option(inputs={**inputs_dict, **{"underlying":"dividend share", "option_type":"call", "dividend":0.02}})
print(st_dividend_call)

print("PUT (Forex) : ")
forex_put = Run().vanilla_option(inputs={**inputs_dict, **{"underlying":"forex rate", "option_type":"put", "forward_rate":0.2, "domestic_rate":0.1}})
print(forex_put)
st_forex_put = stress_test.vanilla_option(inputs={**inputs_dict, **{"underlying":"forex rate", "option_type":"put", "forward_rate":0.2, "domestic_rate":0.1}})
print(st_forex_put)

print("           ")


########################################### TEST OPTION STRATEGY : ###########################################

###############################

print("           ")


########################################## BINARY OPTIONS #####################################

print("HIGHT LOW (binary call) : ")
high_low = Run().binary_option(inputs={**inputs_dict, **{"option_type":"binary_call", "payoff_amount": 120}})
print(high_low)
st_high_low = stress_test.binary_option(inputs={**inputs_dict, **{"option_type":"binary_call", "payoff_amount": 120}})
print(st_high_low)

print("ONE TOUCH : ")
one_touch = Run().binary_option(inputs={**inputs_dict, **{"option_type":"one_touch", "payoff_amount": 120, "barrier":110}})
print(one_touch)
st_one_touch = stress_test.binary_option(inputs={**inputs_dict, **{"option_type":"one_touch", "payoff_amount": 120, "barrier":110}})
print(st_one_touch)

print("DOUBLE NO TOUCH : ")
double_no_touch = Run().binary_option(inputs={**inputs_dict, **{"option_type":"double_no_touch", "payoff_amount": 120, "upper_barrier":110, "lower_barrier":90}})
print(double_no_touch)
st_double_no_touch = stress_test.binary_option(inputs={**inputs_dict, **{"option_type":"double_no_touch", "payoff_amount": 120, "upper_barrier":110, "lower_barrier":90}})
print(st_double_no_touch)

print("           ")