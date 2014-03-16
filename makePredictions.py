#/bash/bin/python

#import sys
#if not sys.argv.count('-i') and not sys.argv.count('-b'):
#    sys.argv.append('-b 1')

import os
import scipy as sp
from ROOT import *
from optparse import OptionParser
import array


input_file   = 'training_inputs/tourney_seeds.csv'
teams_file_name   = 'mm_input_modified.root'

alpha = 0.03

var0 = array.array('f',[0]) ; 
var1 = array.array('f',[0]) ; 
var2 = array.array('f',[0]) ; 
var3 = array.array('f',[0]) ; 
var4 = array.array('f',[0]) ; 
var5 = array.array('f',[0]) ; 
var6 = array.array('f',[0]) ; 
var7 = array.array('f',[0]) ;
var8 = array.array('f',[0]) ;
var9 = array.array('f',[0]) ;
var10 = array.array('f',[0]) ;
var11 = array.array('f',[0]) ;
var12 = array.array('f',[0]) ;

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
    
  seasons 	= []
  teams_season 	= []
  seeds_season 	= []
  outcomes    	= []
  predictions 	= []          

    
  #load tourney team/seed info
  print 'Loading tourney info...'
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
  print 'Done.'
  
  
  #BDT reader initialization
  reader = TMVA.Reader()
  reader.AddSpectator("season", var0)

  #reader.AddVariable("seed1-seed2",var1)
  reader.AddVariable("seed1",		var1)
  reader.AddVariable("seed2",		var2)
  reader.AddVariable("winfrac1",	var3)
  reader.AddVariable("winfrac2",	var4)
  reader.AddVariable("avg_scorediff1",	var5)
  reader.AddVariable("avg_scorediff2",	var6)
  reader.AddVariable('rms_scorediff1', var7),
  reader.AddVariable('rms_scorediff2', var8),
  reader.AddVariable('avg_opp_score_for1',var9),
  reader.AddVariable('avg_opp_score_for2',var10),
  reader.AddVariable('avg_opp_score_against1',var11),
  reader.AddVariable('avg_opp_score_against2',var12)
  
  for season in seasons:
    #reader.BookMVA('BDT_'+season,'./weights/regressionMVA_'+season+'_BDT_MaxDepth4.weights.xml')
    #reader.BookMVA('BDT_'+season,'./weights/regressionMVA_'+season+'_BDT.weights.xml')
    reader.BookMVA('LD_'+season,'./weights/regressionMVA_'+season+'_LD.weights.xml')

  fout = open('submissions/submission.csv','w')
  for i,season in enumerate(seasons):
    print 'Predicting season', season 
    for t1,team1 in enumerate(teams_season[i]):
      for t2,team2 in enumerate(teams_season[i]):
	if (team1 > team2): continue
	
        #make prediction
	#prediction = SimpleSeedPrediction(seeds_season[i][t1], seeds_season[i][t2])
        #prediction = HistSeedPrediction(season,seeds_season[i][t1], seeds_season[i][t2])
        #prediction = MVAPrediction(season, i, team1, team2, reader, 'BDT')
        prediction = MVAPrediction(season, i, team1, team2, reader, 'LD')
	
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
    
def MVAPrediction(season, season_i, team1, team2, reader, method):
  
  teams_file = TFile(teams_file_name,'READ')
  teams = teams_file.Get("teams")
  
  if not (teams.GetEntryWithIndex(team1, season_i) > 0):
    print "Error: Team not found:",team1, season_i 
    return

  team1_seed 			= teams.seed
  team1_avg_scorediff 		= teams.avg_scorediff
  team1_rms_scorediff 		= teams.rms_scorediff
  team1_winfrac 		= teams.winfrac  
  team1_avg_opp_score_for     	= teams.avg_opp_score_for 
  team1_avg_opp_score_against 	= teams.avg_opp_score_against 
  
  if not (teams.GetEntryWithIndex(team2, season_i) > 0):
    print "Error: Team not found:",team2, season_i
    return 

  team2_seed 			= teams.seed
  team2_avg_scorediff 		= teams.avg_scorediff
  team2_rms_scorediff 		= teams.rms_scorediff
  team2_winfrac 		= teams.winfrac  
  team2_avg_opp_score_for     	= teams.winfrac  
  team2_avg_opp_score_against 	= teams.winfrac  

   
  var0[0] = season_i   
  
  var1[0] = team1_seed
  var2[0] = team2_seed
  var3[0] = team1_winfrac  
  var4[0] = team2_winfrac  
  var5[0] = team1_avg_scorediff
  var6[0] = team2_avg_scorediff
  var7[0] = team1_rms_scorediff 
  var8[0] = team2_rms_scorediff  
  var9[0] = team1_avg_opp_score_for
  var10[0] = team2_avg_opp_score_for 
  var11[0] = team1_avg_opp_score_against 
  var12[0] = team2_avg_opp_score_against  
    
  output = reader.EvaluateMVA(method+'_'+season) 
  
  return output

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