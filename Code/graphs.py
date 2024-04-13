from products import VanillaOption, OptionProducts
from rate import Rate
from maturity import Maturity
from brownianMotion import BrownianMotion
from riskAnalysis import OptionRisk, OptionProductsRisk

import matplotlib.pyplot as plt


class Graphs:

    def __init__(self, graph_type: str, 
                 rate: Rate, maturity: Maturity, vol: float,
                 underlying: str, opt_type: str, long_short: str, strike: float, strike2_strangle: float = None) -> None:

        # Check inputs
        self._opt_type = opt_type.lower()
        if self._opt_type not in ["call", "put", "straddle", "strangle", "strip", "strap"]:
            raise Exception("Input error: Wrong option type, please enter call, put, straddle, strangle, strip or strap.")

        self._long_short = long_short.lower()
        if self._long_short not in ["long", "short"]:
            raise Exception("Input error: Position must be long or short.")

        self._graph_type = graph_type.lower()
        if self._graph_type not in ["payoff", "profit", "delta", "gamma", "vega", "theta", "rho"]:
            raise Exception("Input error: graph type must be payoff or profit.")

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
            self._opt_process = process.pricing(self._product)
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
                                     {"option_type": "call", "strike": strike2_strangle})
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

        if self._opt_type in ["call", "put"]:
            for i in range(0, 200):
                payoff = self._product.payoff(spot = i)

                if self._long_short == "long":
                    profits.append(payoff - self._opt_process["price"])
                elif self._long_short == "short":
                    profits.append(- payoff + self._opt_process["price"])
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
        plt.title(f'{self._long_short.capitalize()} {self._opt_type.capitalize()} Option {self._graph_type.capitalize()}')
        plt.show()




