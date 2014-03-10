#/bash/bin/python

#import sys
#if not sys.argv.count('-i') and not sys.argv.count('-b'):
#    sys.argv.append('-b 1')

import os
import scipy as sp
from ROOT import *
from optparse import OptionParser

tourney_file_name = 'mm_input.root'
tourney_seed_file = 'training_inputs/tourney_seeds.csv'
input_file   = 'submissions/sample_submission.csv'

alpha = 0.03

seasons = map(chr, range(65, 84)) #hardcoded list of seasons from A to S

#-----------------------------------------------------------------------------------------------------        
def ParseOptions() :

    parser = OptionParser(usage='python evaluatePrediction.py --file filename')
    
    #parser.add_option('-f', dest='input_file', default=None, 
    #        help='Input file (one file only)' )
    
    return parser.parse_args()


def main(options):
    
  if not os.path.isfile(tourney_file_name):
    print "File not found"
    return
  
  tourney_file    = TFile(tourney_file_name,'READ')
  tourney_results = tourney_file.Get('tourney_results')
    
  fout = TFile('seed_probabilities.root', 'RECREATE')

  h_games_played = [ TH2F('h_games_played_'+season,'',16,0.5,16.5,16,0.5,16.5) for season in seasons ]
  h_games_won    = [ TH2F('h_games_won_'+season,   '',16,0.5,16.5,16,0.5,16.5) for season in seasons ]
  h_seed_winprob = [ TH2F('h_seed_winprob_'+season,'',16,0.5,16.5,16,0.5,16.5) for season in seasons ]

  for game in tourney_results:
        
    seed_wteam = Seed(game.season, game.wteam)
    seed_lteam = Seed(game.season, game.lteam)
    
    for i,season in enumerate(seasons):
      if (game.season[0] == season): continue
	
      h_games_played[i].Fill(seed_wteam, seed_lteam)
      h_games_played[i].Fill(seed_lteam, seed_wteam)    
      h_games_won[i].Fill(seed_wteam, seed_lteam, 1)
  
  for i in range(len(seasons)):
    h_seed_winprob[i].Divide(h_games_won[i],h_games_played[i])
  
    h_games_played[i].Write()
    h_games_won[i].Write()
    h_seed_winprob[i].Write()
    
  fout.Close()
  return
     

def Seed(season, team):

  with open(tourney_seed_file) as f:
    next(f)
    for line in f:
      tokens = line.split(',')
      #print tokens
      if not len(tokens) == 3: continue
      if not tokens[0] == season[0]: continue
      if not int(tokens[2][0:3]) == team: continue
      return int(tokens[1][1:3])
  print 'Error:',season,team
  return -1    


if __name__ == '__main__' :
    main(ParseOptions())
