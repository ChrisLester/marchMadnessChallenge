import string
import time
import ROOT
from ROOT import TMVA
from optparse import OptionParser
import commands

parser = OptionParser()
(options,args) = parser.parse_args()


files = [(ROOT.TFile.Open('regression_train_tourney.root'), 'tourney_results')]

def get_tree(tfile,  tree_name):
    tree = tfile.Get(tree_name)                     
    weight = 1
    return (tree, 1)

trees = [ get_tree(tfile, tname) for tfile, tname in files ]
    

class TMVASession(object):
    def __init__(self, job_name, trees, vars,  spectators = None, cuts=''):
        self.job_name = job_name
        self.trees = trees
        self.vars = vars
        self.spectators = spectators 
        self.cuts = cuts

    def build_factory(self):
        self.out_file = ROOT.TFile('tmva_output.%s.root' % self.job_name, 'RECREATE')
        self.factory = TMVA.Factory(self.job_name, self.out_file, 'V:!Silent:!Color:DrawProgressBar')

        for tree, weight in self.trees:
            self.factory.AddRegressionTree(tree, weight)
                
        for var, type in self.vars:
            self.factory.AddVariable(var, type)

        for spec in self.spectators:
            self.factory.AddSpectator(spec)
	    
	self.factory.AddTarget('game_outcome')   

    def go(self):
        # see p. 20 of the TMVA User Manual for more options
        self.factory.PrepareTrainingAndTestTree(ROOT.TCut(self.cuts), 'NormMode=EqualNumEvents:SplitMode=Random')
        # see p. 59 of the TMVA User Manual for more options
        options = '!H:!V:NTrees=850:MaxDepth=10:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=RegressionVariance:nCuts=21'
        self.factory.BookMethod(TMVA.Types.kBDT, 'BDT', options)
        
        self.factory.TrainAllMethods()
        self.factory.TestAllMethods()
        self.factory.EvaluateAllMethods()

    def close(self):
        self.out_file.Close()

def tprint(s, log=None):
    line = '[%s] %s' % (time.strftime('%Y-%m-%d:%H:%M:%S'), s)
    print line
    if log:
        log.write(line + '\n')
        log.flush()

season = 'A'
# vars
cut = ROOT.TCut('season_int!=0') 
cut_str = cut.GetTitle()
job_name = 'regressionMVA'
tprint('TMVASession %s: %s' % (season, job_name))
s = TMVASession(
        job_name = job_name,
        trees = trees,
        vars = [
                ('seed1','I'),
                ('seed2','I'),
                ('avg_scorediff1','F'),
                ('avg_scorediff2','F'),
                ('winfrac1', 'F'),
                ('winfrac2', 'F'),
                ],
       spectators = ['season'],
       cuts = cut_str )
s.build_factory()
s.go()
s.close()
            
#-----------------------------------------------------------------------------

# EOF
