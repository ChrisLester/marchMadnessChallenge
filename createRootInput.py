#/bash/bin/python

from ROOT import *

fout = TFile('mm_input.root','RECREATE')

tree = TTree('regular_season_results','')
tree.ReadFile('training_inputs/regular_season_results.csv')
tree.Write()

tree = TTree('teams','')
tree.ReadFile('training_inputs/teams.csv')
tree.Write()

tree = TTree('seasons','')
tree.ReadFile('training_inputs/seasons.csv')
tree.Write()

tree = TTree('tourney_results','')
tree.ReadFile('training_inputs/tourney_results.csv')
tree.Write()

tree = TTree('tourney_seeds','')
tree.ReadFile('training_inputs/tourney_seeds.csv')
tree.Write()

tree = TTree('tourney_slots','')
tree.ReadFile('training_inputs/tourney_slots.csv')
tree.Write()

fout.Close()




#import csv

#teams_id = []
#teams_name = [] 
#teams_winfrac = []
#
#with open('training_inputs/teams.csv', 'r') as teamfile:
#   
#  for i,line in enumerate(teamfile.readlines()):
#    if (i==0): continue
#    tokens = line.split(',')
#    
#    if len(tokens) != 2: 
#      print "ERROR len(line)=",len(tokens) 
#      continue
#    teams_id.append(tokens[0])
#    teams_name.append(tokens[1]) 
#
#
#games_
#
#with open('training_inputs/regular_season_results.csv', 'r') as gamefile:
#  
#    for i,line in enumerate(gamefile.readlines()):
#    if (i==0): continue
#    tokens = line.split(',')
#
#   

