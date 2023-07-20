from rdflib import Graph

# Create a Graph
g = Graph()

# Parse in an RDF file hosted on the Internet
g.parse("https://fritz.freiburg.de/duva2dcat/dcat/catalog")

# Loop through each triple in the graph (subj, pred, obj)
for subj, pred, obj in g:
    # Check if there is at least one triple in the Graph
    print(subj)
    if (subj, pred, obj) not in g:
        raise Exception("It better be!")