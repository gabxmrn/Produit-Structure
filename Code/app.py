import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from maturity import Maturity
from rate import Rate
from bond import FixedBond, ZcBond
from brownianMotion import BrownianMotion
from products import VanillaOption, KnockInOption, KnockOutOption
from riskAnalysis import BondRisk, OptionRisk

st.title('Financial Models Analysis')

# Sidebar for model selection
model_selection = st.sidebar.selectbox("Select a Model to Analyze",
                                       ["Bond Pricing", "Vanilla Options", "Barrier Options"])

st.header("Common Inputs")
###########################################  MATURITY: ###########################################
st.subheader("Maturity")
maturity_type = st.selectbox('Maturity Type', ['Maturity in years', 'Computed'])
if maturity_type == 'Maturity in years':
    mat_value = st.number_input('Maturity in years', value=5.0, min_value=0.0)
    maturity = Maturity(mat_value)

else:
    begin_date = st.date_input("Begin Date", value=datetime(2024, 3, 7))
    end_date = st.date_input("End Date", value=datetime(2025, 3, 7))
    day_count_convention = st.selectbox("Day Count Convention", ["ACT/360", "ACT/365"])
    maturity = Maturity(begin_date=begin_date, 
                        end_date=end_date, 
                        day_count_convention=day_count_convention)

###########################################  RATE  ###########################################
st.subheader("Rate")
rate_input_type = st.selectbox(
    "Select the rate input type",
    ["Specific Rate", "Curve"]
)
rate_type = st.selectbox('Rate Type', ['compounded', 'continuous'])
if rate_input_type == "Specific Rate":
    specific_rate = st.number_input('Enter the specific rate', value=0.03, step=0.01, format="%.2f")
    rate = Rate(rate=specific_rate, 
                rate_type=rate_type)

else:
    st.write("Dynamic Inputs for Curve Values")
    st.write("Input maturity and rate pairs for the curve:")
    maturity_1D = st.number_input('Rate for 1 day (1/365 year)', value=0.0075, format="%.4f")
    maturity_1M = st.number_input('Rate for 1 month (1/12 year)', value=0.01, format="%.4f")
    maturity_3M = st.number_input('Rate for 3 months (3/12 year)', value=0.015, format="%.4f")
    maturity_6M = st.number_input('Rate for 6 months (6/12 year)', value=0.0175, format="%.4f")
    maturity_1Y = st.number_input('Rate for 1 year', value=0.02, format="%.4f")
    maturity_5Y = st.number_input('Rate for 5 years', value=0.03, format="%.4f")
    curve = {Maturity(1.0/365.0):maturity_1D,
        Maturity(1.0/12.0):maturity_1M,
        Maturity(3.0/12.0):maturity_3M,
        Maturity(6.0/12.0):maturity_6M,
        Maturity(1.0):maturity_1Y,
        Maturity(5.0):maturity_5Y,
        }
    interpol_type = st.selectbox('Interpolation Type', ['linear', 'logarithmic'])
    rate = Rate(rate_type=rate_type, 
                interpol_type=interpol_type, 
                rate_curve=curve)

if model_selection == "Bond Pricing":
    st.header("Bond Pricing")
    zero_bool = st.radio("Type of coupon detachment",
                         ('Zero-Coupon', 'Fixed'))
    nominal = st.number_input('Nominal Value', min_value=100, value=1000, step=100)
    if zero_bool == "Zero-Coupon":
        zc_bond=  ZcBond(rate=rate, maturity=maturity, nominal=100)
        st.write(f"Prix zero coupon bond = {round(zc_bond.price(), 2)}")
    else:
        coupon_rate = st.number_input('Coupon Rate', min_value=0.0, value=0.5, step=0.1)
        nb_coupon = st.number_input('Number of coupons', min_value=0, value=50, step=1)
        fixed_bond = FixedBond(coupon_rate=coupon_rate, 
                               maturity=maturity, 
                               nominal=nominal, 
                               nb_coupon=nb_coupon, 
                               rate=rate)
        st.write(f"Prix de l'obligation à taux fixe = {round(fixed_bond.price(), 2)}")
        st.write(f"YTM de l'obligation à taux fixe = {round(fixed_bond.ytm(), 2)}")

################## OPTIONS ################
if model_selection in ["Vanilla Options", "Barrier Options"]:
    st.subheader("Inputs to initialise the Brownian Motion")
    nb_simulations = st.number_input('Number of Simulations', value=1000, min_value=1)
    nb_steps = st.number_input('Number of Steps', value=100, min_value=1)
    spot = st.number_input('Spot Price', value=100.0)
    volatility = st.slider('Volatility', min_value=0.0, max_value=1.0, value=0.2)
    rate_value = st.slider('Volatility', min_value=0.0, max_value=4.0, value=0.2)
    rate = Rate(rate=rate_value, 
                rate_type=rate_type,) 
    
    process_params = {
        "nb_simulations": nb_simulations,
        "nb_steps": nb_steps,
        "spot": spot,
        "rates": rate,
        "volatility": volatility,
        "maturity": maturity,
    }

    if model_selection == "Vanilla Options":
        st.header("Vanilla Options")
        option_type = st.selectbox('Option Type', ['Call', 'Put'])
        strike_price = st.number_input('Strike Price', value=100.0)

        if st.button('Simulate'):
            process = BrownianMotion(process_params)
            option_params = {
                "option_type": option_type,
                "strike": strike_price,
            }
            vanilla_option = VanillaOption(option_params)        
            result = process.pricing(vanilla_option)
            st.write(f"Price = {round(result['price'], 2)}, Exercise Probability = {round(result['proba'], 2)}")

    elif model_selection == "Barrier Options":
        st.header("Barrier Options")
        MC_sim = True
        barrier = st.number_input('Barrier Level', value=120, step=10)
        KI_KO_bool = st.radio("Type of barrier option",
                                ('Knock-In', 'Knock-Out'))
        if st.button('Simulate Barrier Option'):
            process = BrownianMotion(process_params)
            option_params = {"barrier": barrier, 
                            "strike": 100.0}  
            if KI_KO_bool == 'Knock-In':
                option = KnockInOption(option_params)
            else:  
                option = KnockOutOption(option_params)
            result = process.pricing(option, monte_carlo=MC_sim)
            price = round(result['price'], 2)
            exercise_prob = round(result['proba'], 2)
            st.write(f"Option Price = {price}, Exercise Probability = {exercise_prob}")
            price_paths = process.paths_plot
            fig = go.Figure()
            for i in range(price_paths.shape[0]):
                fig.add_trace(go.Scatter(x=np.arange(price_paths.shape[1]), y=price_paths[i, :], mode='lines', 
                                            line=dict(width=1), showlegend=False))
            fig.add_trace(go.Scatter(x=[0, price_paths.shape[1]-1], y=[barrier, barrier],
                         mode='lines', line=dict(color="Red", width=4, dash="dashdot"),
                         name=f'Barrier Level: {barrier}'))
            fig.update_layout(title='Monte Carlo Simulation Price Paths',
                            xaxis_title='Time Step',
                            yaxis_title='Price',
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=False))
            # fig.add_trace(go.Scatter(x=0, y=barrier, mode='lines',
            #              line=dict(color="Red", width=4, dash="dashdot"),
            #              name=f'Barrier Level: {barrier}'))

            # fig.add_shape(type="line",  x0=0, y0=barrier, x1=price_paths.shape[1]-1, y1=barrier,
            #                     line=dict(color="Red", width=4, dash="dashdot"))
            st.plotly_chart(fig)
