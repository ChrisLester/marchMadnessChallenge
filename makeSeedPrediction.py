#/bash/bin/python

#import sys
#if not sys.argv.count('-i') and not sys.argv.count('-b'):
#    sys.argv.append('-b 1')

import os
import scipy as sp
from ROOT import *
from optparse import OptionParser

tourney_seed_file = 'training_inputs/tourney_seeds.csv'
input_file   = 'submissions/sample_submission.csv'

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
  
  fout = open('submissions/seed_submission.csv','w')
      
  with open(input_file,'r') as f:     
    next(f)
    for line in f:
      tokens = line.split(',')
      if not len(tokens) == 2: continue
      
      game_id    = tokens[0]
 
      season = game_id[0]
      team1  = int(game_id[2:5])	 
      team2  = int(game_id[6:9])	 
      #print game_id, season, team1, team2
      
      seed_team1 = Seed(season, team1)
      seed_team2 = Seed(season, team2)
      if seed_team1 == -1 or seed_team2 == -1:
        print"ERROR: seed not found",season, team1, seed_team1, team2, seed_team2
	
      prediction = 0.5 + alpha*(seed_team2 - seed_team1)
      
      entry = game_id+','+str(prediction)+'\n'
      
      fout.write(entry)
      
  fout.close()
  return
  

def llfun(act, pred):
  epsilon = 1e-15
  pred = sp.maximum(epsilon, pred)
  pred = sp.minimum(1-epsilon, pred)
  ll = sum(act*sp.log(pred) + sp.subtract(1,act)*sp.log(sp.subtract(1,pred)))
  ll = ll * -1.0/len(act)
  return ll


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
