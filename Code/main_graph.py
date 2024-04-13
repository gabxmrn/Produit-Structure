from graphs import Graphs
from rate import Rate
from maturity import Maturity


# Launch graph
graph = Graphs(graph_type = "vega",
               rate=Rate(0.03, rate_type="continuous"), maturity=Maturity(0.5), vol=0.02,
               underlying = "no dividend share", opt_type = "straddle", long_short = "long", strike = 102)
graph.plot()
