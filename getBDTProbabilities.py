#/bash/bin/python
import array
import os
from ROOT import *
from optparse import OptionParser

historyFileName = 'rootFiles/mm_input_modified.root'
tourneyFileName = 'rootFiles/mm_input.root'

#-----------------------------------------------------------------------------------------------------        
def ParseOptions() :

    parser = OptionParser(usage='python evaluatePrediction.py --file filename')

    parser.add_option('--mvaWeight', dest='mvaWeight', default=None) 
    parser.add_option('--mvaRoot'  , dest='mvaRoot', default=None)
    parser.add_option('--season'   , dest='season', default=None) 
    parser.add_option('--out', dest='outName', default="probability.csv") 
    
    return parser.parse_args()


#-----------------------------------------------------------------------------------------------------        
def evaluateProbability(sigHist,bkgHist,mvaOutput):
    sigLL = sigHist.GetBinContent(sigHist.FindBin(mvaOutput))
    bkgLL = bkgHist.GetBinContent(bkgHist.FindBin(mvaOutput))

    # get probability of being a winner 
    prob = 0.5  
    if not sigLL + bkgLL == 0:
        prob = sigLL/(sigLL+bkgLL) 

    # protect against 0,1 probablitites
    if prob > 0.99: prob = 0.99
    if prob < 0.01: prob = 0.01

    return prob 

#-----------------------------------------------------------------------------------------------------        
def generateCSV(tourneyTree, historyTree, options):
    # loop over seed tree, twice, find all possible pairings, no duplicate pairing

    # get reference hists
    referenceFile = TFile(options[0].mvaRoot) 
    sigRef = referenceFile.Get("Method_BDT/BDT/MVA_BDT_S")
    bkgRef = referenceFile.Get("Method_BDT/BDT/MVA_BDT_B")
    
    # get MVA Reader - from http://aholzner.wordpress.com/2011/08/27/a-tmva-example-in-pyroot/
    reader = TMVA.Reader()
    var1 = array.array('f',[0]) ; reader.AddVariable("m_seed",var1)
    var2 = array.array('f',[0]) ; reader.AddVariable("o_seed",var2)
    var3 = array.array('f',[0]) ; reader.AddVariable("m_avg_scorediff",var3)
    var4 = array.array('f',[0]) ; reader.AddVariable("o_avg_scorediff",var4)
    var5 = array.array('f',[0]) ; reader.AddVariable("m_winfrac",var5)
    var6 = array.array('f',[0]) ; reader.AddVariable("o_winfrac",var6)

    reader.BookMVA("BDT",options[0].mvaWeight)

    # open csv 

    outFile = open(options[0].outName, 'a') 
    iCount = 0
    nSeeds = tourneyTree.GetEntries()
    for i in tourneyTree:

        iCount += 1
        jCount = 0
        if not iCount%50: print 'Processing tourney game %d/%d'%(iCount,nSeeds)
       
        if not options[0].season.count(i.season[0]): continue
        
        team1 = i.team 
        seed1 = int(''.join(c for c in i.seed if c in '1234567890')) 
        season1 = i.season[0] 

        for j in tourneyTree:
            jCount += 1
            if not options[0].season.count(j.season[0]): continue
            if jCount <= iCount: continue

            season2 = j.season

            if not i.season == j.season: continue #only teams from same season have possibility of playing

            team2 = j.team
            seed2 = int(''.join(c for c in j.seed if c in '1234567890')) 
           
            # get other vars from history tree

            team1avg = 0
            team2avg = 0
            team1win = 0
            team2win = 0

            foundTeam1 = False
            foundTeam2 = False 
            for entry in historyTree:
                if not entry.season == j.season: continue

                if entry.team == team1:
                    foundTeam1 = True
                    team1avg   = entry.avg_scorediff
                    team1win   = entry.winfrac

                if entry.team == team2:
                    foundTeam2 = True 
                    team2win   = entry.winfrac
                    team2avg   = entry.avg_scorediff
                if foundTeam1 and foundTeam2: break 

            var1[0] = seed1
            var2[0] = seed2
            var3[0] = team1avg
            var4[0] = team2avg
            var5[0] = team1win
            var6[0] = team2win
            
            output = reader.EvaluateMVA("BDT") 
            
            prob = evaluateProbability(sigRef, bkgRef, output)

            outFile.write(','.join(['_'.join([j.season[0], str(team1), str(team2)]),str(prob)])+'\n')

    outFile.close() 
#-----------------------------------------------------------------------------------------------------        
def main(options):

    # get two trees

    historyFile = TFile(historyFileName)
    historyTree = historyFile.Get("teams")
    
    tourneyFile = TFile(tourneyFileName) 
    tourneyTree = tourneyFile.Get("tourney_seeds" ) 

    # generate CSV
    generateCSV(tourneyTree, historyTree, options)

if __name__ == '__main__' :
    main(ParseOptions())
