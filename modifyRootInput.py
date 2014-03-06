#/bash/bin/python

import sys
if not sys.argv.count('-i') and not sys.argv.count('-b'):
    sys.argv.append('-b')

from array import array
from ROOT import *

#get input
fin = TFile('mm_input.root','READ')
game_tree = fin.Get('regular_season_results')
team_tree = fin.Get('teams')


#prepare output tree
fout = TFile('mm_input_modified.root', 'RECREATE')
#out_game_tree = game_tree.CloneTree(0)
out_team_tree = team_tree.CloneTree(0)

#add branches
winfrac = array( 'd', [0])
out_team_tree.Branch('winfrac',winfrac, 'winfrac/D')

avg_scorediff = array( 'd', [0])
out_team_tree.Branch('avg_scorediff',avg_scorediff, 'avg_scorediff/D')

rms_scorediff = array( 'd', [0])
out_team_tree.Branch('rms_scorediff',rms_scorediff, 'rms_scorediff/D')

season = array( 'c', 'A\0')
out_team_tree.Branch('season', season, 'season/C')

#htemp=TH1F('htemp','',2,-0.5,1.5)
hscorediff=TH1F('hscorediff','',200,-100,100)

# loop over events and calculate new variables
seasons = map(chr, range(65, 83)) #hardcoded list of seasons from A to R
n_seasons = len(seasons) 

n_teams = team_tree.GetEntries()
for i in range(n_teams):
#for i in range(5):
  
  team_tree.GetEntry(i)
  
  if not i%50: print 'Processing team %d/%d'%(i,n_teams)
    
  for ssn in seasons:
  
    #if not i%10000: print 'Processing entry %d/%d'%(i,n_entries)

    #define selections
    #sel_season = '(season == \"'+game_tree.season[:-1]+'\")'  # remove final char which is \0
    sel_season = '(season == \"'+ssn+'\")' 

    sel_team_won  = '(wteam=='+str(team_tree.team)+')'
    sel_team_lst  = '(lteam=='+str(team_tree.team)+')'
    sel_team_all  = '('+sel_team_won+'||'+sel_team_lst+')'

    #sel_lteam_won  = '(wteam=='+str(game_tree.lteam)+')'
    #sel_lteam_lst  = '(lteam=='+str(game_tree.lteam)+')'
    #sel_lteam_all  = '('+sel_lteam_won+'||'+sel_lteam_lst+')'
    
    var_scorediff = "(wscore - lscore)*(+1*(wteam=="+str(team_tree.team)+") + -1*(lteam=="+str(team_tree.team)+"))"
    game_tree.Draw(var_scorediff+">>hscorediff",sel_season+'&&'+sel_team_all)  
    
    ngamesplayed = hscorediff.Integral()
    if (ngamesplayed == 0): continue    

    ngameswon    = hscorediff.Integral(101,200)

    season[0]  		= ssn[0]
    winfrac[0]		= ngameswon / ngamesplayed
    avg_scorediff[0] 	= hscorediff.GetMean()
    rms_scorediff[0] 	= hscorediff.GetRMS()
    
    out_team_tree.Fill()

#out_team_tree.BuildIndex('team','season')

out_team_tree.Write()
fout.Close()
