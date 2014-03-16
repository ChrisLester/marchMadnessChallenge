import string
import time
import ROOT
from ROOT import TMVA
from optparse import OptionParser
import commands

parser = OptionParser()
(options,args) = parser.parse_args()


files = [(ROOT.TFile.Open('regression_train_tourney.root'), 'tourney_results')]

seasons = map(chr, range(65, 83)) #hardcoded list of seasons from A to R

def get_tree(tfile,  tree_name):
    tree = tfile.Get(tree_name)                     
    weight = 1
    return (tree, 1)

trees = [ get_tree(tfile, tname) for tfile, tname in files ]
    

class TMVASession(object):
    def __init__(self, job_name, trees, vars, targets, spectators = None, cuts=''):
        self.job_name = job_name
        self.trees = trees
        self.vars = vars
	self.targets = targets
        self.spectators = spectators 
        self.cuts = cuts

    def build_factory(self):
        self.out_file = ROOT.TFile('tmva_output.%s.root' % self.job_name, 'RECREATE')
        self.factory = TMVA.Factory(self.job_name, self.out_file, 'V:!Silent:!Color')

        for tree, weight in self.trees:
            self.factory.AddRegressionTree(tree, weight)
                
        for var, type in self.vars:
            self.factory.AddVariable(var, type)

        for spec in self.spectators:
            self.factory.AddSpectator(spec)
	    
        for target in self.targets:
 	    self.factory.AddTarget(target)   

    def go(self):
        # see p. 20 of the TMVA User Manual for more options
	options = 'SplitMode=Random'
        options += ':nTrain_Regression=1156'
	self.factory.PrepareTrainingAndTestTree(ROOT.TCut(self.cuts), options)

        # see p. 59 of the TMVA User Manual for more options
        options = '!H:!V'
	options += ':NTrees=850'
	options += ':MaxDepth=5'
	options += ':BoostType=AdaBoost:AdaBoostBeta=0.5'
	#options += ':SeparationType=CrossEntropy'
	options += ':nCuts=30'
	#options += ":MinNodeSize=5%"
	options += ":nEventsMin=50"
        self.factory.BookMethod(TMVA.Types.kBDT, 'BDT', options)
        #for i in range(2,21):
	#  self.factory.BookMethod(TMVA.Types.kBDT, 'BDT_MaxDepth'+str(i), options+':MaxDepth='+str(i))

	# Linear discriminant (same as Fisher, but also performing regression)
	#self.factory.BookMethod( TMVA.Types.kLD, "LD", "!H:!V:VarTransform=None" );        

        self.factory.TrainAllMethods()
        #self.factory.TestAllMethods()
        #self.factory.EvaluateAllMethods()

    def close(self):
        self.out_file.Close()

def tprint(s, log=None):
    line = '[%s] %s' % (time.strftime('%Y-%m-%d:%H:%M:%S'), s)
    print line
    if log:
        log.write(line + '\n')
        log.flush()


for i,season in enumerate(seasons):
#for i,season in enumerate(['test']):
  #season = 'A'
  # vars
  cut = ROOT.TCut('season_int!='+str(i)) 
  #cut = ROOT.TCut('') 
  cut_str = cut.GetTitle()
  job_name = 'regressionMVA_'+season
  tprint('TMVASession %s: %s' % (season, job_name))
  s = TMVASession(
          job_name = job_name,
          trees = trees,
          vars = [
                  ('seed1','I'),
                  ('seed2','I'),
                  ('winfrac1', 'F'),
                  ('winfrac2', 'F'),
                  ('avg_scorediff1','F'),
                  ('avg_scorediff2','F'),
                  ('rms_scorediff1','F'),
                  ('rms_scorediff2','F'),
                  ('avg_opp_score_for1','F'),
                  ('avg_opp_score_for2','F'),
                  ('avg_opp_score_against1','F'),
                  ('avg_opp_score_against2','F'),
                  ],
	  targets = ['game_outcome'], 	
          spectators = ['season'],
          cuts = cut_str )
  s.build_factory()
  s.go()
  s.close()
            
#-----------------------------------------------------------------------------

# EOF
