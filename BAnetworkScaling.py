# =============================================================================
# Script for determining and plotting how the critical temperature of
# BA networks scales with number of nodes.
#
# Author:           Max Graves
# Last Revision:    4-MAY-2013
# =============================================================================

import subprocess, os, sys, argparse, glob
import pylab as pl

# =============================================================================
def parseCMD():
    desc= ('Ising 2D script for plotting phase transition.  Takes as its \
            argument the directory holding all of the data files that you ,\
            want to plot.')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('direcN', help='name of data directory of interest')

    return parser.parse_args()

# =============================================================================
def main():

    args = parseCMD()
    os.chdir(args.direcN)

    try:
        critTemp, numNodes = pl.loadtxt('BAscalingData.txt', unpack=True)
        print 'Found a reduced file!'

    except:
        print 'Didnt find reduced file.  Creating one'
    
        # holds all files created by phaseTransSubmit.py
        direcs = glob.glob("*T*")

        numNodes = pl.array([])
        critTemp = pl.array([])
        for d in direcs:
            os.chdir(d)
            redFile = glob.glob("*reduce*")
            T,E,M,Cv = pl.loadtxt(redFile[0], unpack=True)
            estFile = open(redFile[0],'r')
            estLines = estFile.readlines();
            numNodes = pl.append(numNodes, float(estLines[0].split()[-1]))
            critTemp = pl.append(critTemp, T[Cv.argmax()])
            os.chdir('..')

        # write temps, Es, Ms to file
        filename = 'BAscalingData.txt'
        fid = open(filename, 'w')
        fid.write('# %15s\t%15s\n'%('temps','Nodes'))
        zipped = zip(critTemp, numNodes)
        pl.savetxt(fid, zipped, fmt='%5.9f\t%5.9f')
        fid.close()
        print 'Data has been saved to: ',filename

    # fit semilogx data
    (ar1,br1) = pl.polyfit(pl.log10(numNodes),critTemp,1)
    linY1 = pl.polyval([ar1,br1],pl.log10(numNodes))

    # plot energy vs. temp
    fig1 = pl.figure(1)
    p1 = fig1.add_subplot(111)
    pl.semilogx(numNodes, critTemp, marker='o', linewidth=0,
            markerfacecolor='None', markeredgecolor='Indigo')
    pl.semilogx(numNodes,linY1, color='Blue')
    pl.grid(True)
    pl.ylabel(r'$T_c\ [K]$', size=20)
    pl.xlabel('Nodes', size=20)
    pl.ylim(0)
    pl.xlim(0)
   
    pl.show()
    
# =============================================================================
if __name__=='__main__':
    main()
