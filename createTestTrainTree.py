#/bash/bin/python

import sys
if not sys.argv.count('-i') and not sys.argv.count('-b'):
    sys.argv.append('-b')

from array import array
from ROOT import *

#get input dataset of tourney results
fin = TFile('mm_input.root','READ')
tourney_tree = fin.Get('tourney_results')
seed_tree    = fin.Get('tourney_seeds') 

#get team lookup table
fteam = TFile('mm_input_modified.root')
team_tree = fteam.Get('teams')

#prepare modified output tree
fout = TFile('mm_train_tourney.root', 'RECREATE')
out_train_l = tourney_tree.CloneTree(0) 
out_train_l.SetName('tourney_results_l') 
out_train_w = tourney_tree.CloneTree(0) 
out_train_w.SetName('tourney_results_w') 

#add branches
w_winfrac = array( 'f', [0])
out_train_l.Branch('o_winfrac',w_winfrac, 'o_winfrac/F')
out_train_w.Branch('m_winfrac',w_winfrac, 'm_winfrac/F')

w_avg_scorediff = array( 'f', [0])
out_train_l.Branch('o_avg_scorediff',w_avg_scorediff, 'o_avg_scorediff/F')
out_train_w.Branch('m_avg_scorediff',w_avg_scorediff, 'm_avg_scorediff/F')

w_rms_scorediff = array( 'f', [0])
out_train_l.Branch('o_rms_scorediff',w_rms_scorediff, 'o_rms_scorediff/F')
out_train_w.Branch('m_rms_scorediff',w_rms_scorediff, 'm_rms_scorediff/F')

w_seed = array( 'd', [0])
out_train_w.Branch('m_seed',w_seed, 'm_seed/D')
out_train_l.Branch('o_seed',w_seed, 'o_seed/D')

l_winfrac = array( 'f', [0])
out_train_w.Branch('o_winfrac',l_winfrac, 'o_winfrac/F')
out_train_l.Branch('m_winfrac',l_winfrac, 'm_winfrac/F')

l_avg_scorediff = array( 'f', [0])
out_train_w.Branch('o_avg_scorediff',l_avg_scorediff, 'o_avg_scorediff/F')
out_train_l.Branch('m_avg_scorediff',l_avg_scorediff, 'm_avg_scorediff/F')

l_rms_scorediff = array( 'f', [0])
out_train_w.Branch('o_rms_scorediff',l_rms_scorediff, 'o_rms_scorediff/F')
out_train_l.Branch('m_rms_scorediff',l_rms_scorediff, 'm_rms_scorediff/F')

l_seed = array( 'd', [0])
out_train_w.Branch('o_seed',l_seed, 'o_seed/D')
out_train_l.Branch('m_seed',l_seed, 'm_seed/D')

n_games = tourney_tree.GetEntries()
i = 0 

# loop over tourney games and find team stats/seed for each team
for game in tourney_tree:
  
    i+=1 
    if not i%50: print 'Processing tourney game %d/%d'%(i,n_games)
    
    # preset added values
    found_wteam = False
    found_lteam = False
    w_winfrac[0] = -1
    w_avg_scorediff[0] =   -1 
    w_rms_scorediff[0] =   -1 
    l_winfrac[0] = -1
    l_avg_scorediff[0] = -1 
    l_rms_scorediff[0] = -1       
   
    # grab team performances from team tree
    for entry in team_tree:
        if not game.season == entry.season: continue 

        if entry.team == game.wteam:
            found_wteam = True
            w_winfrac[0] = entry.winfrac
            w_avg_scorediff[0] = entry.avg_scorediff
            w_rms_scorediff[0] = entry.rms_scorediff
        if entry.team == game.lteam:
            found_lteam = True
            l_winfrac[0] = entry.winfrac
            l_avg_scorediff[0] = entry.avg_scorediff
            l_rms_scorediff[0] = entry.rms_scorediff            
        if found_lteam and found_wteam: break
     

    # preset seed values
    found_wteam_seed = False
    found_lteam_seed = False
    w_seed[0] = -1 
    l_seed[0] = -1   

    # grab seed values from seeed tree
    for entry in seed_tree: 
        if not game.season == entry.season: continue 
        if entry.team == game.wteam:
            found_wteam_seed = True
            w_seed[0] = int(''.join(c for c in entry.seed if c in '1234567890')) 
        if entry.team == game.lteam:
            found_lteam_seed = True
            l_seed[0] = int(''.join(c for c in entry.seed if c in '1234567890'))       
        if found_lteam_seed and found_wteam_seed: break


    # fill the tree 
    out_train_l.Fill()
    out_train_w.Fill()

fout.cd()
out_train_w.Write()
out_train_l.Write()
fout.Close() 
