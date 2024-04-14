import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from maturity import Maturity
from rate import Rate
from brownianMotion import BrownianMotion
from products import VanillaOption, KnockInOption, KnockOutOption
from riskAnalysis import BondRisk, OptionRisk
from run import Run
st.markdown(
    """
    <style>
    body {
        font-family: "Arial Unicode MS", Arial, sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title('Financial Models Analysis')

model_selection = st.sidebar.selectbox("Select a model to analyse",
                                       ["Bond Pricing", "Vanilla Options", "Barrier Options", 
                                        "Binary Options", "Structured Products"])

st.header("Common Inputs")
###########################################  MATURITY: ###########################################
st.subheader("Maturity")
maturity_type = st.selectbox('Maturity Type', ['Maturity in years', 'Computed'])
if maturity_type == 'Maturity in years':
    mat_value = st.number_input('Maturity in years', value=0.5, min_value=0.0)
    maturity = Maturity(mat_value)

else:
    col1, col2 = st.columns(2)
    begin_date = col1.date_input("Begin Date", value=datetime(2024, 3, 7))
    end_date = col2.date_input("End Date", value=datetime(2025, 3, 7))
    day_count_convention = st.radio("Day Count Convention", 
                                    ["ACT/360", "ACT/365"])
    maturity = Maturity(begin_date=begin_date, 
                        end_date=end_date, 
                        day_count_convention=day_count_convention)

###########################################  RATE  ###########################################
st.subheader("Rate")
rate_input_type = st.selectbox(
    "Select the rate input type",
    ["Specific Rate", "Curve"])
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
    interpol_type = st.selectbox('Interpolation Type', ['linear', 'cubic', 'logarithmic', 'barycentric', 'krogh', ])
    rate = Rate(rate_type=rate_type, 
                interpol_type=interpol_type, 
                rate_curve=curve)
    
#################### BOND PRICING  ######################
if model_selection == "Bond Pricing":
    st.header("Bond Pricing")
    zero_bool = st.radio("Type of coupon detachment",
                         ('Zero-Coupon', 'Fixed'))
    nominal = st.number_input('Nominal Value', min_value=100, value=100, step=100)
    if zero_bool == "Fixed":
        col1, col2 = st.columns(2)
        coupon_rate = col1.number_input('Coupon Rate', min_value=0.0, value=0.1, step=0.1)
        nb_coupon = col2.number_input('Number of coupons', min_value=0, value=50, step=1)

    if st.button('Simulate Bond Pricing'):
        if zero_bool == "Zero-Coupon":
            zc_bond=  Run().zc_bond(inputs={"rate":rate, 
                                            "maturity":maturity, 
                                            "nominal":nominal})
            st.write(f"Zero coupon bond price = {round(zc_bond['price'], 2)}")

        elif zero_bool == "Fixed":
            fixed_bond = Run().fixed_bond(inputs={"coupon_rate":coupon_rate, 
                                                  "maturity":maturity, 
                                                  "nominal":nominal, 
                                                  "nb_coupon":nb_coupon, 
                                                  "rate":rate})

            st.write(f"Fixed rate bond price = {round(fixed_bond['price'], 2)}")
            st.write(f"Yield to Maturity (YTM) of the fixed rate bond = {round(fixed_bond['ytm'], 2)}")
            col1, col2 = st.columns(2)
            col1.write(f"Duration = {round(fixed_bond['duration'], 2)}")
            col2.write(f"Convexity = {round(fixed_bond['convexity'], 2)}")


################## OPTIONS ################
if model_selection in ["Vanilla Options", "Barrier Options", "Binary Options", "Structured Products"]:
    st.subheader("Inputs to initialise the Brownian Motion")
    nb_simulations = st.number_input('Number of Simulations', value=1000, min_value=1)
    nb_steps = st.number_input('Number of Steps', value=100, min_value=1)
    spot = st.number_input('Spot Price', value=100.0)
    volatility = st.slider('Volatility', min_value=0.0, max_value=1.0, value=0.2)
    strike_price = st.number_input('Strike Price', value=100.0)

    inputs_dict = { "nb_simulations":nb_simulations,
                    "nb_steps":nb_steps,
                    "spot":spot,
                    "rates":rate,
                    "volatility":volatility,
                    "maturity":maturity, 
                    "strike":strike_price}
    
    if model_selection == "Vanilla Options":
        st.header("Vanilla Options")
        option_type = st.radio('Option Type', ['Call', 'Put'])
        underlying =  st.selectbox('Choose the underlyng asset for the option', 
                                   ['non capitalized index', 'no dividend share', 'forex rate'])

        if st.button('Simulate'):
            vanilla_option = Run().vanilla_option(inputs={**inputs_dict, 
                                                          **{"underlying":"no dividend share", 
                                                        "option_type":option_type,
                                                        }})
            col1, col2 = st.columns(2)
            col1.write(f"Price = {round(vanilla_option['price'], 2)}")
            col2.write(f"Exercise Probability = {round(vanilla_option['proba'], 2)}")
            greeks_display = st.expander("Sensitivities")
            cols = greeks_display.columns(5)
            cols[0].write( f"$\delta$: {vanilla_option['delta']}")
            cols[1].write( f"$\gamma$: {vanilla_option['gamma']}")
            cols[2].write( f"$v$: {vanilla_option['vega']}")
            cols[3].write( f"ρ: {vanilla_option['rho']}")
            cols[4].write( f" θ: {vanilla_option['theta']}")
            greeks_display.write(
                f"""
                - $\delta$ represents the equity exposure, i.e., the change in option price due to the spot. \n
                - $\gamma$ represents the payout convexity, i.e., the change in delta due to the spot. \n
                - $v$ represents the volatility exposure, i.e., the change in option price due to the volatility. \n
                - ρ represents the interest rate exposure, i.e., the change in option price due to interest rates. \n
                - θ represents the time decay, i.e., the change in option price due to time passing. \n
                """
            )

    elif model_selection == "Binary Options":
        st.header("Binary Options")
        binary_input =  st.selectbox('Choose the type of binary option', 
                                   ['Binary put', 'Binary call',
                                    'One touch', 'No touch', 
                                    'Double one touch', 'Double no touch']).lower().replace(" ", "_")
        barrier, lower_barrier, upper_barrier = None, None, None
        if binary_input in ["one_touch", "no_touch"]:
            barrier = st.number_input('Input barrier', value=120.0)
        elif binary_input in  ["double_one_touch", "double_no_touch"] :
            col1, col2 = st.columns(2)
            lower_barrier = col1.number_input("Lower barrier", value=90.0)
            upper_barrier = col2.number_input("Upper barrier", value=110.0)
        payoff_amount = st.number_input('Payoff amount', value=100.0)
        if st.button('Simulate Barrier Option'):
            binary_option = Run().binary_option(inputs={**inputs_dict, 
                                                        **{"option_type":binary_input, 
                                                           "payoff_amount": payoff_amount}, 
                                                        ** {"barrier":barrier, 
                                                            "lower_barrier":lower_barrier, 
                                                            "upper_barrier":upper_barrier}})
            col1, col2 = st.columns(2)
            col1.write(f"Price = {round(binary_option['price'], 2)}")
            col2.write(f"Exercise Probability = {round(binary_option['proba'], 2)}")

    elif model_selection == "Barrier Options":
        st.header("Barrier Options")
        MC_sim = True
        barrier = st.number_input('Barrier Level', value=120, step=10)
        KI_KO_bool = st.radio("Type of barrier option",
                                ('Knock-In', 'Knock-Out')).lower().replace('-', "_")
        if st.button('Simulate Barrier Option'):
            barrier_option = Run().barrier_option(inputs={**inputs_dict,
                                                           **{"option_type":KI_KO_bool, 
                                                              "barrier":barrier, 
                                                              "strike":strike_price}})

            col1, col2 = st.columns(2)
            col1.write(f"Price = {round(barrier_option['price'], 2)}")
            col2.write(f"Exercise Probability = {round(barrier_option['proba'], 2)}")
            plot_display = st.expander("Plot")

            price_paths = barrier_option['paths']
            fig = go.Figure()
            for i in range(price_paths.shape[0]):
                fig.add_trace(go.Scatter(x=np.arange(price_paths.shape[1]), y=price_paths[i, :], mode='lines', 
                                            line=dict(width=1), showlegend=False))
            fig.add_trace(go.Scatter(x=[0, price_paths.shape[1]-1], y=[barrier, barrier],
                         mode='lines', line=dict(color="Red", width=4, dash="dashdot"),
                         name=f'Barrier Level: {barrier}'))
            fig.update_layout(title='Monte Carlo Simulation price paths',
                            xaxis_title='Time Step',
                            yaxis_title='Price',
                            xaxis=dict(showgrid=False),
                            yaxis=dict(showgrid=False))

            st.plotly_chart(fig)
