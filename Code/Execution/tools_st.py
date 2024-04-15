import streamlit as st
from RisksAnalysis.stressScenarios import StressScenario

def display_greeks(greeks_dict):
    """
    Function to display sensitivity (Greeks) values in a consistent format.
    
    Parameters:
    - greeks_dict (dict): A dictionary containing sensitivity values (e.g., delta, gamma, vega, rho, theta).
    """
    st.expander("Sensitivities")
    cols = st.columns(5)
    cols[0].write(f"$\delta$: {greeks_dict['delta']}")
    cols[1].write(f"$\gamma$: {greeks_dict['gamma']}")
    cols[2].write(f"$v$: {greeks_dict['vega']}")
    cols[3].write(f"ρ : {greeks_dict['rho']}")
    cols[4].write(f"θ : {greeks_dict['theta']}") 
    
    st.write(
        """
        - $\delta$ represents the equity exposure, i.e., the change in option price due to the spot.
        - $\gamma$ represents the payout convexity, i.e., the change in delta due to the spot.
        - $v$ represents the volatility exposure, i.e., the change in option price due to the volatility.
        - ρ represents the interest rate exposure, i.e., the change in option price due to interest rates.
        - θ represents the time decay, i.e., the change in option price due to time passing.
        """
    )
    
def select_underlying_asset():
    """
    Function to display and select the underlying asset and related parameters.

    Returns:
    - underlying (str): Chosen underlying asset type.
    - dividend (float or None): Selected dividend rate (if applicable).
    - domestic_rate (float or None): Selected domestic rate (if applicable).
    - forward_rate (float or None): Selected forward rate (if applicable).
    """
    underlying = st.selectbox('Choose the underlying asset for the option', 
                              ['non capitalized index', 'no dividend share', 'dividend share', 'forex rate'])
    dividend, domestic_rate, forward_rate = None, None, None

    if underlying == "dividend share":
        dividend = st.slider('Dividend Rate', min_value=0.0, max_value=1.0, value=0.02)
    elif underlying == "forex rate":
        col1, col2 = st.columns(2)
        domestic_rate = col1.slider('Domestic Rate', min_value=0.0, max_value=1.0, value=0.02)
        forward_rate = col2.slider('Forward Rate', min_value=0.0, max_value=1.0, value=0.02)

    return underlying, dividend, domestic_rate, forward_rate

def display_results(asset, proba=False, greeks=False, s_t=False):
    if s_t:
        st.subheader('Stress Testing Results')
    if proba:
        col1, col2 = st.columns(2)
        col1.write(f"Price = {round(asset['price'], 2)}")
        col2.write(f"Exercise Probability = {round(asset['proba'], 2)}")
    else:
        st.write(f"Price = {round(asset['price'], 2)}")
    if greeks:
        display_greeks(asset)
    

def stress_test_input():
    st.header("Stress Testing")
    col1, col2 = st.columns(2)
    new_val = col1.number_input('New Spot', value=120, step=10)
    new_mat = col2.number_input('New Maturity in years',  value=0.5, min_value=0.0)
    stress_test = StressScenario(new_spot=new_val, new_maturity_in_years=new_mat)
    return stress_test