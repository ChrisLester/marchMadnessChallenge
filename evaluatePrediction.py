#/bash/bin/python

#import sys
#if not sys.argv.count('-i') and not sys.argv.count('-b'):
#    sys.argv.append('-b 1')

import os
import scipy as sp
from ROOT import *
from optparse import OptionParser

tourney_file = 'mm_input.root'

#-----------------------------------------------------------------------------------------------------        
def ParseOptions() :

    parser = OptionParser(usage='python evaluatePrediction.py --file filename')
    
    parser.add_option('-f', dest='input_file', default=None, 
            help='Input file (one file only)' )
    
    return parser.parse_args()


def main(options):

  input_file = options[0].input_file
  
  if not os.path.isfile(input_file):
    print "Input file not found"
    return
  
  if not os.path.isfile(tourney_file):
    print "Tourney file not found:", tourney_file
    return
  
  result_file = TFile(tourney_file,'READ')
  result_tree = result_file.Get('tourney_results')
  if not result_tree:
    print "tourney_results tree not found"
    return
    
  h_outcome = TH1F('h_outcome','',2,-0.5,1.5)  
  
  outcomes    = []
  predictions = []  
    
  with open(input_file,'r') as f:     
    next(f)
    for line in f:
      tokens = line.split(',')
      if not len(tokens) == 2: continue
      
      game_id    = tokens[0]
      prediction = float(tokens[1])

      season = game_id[0]
      team1  = game_id[2:5]	 
      team2  = game_id[6:9]	 
      #print game_id, season, team1, team2

      sel_season = '(season == \"'+season+'\")' 
      sel_teams  = '(((wteam=='+team1+')&&(lteam=='+team2+')) || ((wteam=='+team2+')&&(lteam=='+team1+')))'
      cut_playin = '(daynum>=136)'
      
      result_tree.Draw('wteam=='+team1+'>>h_outcome',sel_season+'&&'+sel_teams+'&&'+cut_playin, 'goff')
      
      n_games = h_outcome.Integral() 
      if n_games == 0: continue      
      if n_games > 1:
        print 'ERROR: Found',n_games,'matching game_id',game_id	 
        continue
      game_outcome = h_outcome[2]	
      
      outcomes.append(game_outcome)
      predictions.append(prediction)
      
  score = llfun(outcomes, predictions)

  print 'Found',len(outcomes),'games'
  print '---------------------'
  print 'Score = ', score
  print '---------------------'

  return
  

def llfun(act, pred):
  epsilon = 1e-15
  pred = sp.maximum(epsilon, pred)
  pred = sp.minimum(1-epsilon, pred)
  ll = sum(act*sp.log(pred) + sp.subtract(1,act)*sp.log(sp.subtract(1,pred)))
  ll = ll * -1.0/len(act)
  return ll


if __name__ == '__main__' :
    main(ParseOptions())
