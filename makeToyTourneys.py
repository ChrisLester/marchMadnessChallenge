#/bash/bin/python

#import sys
#if not sys.argv.count('-i') and not sys.argv.count('-b'):
#    sys.argv.append('-b 1')

import os
import scipy as sp
import random
from ROOT import *
from optparse import OptionParser

tourney_seed_file = 'training_inputs/tourney_seeds.csv'
input_file        = 'submissions/sample_submission.csv'

alpha = 0.03

#default_n_toys = 1

seeds = [1,16,8,9,5,12,4,13,6,11,3,14,7,10,2,15]

#-----------------------------------------------------------------------------------------------------        
def ParseOptions() :

    parser = OptionParser(usage='python makeToyTourneys.py -n n_toys')
    
    parser.add_option('-n', dest='n_toys', default=10, 
            help='number of toys to throw' )
    
    return parser.parse_args()


def main(options):
   
  ntoys = options[0].n_toys
      
  outcomes    = []
  predictions = []  
  
  fout = open('toy_tourneys.csv','w')
      
  for i in range(ntoys):
    makeToyTourney(i, fout)
      
  fout.close()
  return
  
def makeToyTourney(season, fout):
    
  #set up initial matchups
  matchups_r1 = []
  for i in range(4): #four conferences
    for j in range(8):  #eight first round games per conference
      team_lowseed  = int(100*(i+1) + seeds[2*j])
      team_highseed = int(100*(i+1) + seeds[2*j+1])
      matchups_r1.append( [team_lowseed,team_highseed] )
  
  #run the games
  runToy(season,matchups_r1, fout)
  
  return      

def runToy(season, games, fout):

  if (len(games) < 1): return
  
  next_round_games = []
  for i,team in enumerate(games):
    if team[0] == 0 or team[1] == 0: return
        
    #simple delta seed prob model
    prob = 0.50+0.03*(Seed(team[1])-Seed(team[0]))    
    
    rnum = random.random()    
    outcome = int(rnum <= prob)
    
    #print team[0], team[1], prob, rnum, outcome
    
    fout.write(str(season)+'_'+str(team[0])+'_'+str(team[1])+','+str(outcome)+'\n')
    
    winner = team[0] if outcome else team[1]    
    if (i%2 == 0):
      next_round_games.append([winner, 0])
    else:
      next_round_games[-1][1] = winner 
      
  runToy(season,next_round_games,fout)
  
  return  

#function to return seed of team given team id
def Seed(team):
  #dummy for now
  return team%100


#def Seed(season, team):
#
#  with open(tourney_seed_file) as f:
#    next(f)
#    for line in f:
#      tokens = line.split(',')
#      #print tokens
#      if not len(tokens) == 3: continue
#      if not tokens[0] == season: continue
#      if not int(tokens[2][0:3]) == team: continue
#      return int(tokens[1][1:3])
#  print 'Errror:',season,team
#  return -1    


if __name__ == '__main__' :
    main(ParseOptions())
