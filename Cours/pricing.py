from datetime import datetime
from done.Bond import FixedBond
from done.FloatingBond import FloatingBond
from IRSwap import IRSwap
from done.ZcBond import ZcBond
from done.maturity import Maturity
from done.rate import Rate
 
#rate=Rate(rate=0.03, rate_type="compounded")
rate=Rate(
    rate_curve={
        Maturity(1.0/365.0):0.0075,
        Maturity(1.0/12.0):0.01,
        Maturity(3.0/12.0):0.015,
        Maturity(6.0/12.0):0.0175,
        Maturity(1.0):0.02,
        Maturity(5.0):0.03,
    },
    rate_type="compounded"
)
maturity=Maturity(
    begin_date=datetime(2024, 3, 7),
    end_date=datetime(2025, 3, 7),
    day_count_convention="ACT/360"
)
nominal=100
zc_bond=ZcBond(rate, maturity, nominal)
p=zc_bond.price()
print(p) #97.04
 
bond=FixedBond(
    coupon_rate=0.01, 
    maturity=maturity,
    nominal=nominal,
    nb_coupon=2,
    rate=rate
)
print(bond.price())
print(bond.ytm())
 
float_bond=FloatingBond(
    libor_rate=0.01, 
    maturity=Maturity(0.5),
    nominal=nominal,
    nb_coupon=2,
    rate=rate
)
print(float_bond.price())
 
 
swap=IRSwap(
    contract_maturity=maturity,
    fixed_coupon=0.03,
    fixed_nb_coupon=2,
    fixed_pay=True,
    float_nb_coupon=2, 
    libor_maturity=Maturity(0.5),
    libor_rate=0.01,
    rates=rate,
    nominal=100
)
print(swap.price())