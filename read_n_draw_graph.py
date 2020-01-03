import networkx as nx
import matplotlib.pyplot as plt

G=nx.DiGraph()


# nx.write_gml(G, "./g")

# nx.draw(G)
# plt.show()
# nx.draw_networkx(G)


G = nx.read_gml('./test')
# nx.draw_networkx(G)
nx.draw_networkx(G)
# plt.show()
plt.savefig("./graph.png")
