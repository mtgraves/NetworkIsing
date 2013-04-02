# =============================================================================
# Main Driver for Ising Model Applied to Networks
#
# Author:               Max Graves
# Last Revised:         2-APR-2013
# =============================================================================

import networkx as nx
import pylab as pl
import sys, random, argparse

# =============================================================================
def parseCMD():
    """
    Parse the command line.
    """
    parser = argparse.ArgumentParser(description = 'Ising Model for Networks')
    parser.add_argument("-S", "--showHist", action="store_true",
            dest="showHist",
            default=False,
            help="show the simulation in histogram form (SLOW!)")
    parser.add_argument('--nodes', '-N', type=int, default=10,
            help='number of nodes in network')
    parser.add_argument('--temp', '-T', type=float,
            help='enter temperature in kelvin')
    parser.add_argument('--field', '-H', type=float, default=0.0,
            help='enter magnetic field strength')
    parser.add_argument('--length', '-L', type=float,
            help='enter the length of the 2-d lattice')
    parser.add_argument('--exchange', '-J', type=float, default=1,
            help='enter the value of the exchange constant')
    parser.add_argument('--sweeps', '-s', type=int,
            help='enter the number of MC sweeps')
    return parser.parse_args()

# =============================================================================
def main():

    args = parseCMD()

    # Define graph.  For complete list of predefined graphs, see:
    # http://networkx.github.com/documentation/latest/tutorial/
    #   tutorial.html#adding-attributes-to-graphs-nodes-and-edges
    G = nx.complete_graph(args.nodes)

    # keep track of spins of nodes
    spinUp, spinDown = [], []

    # assign each node a spin (\pm 1)
    for node in G:
        r = 2.0*random.randint(0,1)-1.0
        if r == 1.0:
            spinUp.append(node)
        else:
            spinDown.append(node)
        for neighbor in range(len(G)):
            if neighbor in G[node]:
                G[neighbor][node] = r
            else:
                pass

    # plot the network with colored nodes indicating spin 
    fig1 = pl.figure(1)
    p1 = fig1.add_subplot(111)
    position = nx.circular_layout(G)
    nx.draw_networkx_nodes(G,position, nodelist=spinUp, node_color='green')
    nx.draw_networkx_nodes(G,position, nodelist=spinDown, node_color='purple')
    nx.draw_networkx_edges(G,position)
    nx.draw_networkx_labels(G,position)
     
    pl.show()

# =============================================================================
if __name__=='__main__':
    main()
