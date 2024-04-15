from Execution.graphs import GraphsOptions, GraphsStructuredProducts
from Products.rate import Rate
from Products.maturity import Maturity


# Launch graph
# graph = GraphsOptions(graph_type = "delta",
#                rate=Rate(0.03, rate_type="continuous"), maturity=Maturity(0.5), vol=0.2,
#                underlying = "no dividend share", opt_type = "butterfly spread", long_short = "long", strike = 95, strike2_strangle_spread=110, strike3_spread=125)
# graph.plot()

graph = GraphsStructuredProducts(graph_type="profit",
                                 rate=Rate(0.03, rate_type="continuous"), maturity=Maturity(0.5), vol=0.2,
                                 underlying = "no dividend share", prod_type="certificat outperformance", strike=102,
                                 coupon_rate=0.02, nb_coupon=12,nominal=100)
graph.plot()