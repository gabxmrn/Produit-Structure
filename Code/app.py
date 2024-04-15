import streamlit as st
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from Products.maturity import Maturity
from Products.rate import Rate
from Execution.run import Run, StressTest
from Execution.tools_st import select_underlying_asset, display_results, stress_test_input

st.title('Financial Models Analysis')

model_selection = st.sidebar.selectbox("Select a model to analyse",
                                       ["Bond Pricing", "Vanilla Options", "Barrier Options", 
                                        "Binary Options", "Structured Products", 
                                        "Optional Strategy Products"])

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
rate_input_type = st.selectbox("Select the rate input type",
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
##### STRESS TESTING ####    
s_t = stress_test_input()

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
            display_results(zc_bond)
            stress_test = s_t.zc_bond(inputs={"rate":rate, 
                                "maturity":maturity, 
                                "nominal":nominal})
            
            display_results(stress_test, s_t=True)


        elif zero_bool == "Fixed":
            fixed_bond = Run().fixed_bond(inputs={"coupon_rate":coupon_rate, 
                                                  "maturity":maturity, 
                                                  "nominal":nominal, 
                                                  "nb_coupon":nb_coupon, 
                                                  "rate":rate})
            display_results(fixed_bond)
            st.write(f"Yield to Maturity (YTM) of the fixed rate bond = {round(fixed_bond['ytm'], 2)}")
            col1, col2 = st.columns(2)
            col1.write(f"Duration = {round(fixed_bond['duration'], 2)}")
            col2.write(f"Convexity = {round(fixed_bond['convexity'], 2)}")
            stress_test = s_t.fixed_bond(inputs={"coupon_rate":coupon_rate, 
                                   "maturity":maturity, 
                                   "nominal":nominal, 
                                   "nb_coupon":nb_coupon, 
                                   "rate":rate})
            display_results(stress_test, s_t=True)



################## OPTIONS ################
if model_selection in ["Vanilla Options", "Barrier Options", "Binary Options", "Structured Products","Optional Strategy Products"]:
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
        underlying, dividend, domestic_rate, forward_rate = select_underlying_asset()

        if st.button('Simulate'):
            vanilla_option = Run().vanilla_option(inputs={**inputs_dict, 
                                                          **{"underlying":underlying, 
                                                            "option_type":option_type,},
                                                          ** {"dividend": dividend, 
                                                              "forward_rate": forward_rate,
                                                            "domestic_rate": domestic_rate,}})
            st.write(f"Payoff Amount = {round(vanilla_option['payoff'], 2)}")            
            display_results(vanilla_option, proba=True, greeks=True)
            stress_test = s_t.vanilla_option(inputs={**inputs_dict, 
                                **{"underlying":underlying, 
                                  "option_type":option_type,},
                                ** {"dividend": dividend, 
                                    "forward_rate": forward_rate,
                                  "domestic_rate": domestic_rate,}})
            display_results(stress_test, proba=True, greeks=True, s_t=True)




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

        if st.button('Simulate Binary Option'):
            binary_option = Run().binary_option(inputs={**inputs_dict, 
                                                        **{"option_type":binary_input, 
                                                           "payoff_amount": payoff_amount}, 
                                                        ** {"barrier":barrier, 
                                                            "lower_barrier":lower_barrier, 
                                                            "upper_barrier":upper_barrier}})
            display_results(binary_option, proba=True)
            stress_test = s_t.vanilla_option(inputs={**inputs_dict, 
                                **{"option_type":binary_input, 
                                   "payoff_amount": payoff_amount}, 
                                ** {"barrier":barrier, 
                                    "lower_barrier":lower_barrier, 
                                    "upper_barrier":upper_barrier}})
            display_results(stress_test, proba=True, s_t=True)


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

            display_results(barrier_option, proba=True)
                    
            stress_test = s_t.barrier_option(inputs={**inputs_dict,
                            **{"option_type":KI_KO_bool, 
                                "barrier":barrier, 
                                "strike":strike_price}})             
            display_results(stress_test, proba=True, s_t=True)

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



    elif model_selection == "Optional Strategy Products":
        st.header("Optional Strategy Products")
        opt_prod_choice =  st.selectbox('Choose the type of binary option', 
                            ['Spread', 'Straddle', 'Strip', 'Strap'
                            'Strangle', 'Butterfly']).lower().replace(" ", "_")
        
        ### SPREAD ###
        if opt_prod_choice == "spread":
            option_type = st.radio('Option Type', ['Call', 'Put'])
            underlying, dividend, domestic_rate, forward_rate = select_underlying_asset()

            col1, col2 = st.columns(2)
            short_strike = col1.number_input('Short strike', value=105)
            long_strike = col2.number_input('Long strike', value=95)

            if st.button('Simulate Spread Options'):
                spread = Run().spread(inputs={**inputs_dict, 
                                              **{"underlying":underlying, 
                                                  "option_type":option_type,
                                                  "long_strike":long_strike, 
                                                  "short_strike":short_strike},
                                              ** {"dividend": dividend, 
                                                  "forward_rate": forward_rate,
                                                  "domestic_rate": domestic_rate,}})
                display_results(spread, greeks=True)
                stress_test = s_t.spread(inputs={**inputs_dict, 
                                  **{"underlying":underlying, 
                                      "option_type":option_type,
                                      "long_strike":long_strike, 
                                      "short_strike":short_strike},
                                  ** {"dividend": dividend, 
                                      "forward_rate": forward_rate,
                                      "domestic_rate": domestic_rate,}})     
                display_results(stress_test, greeks=True, s_t=True)

                
        elif opt_prod_choice in ["straddle", "strangle", "strip", "strap"]:
            option_pos = st.radio('Option position', ['Short', 'Long']).lower()
            underlying, dividend, domestic_rate, forward_rate = select_underlying_asset()

            col1, col2 = st.columns(2)
            call_strike = col1.number_input('Call strike', value=105)
            put_strike = col2.number_input('Put strike', value=95)

            if st.button('Simulate Strategy Options'):
                option = Run().option_strategy(inputs={**inputs_dict, 
                                            **{"underlying":underlying, 
                                                "option_type":opt_prod_choice,
                                                "call_strike":call_strike, 
                                                "put_strike":put_strike},
                                            ** {"dividend": dividend, 
                                                "forward_rate": forward_rate,
                                                "domestic_rate": domestic_rate,}})
                display_results(option, greeks = True)
                stress_test = s_t.option_strategy(inputs={**inputs_dict, 
                            **{"underlying":underlying, 
                                "option_type":opt_prod_choice,
                                "call_strike":call_strike, 
                                "put_strike":put_strike},
                            ** {"dividend": dividend, 
                                "forward_rate": forward_rate,
                                "domestic_rate": domestic_rate,}})
                display_results(stress_test, greeks=True, s_t=True)

    elif model_selection == "Structured Products":
        st.header("Structured Products")
        struct_choice = st.selectbox("Choose your structured product",
                            ('Reverse Convertible', 'Certificat Outperformance'))
        underlying, dividend, domestic_rate, forward_rate = select_underlying_asset()

        if struct_choice == "Reverse Convertible":
            nominal = st.number_input('Nominal Value', min_value=100, value=100, step=100)
            col1, col2 = st.columns(2)
            coupon_rate = col1.number_input('Coupon Rate', min_value=0.0, value=0.1, step=0.1)
            nb_coupon = col2.number_input('Number of coupons', min_value=0, value=50, step=1)
        elif struct_choice == "Certificat Outperformance":
            call_strike = st.number_input('Call Strike', min_value=100, value=100, step=100)

        if st.button('Simulate Structured Products'):
            if struct_choice == "Reverse Convertible":
                reverse_convertible = Run().reverse_convertible(inputs={**inputs_dict, 
                                                                        "coupon_rate":coupon_rate, 
                                                                        "nominal":nominal, 
                                                                        "nb_coupon":nb_coupon,
                                                                        "underlying":underlying,
                                                                        "strike" : strike_price,
                                                                    ** {"dividend": dividend, 
                                                                    "forward_rate": forward_rate,
                                                                    "domestic_rate": domestic_rate,}})
                display_results(reverse_convertible)
                stress_test = s_t.reverse_convertible(inputs={**inputs_dict, 
                                                "coupon_rate":coupon_rate, 
                                                "nominal":nominal, 
                                                "nb_coupon":nb_coupon,
                                                "underlying":underlying,
                                                "strike" : strike_price,
                                                ** {"dividend": dividend, 
                                                "forward_rate": forward_rate,
                                                "domestic_rate": domestic_rate,}})
                display_results(stress_test, s_t=True)

            elif struct_choice == "Certificat Outperformance":
                certificat_outperformance = Run().certificat_outperformance(inputs={**inputs_dict, 
                                                                                    "underlying":underlying, 
                                                                                    "call_strike":call_strike, 
                                                                                ** {"dividend": dividend, 
                                                                                "forward_rate": forward_rate,
                                                                                "domestic_rate": domestic_rate,}})
                display_results(certificat_outperformance)
                stress_test = s_t.certificat_outperformance(inputs={**inputs_dict,
                                                   "underlying":underlying, 
                                                    "call_strike":call_strike, 
                                                   ** {"dividend": dividend, 
                                                   "forward_rate": forward_rate,
                                                   "domestic_rate": domestic_rate,}})
                display_results(stress_test, s_t=True)


