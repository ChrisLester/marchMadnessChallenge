#/bash/bin/python

import sys
if not sys.argv.count('-i') and not sys.argv.count('-b'):
    sys.argv.append('-b')

from array import array
from ROOT import *

#seed probablity root and associated functions 
seed_prob_file = TFile('seed_probabilities.root', 'READ') 
alpha = 0.03
def SimpleSeedPrediction(seed1, seed2):
  return 0.5 + alpha*(seed2-seed1)

def HistSeedPrediction(season, seed1, seed2):
  
  seed_prob_file  = TFile('seed_probabilities.root','READ')
  
  if seed_prob_file.Get('h_games_played_'+season).GetBinContent(seed1, seed2) >= 10:
    return seed_prob_file.Get('h_seed_winprob_'+season).GetBinContent(seed1, seed2)
  else:  
    return SimpleSeedPrediction(seed1,seed2)
 
seasons = map(chr, range(65, 84)) #hardcoded list of seasons from A to S

#get input dataset of tourney results
fin = TFile('mm_input.root','READ')
tourney_tree = fin.Get('tourney_results')
seed_tree    = fin.Get('tourney_seeds') 

#get team lookup table
fteam = TFile('mm_input_modified.root')
team_tree = fteam.Get('teams')
team_tree.BuildIndex('team','season_int')

#prepare modified output tree
fout = TFile('regression_train_tourney.root', 'RECREATE')
out_train = tourney_tree.CloneTree(0) 

#add branches
winfrac1 = array( 'f', [0])
out_train.Branch('winfrac1',winfrac1, 'winfrac1/F')

winfrac2 = array( 'f', [0])
out_train.Branch('winfrac2',winfrac2, 'winfrac2/F')

avg_scorediff1 = array( 'f', [0])
out_train.Branch('avg_scorediff1',avg_scorediff1, 'avg_scorediff1/F')

avg_scorediff2 = array( 'f', [0])
out_train.Branch('avg_scorediff2',avg_scorediff2, 'avg_scorediff2/F')

rms_scorediff1 = array( 'f', [0])
out_train.Branch('rms_scorediff1',rms_scorediff1, 'rms_scorediff1/F')

rms_scorediff2 = array( 'f', [0])
out_train.Branch('rms_scorediff2',rms_scorediff2, 'rms_scorediff2/F')

avg_score_for1 = array( 'f', [0])
out_train.Branch('avg_score_for1',avg_score_for1, 'avg_score_for1/F')

avg_score_for2 = array( 'f', [0])
out_train.Branch('avg_score_for2',avg_score_for2, 'avg_score_for2/F')

avg_score_against1 = array( 'f', [0])
out_train.Branch('avg_score_against1',avg_score_against1, 'avg_score_against1/F')

avg_score_against2 = array( 'f', [0])
out_train.Branch('avg_score_against2',avg_score_against2, 'avg_score_against2/F')

avg_opp_score_for1 = array( 'f', [0])
out_train.Branch('avg_opp_score_for1',avg_opp_score_for1, 'avg_opp_score_for1/F')

avg_opp_score_for2 = array( 'f', [0])
out_train.Branch('avg_opp_score_for2',avg_opp_score_for2, 'avg_opp_score_for2/F')

avg_opp_score_against1 = array( 'f', [0])
out_train.Branch('avg_opp_score_against1',avg_opp_score_against1, 'avg_opp_score_against1/F')

avg_opp_score_against2 = array( 'f', [0])
out_train.Branch('avg_opp_score_against2',avg_opp_score_against2, 'avg_opp_score_against2/F')

seed1 = array( 'i', [0])
out_train.Branch('seed1',seed1, 'seed1/I')

seed2 = array( 'i', [0])
out_train.Branch('seed2',seed2, 'seed2/I')

team1 = array( 'i', [0])
out_train.Branch('team1',team1, 'team1/I')

team2 = array( 'i', [0])
out_train.Branch('team2',team2, 'team2/I')

season_int = array( 'i', [0])
out_train.Branch('season_int',season_int, 'season_int/I')

game_outcome = array( 'i', [0])
out_train.Branch('game_outcome',game_outcome, 'game_outcome/I')

seed_prob = array( 'f', [0])
out_train.Branch('seed_prob',seed_prob, 'seed_prob/F')



n_games = tourney_tree.GetEntries()
i = 0 

# loop over tourney games and find team stats/seed for each team
for game in tourney_tree:
  
    i+=1 
    if not i%50: print 'Processing tourney game %d/%d'%(i,n_games)
    
    season_int[0] = seasons.index(game.season[0])
      
    # grab team performances from team tree
    team1[0] = min(game.wteam, game.lteam)        
    if not (team_tree.GetEntryWithIndex( team1[0], season_int[0]) > 0):
      print "ERROR: Did not find:", team1[0], game.season[0]
      continue
    seed1[0] = team_tree.seed
    winfrac1[0] = team_tree.winfrac
    avg_scorediff1[0] = team_tree.avg_scorediff
    rms_scorediff1[0] = team_tree.rms_scorediff
    avg_score_for1[0] = team_tree.avg_score_for
    avg_score_against1[0] = team_tree.avg_score_against
    avg_opp_score_for1[0] = team_tree.avg_opp_score_for
    avg_opp_score_against1[0] = team_tree.avg_opp_score_against
    
    team2[0] = max(game.wteam, game.lteam)        
    if not (team_tree.GetEntryWithIndex( team2[0], season_int[0]) > 0):
      print "ERROR: Did not find:", team2[0], game.season[0]
      continue
    seed2[0] = team_tree.seed
    winfrac2[0] = team_tree.winfrac
    avg_scorediff2[0] = team_tree.avg_scorediff
    rms_scorediff2[0] = team_tree.rms_scorediff
    avg_score_for2[0] = team_tree.avg_score_for
    avg_score_against2[0] = team_tree.avg_score_against
    avg_opp_score_for2[0] = team_tree.avg_opp_score_for
    avg_opp_score_against2[0] = team_tree.avg_opp_score_against

    seed_prob[0] = HistSeedPrediction(game.season[0], seed1[0],seed2[0])

    game_outcome[0] = (team1[0] == game.wteam)
    
    # fill the tree 
    out_train.Fill()

fout.cd()
out_train.Write()
fout.Close() 
