#/bash/bin/python

#import sys
#if not sys.argv.count('-i') and not sys.argv.count('-b'):
#    sys.argv.append('-b 1')

import os
import scipy as sp
from ROOT import *
from optparse import OptionParser

input_file   = 'training_inputs/tourney_seeds.csv'
#input_file   = 'submissions/sample_submission.csv'
#input_file   = 'training_input/sample_submission.csv'

alpha = 0.03

#-----------------------------------------------------------------------------------------------------        
def ParseOptions() :

    parser = OptionParser(usage='python evaluatePrediction.py --file filename')
    
    #parser.add_option('-f', dest='input_file', default=None, 
    #        help='Input file (one file only)' )
    
    return parser.parse_args()


def main(options):
    
  if not os.path.isfile(input_file):
    print "File not found"
    return
  
  outcomes    = []
  predictions = []  
        
  seasons = []
  teams_season = []
  seeds_season = []
  with open(input_file,'r') as f:     
    next(f)
    for line in f:
      tokens = line.split(',')
      if not len(tokens) == 3: continue
 
      season = tokens[0]
      seed   = int(tokens[1][1:3])	 
      team   = int(tokens[2])	 
      #print game_id, season, team1, team2
      if season not in seasons:
        seasons.append(season)
	teams_season.append( [team] )
	seeds_season.append( [seed] )
      else:
        index = seasons.index(season)
	teams_season[index].append(team)
	seeds_season[index].append(seed)

  fout = open('submissions/histseed_allseasons_submission.csv','w')
  for i,season in enumerate(seasons):
    for t1,team1 in enumerate(teams_season[i]):
      for t2,team2 in enumerate(teams_season[i]):
	if (team1 > team2): continue
	
        #make prediction
	#prediction = SimpleSeedPrediction(seeds_season[i][t1], seeds_season[i][t2])
        prediction = HistSeedPrediction(season,seeds_season[i][t1], seeds_season[i][t2])

        #bound prediction
	prediction = min(0.999, prediction)
        prediction = max(0.001, prediction)
      
        entry = season+'_'+str(team1)+'_'+str(team2)+','+str(prediction)+'\n'
      
        fout.write(entry)
      
  fout.close()
  return
  
def SimpleSeedPrediction(seed1, seed2):
  return 0.5 + alpha*(seed2-seed1)

def HistSeedPrediction(season, seed1, seed2):
  
  seed_prob_file  = TFile('seed_probabilities.root','READ')
  
  if seed_prob_file.Get('h_games_played_'+season).GetBinContent(seed1, seed2) >= 10:
    return seed_prob_file.Get('h_seed_winprob_'+season).GetBinContent(seed1, seed2)
  else:  
    return SimpleSeedPrediction(seed1,seed2)
    
    
def Seed(season, team):

  with open(tourney_seed_file) as f:
    next(f)
    for line in f:
      tokens = line.split(',')
      #print tokens
      if not len(tokens) == 3: continue
      if not tokens[0] == season: continue
      if not int(tokens[2][0:3]) == team: continue
      return int(tokens[1][1:3])
  print 'Errror:',season,team
  return -1    


if __name__ == '__main__' :
    main(ParseOptions())
