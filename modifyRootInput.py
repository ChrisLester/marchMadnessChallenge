#/bash/bin/python

import sys
if not sys.argv.count('-i') and not sys.argv.count('-b'):
    sys.argv.append('-b')

from array import array
from ROOT import *
import scipy as sp

#get input
fin = TFile('mm_input.root','READ')
game_tree = fin.Get('regular_season_results')
team_tree = fin.Get('teams')


#prepare output tree
fout = TFile('mm_input_modified.root', 'RECREATE')
#out_game_tree = game_tree.CloneTree(0)
temp_team_tree = team_tree.CloneTree(0)

#add branches
winfrac = array( 'd', [0])
temp_team_tree.Branch('winfrac',winfrac, 'winfrac/D')

avg_score_for = array ('d', [0] )
temp_team_tree.Branch('avg_score_for',avg_score_for,'avg_score_for/D')

avg_score_against = array ('d', [0] )
temp_team_tree.Branch('avg_score_against',avg_score_against,'avg_score_against/D')

avg_scorediff = array( 'd', [0])
temp_team_tree.Branch('avg_scorediff',avg_scorediff, 'avg_scorediff/D')

rms_scorediff = array( 'd', [0])
temp_team_tree.Branch('rms_scorediff',rms_scorediff, 'rms_scorediff/D')

season = array( 'c', 'A\0')
temp_team_tree.Branch('season', season, 'season/C')

season_int = array( 'i', [0])
temp_team_tree.Branch('season_int', season_int, 'season_int/I')

#htemp=TH1F('htemp','',2,-0.5,1.5)
hscorediff=TH1F('hscorediff','',200,-100,100)
hscore=TH2F('hscore','',150,0,150,150,0,150)

# loop over events and calculate new variables
seasons = map(chr, range(65, 83)) #hardcoded list of seasons from A to R
n_seasons = len(seasons) 

n_teams = team_tree.GetEntries()
for i in range(n_teams):
#for i in range(5):
  
  team_tree.GetEntry(i)
  
  if not i%50: print 'Processing team %d/%d'%(i,n_teams)
    
  for i,ssn in enumerate(seasons):
  
    #define selections
    sel_season = '(season == \"'+ssn+'\")' 
    sel_team_won  = '(wteam=='+str(team_tree.team)+')'
    sel_team_lst  = '(lteam=='+str(team_tree.team)+')'
    sel_team_all  = '('+sel_team_won+'||'+sel_team_lst+')'

    game_tree.Draw('>>game_list',sel_season+'&&'+sel_team_all)
    game_list = gDirectory.Get('game_list')
    
    var_scorediff = "(wscore - lscore)*(+1*(wteam=="+str(team_tree.team)+") + -1*(lteam=="+str(team_tree.team)+"))"
    game_tree.Draw(var_scorediff+">>hscorediff",sel_season+'&&'+sel_team_all)  
    
    ngamesplayed = game_list.GetN()
    if (ngamesplayed==0): continue
    current_team   = team_tree.team

    ngameswon = 0
    scores_for = []
    scores_against = []
    score_diffs = []
    for j in range(ngamesplayed):
      game_tree.GetEntry(game_list.GetEntry(j))
      
      won = game_tree.wteam == current_team
      if (won): ngameswon += 1 
      scores_for.append( game_tree.wscore if won else game_tree.lscore)
      scores_against.append( game_tree.lscore if won else game_tree.wscore)
      score_diffs.append( (game_tree.wscore-game_tree.lscore)*(+1 if won else -1))
      
    avg_score_for[0]     = sp.average(scores_for)
    avg_score_against[0] = sp.average(scores_against)
    
    season[0]  		= ssn[0]
    season_int[0]	= i
    winfrac[0]		= ngameswon / ngamesplayed
    avg_scorediff[0] 	= sp.average(score_diffs)
    rms_scorediff[0] 	= sp.sqrt(1./ngamesplayed*sum((sd-avg_scorediff[0])**2 for sd in score_diffs))
    
    temp_team_tree.Fill()

print "Building index"
temp_team_tree.BuildIndex('team','season_int')
print "Done"


out_team_tree = temp_team_tree.CloneTree(0)

avg_opp_score_for = array ('d', [0] )
out_team_tree.Branch('avg_opp_score_for',avg_opp_score_for,'avg_opp_score_for/D')

avg_opp_score_against = array ('d', [0] )
out_team_tree.Branch('avg_opp_score_against',avg_opp_score_against,'avg_opp_score_against/D')

n_teams = temp_team_tree.GetEntries()
for i in range(n_teams):
  
  if not i%50: print 'Processing team %d/%d'%(i,n_teams)

  temp_team_tree.GetEntry(i)
  
  sel_season = '(season == \"'+temp_team_tree.season[0]+'\")' 
  sel_team_won  = '(wteam=='+str(temp_team_tree.team)+')'
  sel_team_lst  = '(lteam=='+str(temp_team_tree.team)+')'
  sel_team_all  = '('+sel_team_won+'||'+sel_team_lst+')'

  game_tree.Draw('>>game_list',sel_season+'&&'+sel_team_all)
  game_list = gDirectory.Get('game_list')
  
  avg_opp_score_for[0] = 0
  avg_opp_score_against[0] = 0
  ngames = game_list.GetN()
  current_team = temp_team_tree.team
  current_season = temp_team_tree.season_int
  
  if (ngames==0): continue
  
  n_opponents = 0
  for j in range(ngames):
    game_tree.GetEntry(game_list.GetEntry(j))
    
    opp_team = game_tree.lteam if game_tree.wteam == current_team else game_tree.wteam
    
    found = (temp_team_tree.GetEntryWithIndex(opp_team, current_season) > 0)
    if not found: 
      print "Warning: opponent team not found: ", opp_team, current_season
      continue
      
    n_opponents += 1
    avg_opp_score_for[0] += temp_team_tree.avg_score_for
    avg_opp_score_against[0] += temp_team_tree.avg_score_against
  
  avg_opp_score_for[0] *= 1./n_opponents if n_opponents != 0 else 0
  avg_opp_score_against[0] *= 1./n_opponents if n_opponents != 0 else 0
 
  out_team_tree.Fill()

out_team_tree.BuildIndex('team','season_int')
  
out_team_tree.Write()
fout.Close()
