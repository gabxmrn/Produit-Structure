from Products.products import VanillaOption, OptionProducts, Spread, ButterflySpread, ReverseConvertible, CertificatOutperformance
from Products.rate import Rate
from Products.maturity import Maturity
from Products.brownianMotion import BrownianMotion
from Products.bond import FixedBond
from riskAnalysis import OptionRisk, OptionProductsRisk, SpreadRisk, ButterflySpreadRisk, StructuredProductsRisk

import matplotlib.pyplot as plt


class GraphsOptions:
    """ A class representing the graphic of an option.
    Argument:
        _opt_type (str): product type (option or option strategy).
        _long_short (str): if the product is long or short.
        _graph_type (str): type of graphical representation.
        _rate (Rate): rate of the financial product.
        _vol (float): volatility of the financial product.
        _maturity (Maturity): maturity of the financial product.
        _product (VanillaOption, Spread, ButterflySpread or OptionProducts) : the financial product.
        _product_price (float): product price.
    """

    def __init__(self, graph_type: str, 
                 rate: Rate, maturity: Maturity, vol: float,
                 underlying: str, opt_type: str, long_short: str, strike: float, 
                 strike2_strangle_spread: float = None, strike3_spread: float = None) -> None:
        """
        Initialize a GraphsOption object.
        Args:
            graph_type (str): type of graphical representation.
            rate (Rate): rate of the financial product.
            maturity (Maturity): maturity of the financial product.
            vol (float): volatility of the financial product.
            underlying (str): underlying of the financial product.
            opt_type (str): type of financial product.
            long_short (str): if the product is long or short.
            strike (float): strike of the financial product.
            strike2_strangle_spread (float, optional): a second strike, greater than strike. Defaults to None.
            strike3_spread (float, optional): a third strike, greater than strike and strike2. Defaults to None.
        """

        # Check inputs
        self._opt_type = opt_type.lower()
        if self._opt_type not in ["call", "put", "straddle", "strangle", "strip", "strap", "call spread", "put spread", "butterfly spread"]:
            raise Exception("Input error: Wrong option type, please enter call, put, straddle, strangle, strip, strap, call spread, put spread, or butterfly spread.")

        self._long_short = long_short.lower()
        if self._long_short not in ["long", "short"]:
            raise Exception("Input error: Position must be long or short.")

        self._graph_type = graph_type.lower()
        if self._graph_type not in ["payoff", "profit", "delta", "gamma", "vega", "theta", "rho"]:
            raise Exception("Input error: graph type must be payoff, profit, delta, gamma, vega, theta, rho.")

        if strike >= strike2_strangle_spread or strike >= strike3_spread or strike2_strangle_spread >= strike3_spread:
            raise Exception("Input error: Strikes must be as follow : strike < strike2 < strik3.")

        # Process creation
        self._rate = rate
        self._vol = vol
        self._maturity = maturity
        process = BrownianMotion({
            "nb_simulations":1000,
            "nb_steps":1000,
            "spot":100,
            "rates":self._rate,
            "volatility":self._vol,
            "maturity":self._maturity
        })
        
        # Product creation
        if self._opt_type in ["call", "put"]:
            self._product = VanillaOption(underlying,
                                          {"option_type": self._opt_type, "strike": strike})
            self._product_price = process.pricing(self._product)["price"]
        elif self._opt_type == "call spread":
            short_call = VanillaOption(underlying, {"option_type":"call", "strike": strike2_strangle_spread})
            short_price = process.pricing(short_call)['price']
            long_call = VanillaOption(underlying, {"option_type":"call", "strike": strike})
            long_price = process.pricing(long_call)['price']

            self._product = Spread(self._opt_type,
                                   {"long leg":long_call, "long leg price":long_price, "short leg": short_call, "short leg price": short_price})
            self._product_price = self._product.price()
        elif self._opt_type == "put spread":
            short_put = VanillaOption(underlying, {"option_type":"put", "strike": strike})
            short_price = process.pricing(short_put)['price']
            long_put = VanillaOption(underlying, {"option_type":"put", "strike": strike2_strangle_spread})
            long_price = process.pricing(long_put)['price']

            self._product = Spread(self._opt_type,
                                   {"long leg":long_put, "long leg price":long_price, "short leg": short_put, "short leg price": short_price})
            self._product_price = self._product.price()
        elif self._opt_type == "butterfly spread":
            # Call Spread
            short_call = VanillaOption(underlying, {"option_type":"call", "strike": strike2_strangle_spread})
            short_price = process.pricing(short_call)['price']
            long_call = VanillaOption(underlying, {"option_type":"call", "strike": strike})
            long_price = process.pricing(long_call)['price']
            call_spread = Spread("call spread",
                                 {"long leg":long_call, "long leg price":long_price, "short leg": short_call, "short leg price": short_price})
            
            # Put Spread
            short_put = VanillaOption(underlying, {"option_type":"put", "strike": strike2_strangle_spread})
            short_price = process.pricing(short_put)['price']
            long_put = VanillaOption(underlying, {"option_type":"put", "strike": strike3_spread})
            long_price = process.pricing(long_put)['price']
            put_spread = Spread("put spread",
                                {"long leg":long_put, "long leg price":long_price, "short leg": short_put, "short leg price": short_price})
            
            self._product = ButterflySpread({"put spread":put_spread, "call spread":call_spread})
            self._product_price = self._product.price()
        else:
            if self._opt_type in ["straddle", "strip", "strap"]:
                call = VanillaOption(underlying,
                                     {"option_type": "call", "strike": strike})
                call_price = process.pricing(call)
                put = VanillaOption(underlying,
                                    {"option_type": "put", "strike": strike})
                put_price = process.pricing(put)
            else:
                call = VanillaOption(underlying,
                                     {"option_type": "call", "strike": strike2_strangle_spread})
                call_price = process.pricing(call)
                put = VanillaOption(underlying,
                                    {"option_type": "put", "strike": strike})
                put_price = process.pricing(put)

            self._product = OptionProducts(type = self._opt_type,
                                           long_short = self._long_short,
                                           inputs = {"call": call, "call price": call_price["price"],
                                                     "put": put, "put price": put_price["price"]})
            self._product_price = self._product.price()
        
    def payoff(self) -> list:
        """ Calculate and return the payoff of the product for a range of spots. """
        payoffs = []
        
        if self._opt_type in ["call", "put"]:
            for i in range(0, 200):
                payoff = self._product.payoff(spot = i)

                if self._long_short == "long":
                    payoffs.append(payoff)
                elif self._long_short == "short":
                    payoffs.append(-payoff)
        else:
            for i in range(0, 200):
                payoff = self._product.payoff(spot = i)
                payoffs.append(payoff)

        return payoffs

    def price(self) -> list:
        """ Calculate and return the price of the product for a range of spots. """
        profits =[]

        if self._opt_type in ["call", "put", "call spread", "put spread"]:
            for i in range(0, 200):
                payoff = self._product.payoff(spot = i)

                if self._long_short == "long":
                    profits.append(payoff - self._product_price)
                elif self._long_short == "short":
                    profits.append(- payoff + self._product_price)
        else:
            for i in range(0, 200):
                payoff = self._product.payoff(spot = i)
                profits.append(payoff - self._product_price)

        return profits
    
    def greeks(self) -> list:
        """ Calculate and return the greeks of the product for a range of spots. """
        greeks = []

        for i in range(1, 200):
            process = BrownianMotion({
                "nb_simulations":1000,
                "nb_steps":1000,
                "spot": i,
                "rates":self._rate,
                "volatility":self._vol,
                "maturity":self._maturity
            })
            if self._opt_type in ["call", "put"]:
                opt_greeks = OptionRisk(self._product, process)
            elif self._opt_type in ["call spread", "put spread"]:
                opt_greeks = SpreadRisk(self._product, process)
            elif self._opt_type == "butterfly spread":
                opt_greeks = ButterflySpreadRisk(self._product, process)
            else:
                opt_greeks = OptionProductsRisk(self._product, process)

            if self._graph_type == "delta":
                greeks.append(opt_greeks.delta())
            elif self._graph_type == "gamma":
                greeks.append(opt_greeks.gamma())
            elif self._graph_type == "vega":
                greeks.append(opt_greeks.vega())
            elif self._graph_type == "theta":
                greeks.append(opt_greeks.theta())
            elif self._graph_type == "rho":
                greeks.append(opt_greeks.rho())

        return greeks

    def plot(self) -> None:
        """ Graph the payoff, profit, or greeks of the product for a range of spots. """
        if self._graph_type == "payoff":
            y_series = self.payoff()
        elif self._graph_type == "profit":
            y_series = self.price()
        else:
            y_series = self.greeks()

        if self._graph_type in ["payoff", "profit"]:
            y_below_zero = [y if y <= 0 else None for y in y_series]
            y_above_zero = [y if y > 0 else None for y in y_series]

            plt.plot(range(0, 200), y_below_zero, color='red', label='Below 0')
            plt.plot(range(0, 200), y_above_zero, color='green', label='Above 0')
            plt.axhline(0, color='black', linewidth=0.5)
        else:
            plt.plot(range(1, 200), y_series, color='blue')
            plt.axhline(0, color='black', linewidth=0.5)

        plt.xlabel('Spot Price')
        plt.ylabel(self._graph_type.capitalize())
        plt.title(f'{self._long_short.title()} {self._opt_type.capitalize()} Option {self._graph_type.capitalize()}')
        plt.show()


class GraphsStructuredProducts:
    """ A class representing the graphic of a structured product.
    Argument:
        _prod_type (str): type of structured product.
        _graph_type (str): type of graphical representation.
        _rate (Rate): rate of the financial product.
        _vol (float): volatility of the financial product.
        _maturity (Maturity): maturity of the financial product.
        _product (ReverseConvertible or CertificatOutperformance): structured product to graph.
        _product_price (float): price of the structured product.
    """

    def __init__(self, graph_type: str, 
                 rate: Rate, maturity: Maturity, vol: float,
                 underlying: str, prod_type: str, strike: float, 
                 additionnal_coupon: float = None, coupon_rate: float = None, nb_coupon: float = None, nominal: float = None
                 ) -> None:
        """
        Initialize a GraphsStructuredProducts object.
        Args:
            graph_type (str): type of graphical representation.
            rate (Rate): rate of the financial product.
            maturity (Maturity): maturity of the financial product.
            vol (float): volatility of the financial product.
            underlying (str): underlying of the financial product.
            prod_type (str): type of structured product.
            strike (float): strike of the financial product.
            additionnal_coupon (float, optional): the additional coupon for the reverse convertible. Defaults to None.
            coupon_rate (float, optional): the coupon_rate for the reverse convertible. Defaults to None.
            nb_coupon (float, optional): the number of coupon for the reverse convertible. Defaults to None.
            nominal (float, optional): the nominal for the reverse convertible. Defaults to None.
        """

        # Check inputs
        self._prod_type = prod_type.lower()
        if self._prod_type not in ["reverse convertible", "certificat outperformance"]:
            raise Exception("Input error: Wrong option type, please enter reverse convertible or certificate outperformance.")

        self._graph_type = graph_type.lower()
        if self._graph_type not in ["payoff", "profit", "delta", "gamma", "vega", "theta", "rho"]:
            raise Exception("Input error: graph type must be payoff, profit, delta, gamma, vega, theta, rho.")
        
        # Process creation
        self._rate = rate
        self._vol = vol
        self._maturity = maturity
        process = BrownianMotion({
            "nb_simulations":1000,
            "nb_steps":1000,
            "spot":100,
            "rates":self._rate,
            "volatility":self._vol,
            "maturity":self._maturity
        })

        # Product creation
        if self._prod_type == "reverse convertible":
            put = VanillaOption(underlying, {"option_type":"put", "strike":strike})
            put_price = process.pricing(put)["price"]
            bond = FixedBond(coupon_rate=coupon_rate, maturity=self._maturity, nominal=nominal, nb_coupon=nb_coupon, rate=self._rate)

            self._product = ReverseConvertible({"put":put, "put price": put_price, 
                         "bond":bond, "bond price": bond.price(),
                         "coupon": additionnal_coupon})
            self._product_price = self._product.price()

        else:
            call = VanillaOption(underlying, {"option_type":"call", "strike":strike})
            call_price = process.pricing(call)["price"]
            call_zs = VanillaOption(underlying, {"option_type":"call", "strike":0})
            call_zs_price = process.pricing(call_zs)["price"]

            # Certificat outperformance
            self._product = CertificatOutperformance({"zero strike call": call_zs, "zero strike call price": call_zs_price,
                                                      "call":call, "call price":call_price})
            self._product_price = self._product.price()

    def payoff(self):
        """ Calculate and return the payoff of the product for a range of spots. """
        payoffs = []

        for i in range(0, 200):
            payoff = self._product.payoff(spot = i)
            payoffs.append(payoff)
        
        return payoffs

    def price(self):
        """ Calculate and return the profit of the product for a range of spots. """
        profits = []

        for i in range(0, 200):
            payoff = self._product.payoff(spot = i)
            profits.append(payoff - self._product_price)
        
        return profits

    def greeks(self):
        """ Calculate and return the greeks of the product for a range of spots. """
        greeks = []

        for i in range(1, 200):
            process = BrownianMotion({
                "nb_simulations":1000,
                "nb_steps":1000,
                "spot": i,
                "rates":self._rate,
                "volatility":self._vol,
                "maturity":self._maturity
            })

            if self._prod_type == "reverse convertible":
                opt_greeks = StructuredProductsRisk(self._prod_type, process, 
                                                convertible=self._product)
            else:
                opt_greeks = StructuredProductsRisk(self._prod_type, process,
                                                    certificat=self._product)
            
            if self._graph_type == "delta":
                greeks.append(opt_greeks.delta())
            elif self._graph_type == "gamma":
                greeks.append(opt_greeks.gamma())
            elif self._graph_type == "vega":
                greeks.append(opt_greeks.vega())
            elif self._graph_type == "theta":
                greeks.append(opt_greeks.theta())
            elif self._graph_type == "rho":
                greeks.append(opt_greeks.rho())

        return greeks

    def plot(self) -> None:
        """ Graph the payoff, profit or greeks of the structured product for a range of spots. """
        if self._graph_type == "payoff":
            y_series = self.payoff()
        elif self._graph_type == "profit":
            y_series = self.price()
        else: y_series = self.greeks()

        if self._graph_type in ["payoff", "profit"]:
            y_below_zero = [y if y <= 0 else None for y in y_series]
            y_above_zero = [y if y > 0 else None for y in y_series]

            plt.plot(range(0, 200), y_below_zero, color='red', label='Below 0')
            plt.plot(range(0, 200), y_above_zero, color='green', label='Above 0')
            plt.axhline(0, color='black', linewidth=0.5)
        else:
            plt.plot(range(1, 200), y_series, color='blue')
            plt.axhline(0, color='black', linewidth=0.5)

        plt.xlabel('Spot Price')
        plt.ylabel(self._graph_type.capitalize())
        plt.title(f'{self._prod_type.title()} Option {self._graph_type.capitalize()}')
        plt.show()
