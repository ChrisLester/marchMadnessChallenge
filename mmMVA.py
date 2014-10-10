import string
import time
import ROOT
from ROOT import TMVA
from optparse import OptionParser
import commands

parser = OptionParser()
(options,args) = parser.parse_args()


bkg_files = [(ROOT.TFile('mm_train_tourney.root'), 'tourney_results_l')]

sig_files = [(ROOT.TFile.Open('mm_train_tourney.root'), 'tourney_results_w')]

def get_tree(tfile,  tree_name):
    tree = tfile.Get(tree_name)                     
    weight = 1
    return (tree, 1)

sig_trees = [ get_tree(tfile, tname) for tfile, tname in sig_files ]

bkg_trees = [ get_tree(tfile, tname) for tfile, tname in bkg_files ]
    

class TMVASession(object):
    def __init__(self, job_name, sig_trees, bkg_trees, vars,  spectators = None, cuts=''):
        self.job_name = job_name
        self.sig_trees = sig_trees
        self.bkg_trees = bkg_trees
        self.vars = vars
        self.spectators = spectators 
        self.cuts = cuts

    def build_factory(self):
        self.out_file = ROOT.TFile('tmva_output.%s.root' % self.job_name, 'RECREATE')
        self.factory = TMVA.Factory(self.job_name, self.out_file, 'V:!Silent:!Color:DrawProgressBar')

        for tree, weight in self.sig_trees:
            self.factory.AddSignalTree(tree, weight)
        
        for tree, weight in self.bkg_trees:
            self.factory.AddBackgroundTree(tree, weight)
        
        for var, type in self.vars:
            self.factory.AddVariable(var, type)

        for spec in self.spectators:
            self.factory.AddSpectator(spec)

    def go(self):
        # see p. 20 of the TMVA User Manual for more options
        self.factory.PrepareTrainingAndTestTree(ROOT.TCut(self.cuts), 'NormMode=EqualNumEvents:SplitMode=Random')
        # see p. 59 of the TMVA User Manual for more options
        options = '!H:!V:NTrees=850:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=21'
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
my_seed       = 'm_seed'
op_seed       = 'o_seed'   
my_winfrac    = 'm_winfrac'
op_winfrac    = 'o_winfrac'
my_ascorediff = 'm_avg_scorediff'
op_ascorediff = 'o_avg_scorediff'
cut = ROOT.TCut('') 
cut_str = cut.GetTitle()
job_name = 'mmMVA'
tprint('TMVASession %s: %s' % (season, job_name))
s = TMVASession(
        job_name = job_name,
        sig_trees = sig_trees,
        bkg_trees = bkg_trees,
        vars = [
                (my_seed,'D'),
                (op_seed,'D'),
                (my_ascorediff, 'F'),
                (op_ascorediff,'F'),
                (my_winfrac, 'F'),
                (op_winfrac, 'F'),
                ],
       spectators = ['season'],
       cuts = cut_str )
s.build_factory()
s.go()
s.close()
            
#-----------------------------------------------------------------------------

# EOF
