#/bash/bin/python

#import sys
#if not sys.argv.count('-i') and not sys.argv.count('-b'):
#    sys.argv.append('-b 1')

import os
import scipy as sp
from ROOT import *
from optparse import OptionParser

tourney_file = 'toy_tourneys.csv'

alpha = 0.033

#-----------------------------------------------------------------------------------------------------        
def ParseOptions() :

    parser = OptionParser(usage='python evaluatePrediction.py')
    
    #parser.add_option('-f', dest='input_file', default=None, 
    #        help='Input file (one file only)' )
    
    return parser.parse_args()


def main(options):

  if not os.path.isfile(tourney_file):
    print "Tourney file not found:", tourney_file
    return
    
  seasons = []
  outcomes    = []
  predictions = []    
   
  with open(tourney_file,'r') as f:     
    next(f)
    for line in f:
      tokens = line.split(',')
      if not len(tokens) == 2: continue
      
      game_id      = tokens[0]
      game_outcome = int(tokens[1])

      tokens = game_id.split('_')
      season = int(tokens[0])
      team1  = int(tokens[1])	 
      team2  = int(tokens[2]) 
      #print game_id, season, team1, team2
      
      prediction = SimpleSeedPrediction(Seed(team1),Seed(team2))
                 
      if season in seasons:
        season_index = seasons.index(season)
	outcomes[season_index].append(game_outcome)
	predictions[season_index].append(prediction)
      else:
        seasons.append(season)
        outcomes.append( [game_outcome] )
        predictions.append( [prediction] )
  
  scores  = [] 
  print 'Season\tScore'
  print '---------------------'
  for i in range(len(seasons)):          
    scores.append( llfun(outcomes[i], predictions[i]) )
    print seasons[i],'\t',scores[i]
      
  print '---------------------'
  print 'Min Score     = ', sp.amin(scores)
  print 'Average Score = ', sp.average(scores)
  print 'Max Score     = ', sp.amax(scores)
  print 'Variance      = ', sp.var(scores)
  print 'Std. Dev.     = ', sp.std(scores)
  print '---------------------'

  return
  
def SimpleSeedPrediction(seed1, seed2):
  return 0.5+alpha*(seed2-seed1)
 
def Seed(team):
  return team%100 

def llfun(act, pred):
  epsilon = 1e-15
  pred = sp.maximum(epsilon, pred)
  pred = sp.minimum(1-epsilon, pred)
  ll = sum(act*sp.log(pred) + sp.subtract(1,act)*sp.log(sp.subtract(1,pred)))
  ll = ll * -1.0/len(act)
  return ll


if __name__ == '__main__' :
    main(ParseOptions())
