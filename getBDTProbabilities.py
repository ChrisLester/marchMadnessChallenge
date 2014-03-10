#/bash/bin/python
import array
import os
from ROOT import *
from optparse import OptionParser

historyFileName = 'mm_input_modified.root'
tourneyFileName = 'mm_input.root'

#-----------------------------------------------------------------------------------------------------        
def ParseOptions() :

    parser = OptionParser(usage='python evaluatePrediction.py --file filename')
    
    parser.add_option('--mvaWeight', dest='mvaWeight', default=None) 
    parser.add_option('--mvaRoot'  , dest='mvaRoot', default=None)
    parser.add_option('--season'   , dest='season', default=None) 
    parser.add_option('-out', dest='outFile', default="probability.csv") 
    
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
def main(options):

    # get reference hists
    referenceFile = TFile(options[0].mvaRoot) 
    bkgRef = referenceFile.Get("Method_BDT/BDT/MVA_BDT_S")
    sigRef = referenceFile.Get("Method_BDT/BDT/MVA_BDT_B")
    
    # get MVA Reader - from http://aholzner.wordpress.com/2011/08/27/a-tmva-example-in-pyroot/
    reader = ROOT.TMVA.Reader()
    bdtVars = []
    bdtVars.append(array.array('d',[0]) ; reader.AddVariable("m_seed",var1))
    bdtVars.append(array.array('d',[0]) ; reader.AddVariable("s_seed",var2))
    bdtVars.append(array.array('f',[0]) ; reader.AddVariable("m_avg_scorediff",var3))
    bdtVars.append(array.array('f',[0]) ; reader.AddVariable("o_avg_scorediff",var4))
    bdtVars.append(array.array('f',[0]) ; reader.AddVariable("m_winfrac",var5))
    bdtVars.append(array.array('f',[0]) ; reader.AddVariable("o_winfrac",var6))

    reader.BookMVA("BDT",options[0].mvaWeight)

    # get two trees

    historyFile = TFile(historyFileName)
    historyTree = historyFile.Get("teams")
    
    tourneyFile = TFile(tourneyFileName) 
    tourneyTree = TFile("tourney_seeds" ) 



if __name__ == '__main__' :
    main(ParseOptions())
