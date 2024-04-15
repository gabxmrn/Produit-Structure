# Financial Models Analysis Tool
## Université Paris Dauphine - PSL | Master 272 - Quantitative Finance
### Meghna Bhaugeerutty, Caroline Kirch, Gabrielle Morin

Welcome to the Financial Models Analysis Tool, an interactive Streamlit application designed to perform financial analysis and simulation across various financial products including bonds, vanilla options, barrier options, binary options, structured products, and optional strategy products. This tool utilizes Monte Carlo simulation techniques and other financial modeling methods to provide insights into the pricing and risk management of these products.

### Features
- Financial Product Analysis: Support for various financial products such as vanilla and barrier options, bonds, and structured financial products.
- Monte Carlo Simulations: Enables the simulation of price paths for options and other financial instruments to assess potential future outcomes.
- Interactive Inputs: Users can input parameters such as rates, maturities, and other product-specific variables to tailor the analysis.
- Graphical Visualizations: Incorporates Plotly for dynamic, interactive visualizations of simulation results.
- Stress Testing: Facilitates stress testing of financial products to understand potential risks under adverse conditions.

### Installation
This application is built using Python and Streamlit, and it requires several dependencies to run properly.
**Prerequisites**: Python 3.7+, pip

#### Setup Instructions
1. Clone the repository
```bash 
git clone https://github.com/gabxmrn/Produit-Structure.git
cd Produit-Structure
```

2. Create a virtual environment and install required libraries
```bash 
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

3. Run the application
```bash
streamlit run app.py
```

Alternatively, you can modify the information for each product in the `main.py` file from Python directly : 
3.1 Run from Python
```bash
python main.py
```

### Usage
After starting the application, navigate through the sidebar to select the type of financial product you wish to analyze. Input the required parameters through the user-friendly interface, and hit the simulate button to see the results displayed along with graphical outputs where applicable.

#### Analyzing Different Financial Products
- **Bond Pricing**: Choose between zero-coupon and fixed coupon bonds. Enter details such as nominal value, maturity, and interest rate.
- **Options**: Analyze vanilla options by specifying the underlying asset, strike price, and expiration. Barrier and binary options are also supported with additional configuration for barriers.
- **Structured Products**: Set up parameters for products like reverse convertibles or outperformance certificates.
Results will include pricing outputs, graphical representations of price movements, and risk metrics depending on the product being analyzed.