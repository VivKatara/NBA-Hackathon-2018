import numpy as np
import pandas as pd
import csv
from Game import Game


def main():
	with open('KataraLi_SAT_Q1_BBALL.csv', 'w') as f:
		#Defining output columns
		fieldnames = ['Game_ID', 'Player_ID', 'Player_Plus/Minus']
		writer = csv.DictWriter(f, fieldnames = fieldnames)
		writer.writeheader()

		player_data = pd.read_csv("Play By Play Data Sample (50 Games).txt", sep = "\t")
		lineup_data = pd.read_csv("Game Lineup Data Sample (50 Games).txt", sep = "\t")

		#Keeps track of where we are in lineup_data
		lineup_index = 0
		block = 1

		#Iterate through each line in play by play
		for index, row in player_data.iterrows():
			#Start of a new period
		    if row['Event_Msg_Type'] == 12:

		    	#Start of a new game
		    	if row['Period'] == 1:
		       		new_game = Game(row['Game_id'], lineup_data)
		       		#Find both teams in the game
		        	new_game.setTeams(lineup_index)

		    	#Set lineups for each team
		    	new_game.setLineups(lineup_index)
		    	lineup_index += 10

		    #For all made shots except (1,0) tuple
		    elif row['Event_Msg_Type'] == 1 and row['Action_Type'] != 0:
		    	#Option 1 column specifies how many points the shot is worth
		    	new_game.madeShot(row['Team_id'], row['Option1'])

		    #For subs
		    elif row['Event_Msg_Type'] == 8:
		    	new_game.substitution(row['Person1'], row['Person2'])

		    #Except for technical fouls, Option 3 column details how many free throws, if any, are due after a foul is committed
		    elif row['Event_Msg_Type'] == 6 and (row['Option3'] != 0 or row['Action_Type'] in [11, 12, 13, 17, 18, 19, 21, 25, 30]):
		    	new_game.foul(row['Action_Type'], row['Option3'])

		    #For free throws
		    elif row['Event_Msg_Type'] == 3:
		    	new_game.free_throw(row['Action_Type'], row['Option1'], row['Person1'])

		    #For lane violations - Though there are only two instances in the data, these turnovers nullify a due free throw
		    elif row['Event_Msg_Type'] == 5 and row['Action_Type'] == 17:
		    	new_game.update_fouled_lineups()

		    #End of a game, print output
		    elif row['Event_Msg_Type'] == 13 and row['Period'] == 4:
		    	for i in new_game.team1_players:
		    		writer.writerow({'Game_ID' : new_game.game_id, 'Player_ID' : i.player_id, 'Player_Plus/Minus' : ("%+d" % (i.plus_minus))})
		    	for i in new_game.team2_players:
		    		writer.writerow({'Game_ID' : new_game.game_id, 'Player_ID' : i.player_id, 'Player_Plus/Minus' : ("%+d" % (i.plus_minus))})

		    else:
		    	continue

main()





