# =============================================================================
# Main Driver for Ising Model Applied to Networks
#
# Author:               Max Graves
# Last Revised:         2-APR-2013
# =============================================================================

import networkx as nx
import pylab as pl
import sys, random, argparse, os

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
    parser.add_argument('--temp', '-T', type=float, default = 5.0,
            help='enter temperature in kelvin')
    parser.add_argument('--field', '-H', type=float, default=0.0,
            help='enter magnetic field strength')
    parser.add_argument('--exchange', '-J', type=float, default=1,
            help='enter the value of the exchange constant')
    parser.add_argument('--sweeps', '-s', type=int, default = 2000,
            help='enter the number of MC sweeps')
    return parser.parse_args()

# =============================================================================
def swapSpin(spinUp, spinDown, spin, totSpin):
    """
    Removes a node index from one list and puts it in the other.
    """
    if spin in spinDown:
        spinDown.remove(spin)
        spinUp.append(spin)
        totSpin += 2
    else:
        spinUp.remove(spin)
        spinDown.append(spin)
        totSpin -= 2
    return spinUp, spinDown, totSpin

# =============================================================================
def EnergyChange(spinUp, G, J, R):
    """
    calculates the energy change of flipping a spin.
    """
    if R in spinUp:
        tempSpin = 1.0
    else:
        tempSpin = -1.0
    spinSum = 0.0
    for i in G[R]:
        spinSum += tempSpin*G[R][i]

    delE =  2.0 * J * spinSum
    return delE

# =============================================================================
def updatePlot(G, position, spinUp, spinDown, upColor, downColor, ax):
    """
    Updates plot of network for viewing MC moves.
    """
    pl.cla()
    position = nx.circular_layout(G)
    nx.draw_networkx_nodes(G,position, nodelist=spinUp,
        node_color=upColor)
    nx.draw_networkx_nodes(G,position, nodelist=spinDown,
        node_color=downColor)
    nx.draw_networkx_edges(G,position)
    nx.draw_networkx_labels(G,position)
    ax.text(-0.1, 0.98, 'Spin Up', style='italic',
            bbox={'facecolor':upColor, 'alpha':0.9, 'pad':10})
    ax.text(-0.1, 1.1, 'Spin Down', style='italic',color='White',
            bbox={'facecolor':downColor, 'alpha':0.9, 'pad':10})

    pl.draw()

# =============================================================================
def main():

    # assign variables, define constants
    args = parseCMD()
    T,H,N = float(args.temp), float(args.field), int(args.nodes)
    J, s = float(args.exchange), int(args.sweeps)
    k_B = 1     # = 1.3806503 * pow(10,-23)
    upColor = 'Fuchsia'
    downColor = 'Black'

    # http://networkx.github.com/documentation/latest/tutorial/
    #   tutorial.html#adding-attributes-to-graphs-nodes-and-edges
    #G = nx.complete_graph(N)
    #G = nx.karate_club_graph()
    z=[3 for i in range(N)]
    G=nx.expected_degree_graph(z)

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
    
    # compute initial quantities
    totSpin = len(spinUp) - len(spinDown)
    spinSum = 0.0
    for i in range(len(G)):
        if i in spinUp:
            tempSpin = 1.0
        else:
            tempSpin = -1.0
        for j in G[i]:
            spinSum += tempSpin*G[i][j] 
    E = - 0.5 * J * spinSum     # divide by two because of double counting
    M = 1.0*totSpin/(1.0*N)
    
    # define arrays for mcSteps, Energies, Magnetism
    mcSteps, Es, Ms = pl.arange(s), pl.array([E]), pl.array([M])
    E2 = pl.array([E*E]) 

    # keep track of acceptance
    a = 0       # accepted moves
    r = 0       # rejected moves
    if args.showHist:
        pl.ion()
        fig = pl.figure(1)
        ax = fig.add_subplot(111)
        position = nx.circular_layout(G)

    for step in mcSteps:
        # randomly choose a node to try to flip the spin
        R = random.randint(0,len(G)-1)
        
        # compute change in energy from flipping that spin
        delE = EnergyChange(spinUp, G, J, R)

        # calculate Boltzmann factor
        Boltz = pl.exp(-1.0*delE/(k_B*T))

        if (delE <= 0):
            reject = False
            E += delE
            spinUp, spinDown, totSpin = swapSpin(spinUp,
                    spinDown, R, totSpin) 
        else:
            n = random.random()
            if (n <= Boltz):
                E += delE
                reject = False
                spinUp, spinDown, totSpin = swapSpin(spinUp,
                        spinDown, R, totSpin) 
            else:
                reject = True

        if reject==True:
            r += 1
        else:
            a += 1
        
        # calculate magnetism (not absolute value)
        M = 1.0*totSpin/(1.0*N)

        # store observables in array
        Es = pl.append(Es, E)
        Ms = pl.append(Ms, M)
        E2 = pl.append(E2, E*E)

        if args.showHist:
            updatePlot(G, position, spinUp, spinDown, upColor, downColor, ax)       

    if args.showHist:
        pl.close()
        pl.ioff()

    print 'acceptance ratio: ', 1.0*a/(r+a)

    if os.path.exists('./data/'):
        os.chdir('./data/')
    else:
        os.mkdir('./data/')
        os.chdir('./data/')

    filename = 'ising2D_L%s_s%s_Temp%s.dat'%(int(N), s, T)
    fid = open(filename, 'w')
    fid.write('# temp:  %s\n'%T)
    fid.write('# nodes:  %s\n'%N)
    fid.write('# field:  %s\n'%H)
    fid.write('# %15s\t%15s\t%15s\t%15s\n'%('mcSteps','Energies',
        'Magnetism','Energy^2'))
    zipped = zip(mcSteps, Es, Ms, E2)
    pl.savetxt(fid, zipped, fmt='%5.9f\t%5.9f\t%5.9f\t%5.9f')
    fid.close()
    print 'Data has been saved to: ',filename
    
# =============================================================================
if __name__=='__main__':
    main()
