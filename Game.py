import numpy as np
import pandas as pd 
from Player import Player


class Game:

	def __init__(self, game_id, lineup_data):
		self.game_id = game_id
		self.lineup_data = lineup_data
		self.team1 = ''
		self.team2 = ''

		#Will hold all players that have checked in to the game for a team
		self.team1_players = []
		self.team2_players = []

		#Will hold the ids of the player objects, which is great for index tracking
		self.team1_ids = []
		self.team2_ids = []

		#Holds the players that are currently on the floor
		self.team1_current_lineup = []
		self.team2_current_lineup = []

		#Will hold the ids of the players currently on the floor, which is great for index tracking
		self.team1_current_ids = []
		self.team2_current_ids = []

		#Will hold the players who were on the court at the time of a foul
		self.team1_fouled_lineup = []
		self.team2_fouled_lineup = []

	#Finds the two teams invovled in a game
	def setTeams(self, counter):
		index = counter
		teams = []
		while self.team1 == '' or self.team2 == '':
			if self.lineup_data.loc[index]['Team_id'] not in teams:
				teams.append(self.lineup_data.loc[index]['Team_id'])
				#Sets team1 to the first unique team found
				if self.team1 == '':
					self.team1 = self.lineup_data.loc[index]['Team_id']
				#Sets team2 to the second unique team found
				else:
					self.team2 = self.lineup_data.loc[index]['Team_id']
			#Continues until two unique teams are found
			index += 1

	def setLineups(self, counter):
		index = counter
		#Loop stops after iterating through ten lines of the data, since ten lines cover the lineups of both teams at the beginning of each quarter
		stop = index + 10

		#Set the current lineups to empty so that we can add to them
		self.team1_current_lineup = []
		self.team1_current_ids = []
		self.team2_current_lineup = []
		self.team2_current_ids = []

		while index < stop:
			#If Player has already checked in for team1
			if self.lineup_data.loc[index]['Person_id'] in self.team1_ids:
				place = self.team1_ids.index(self.lineup_data.loc[index]['Person_id'])
				self.team1_current_lineup.append(self.team1_players[place])
				self.team1_current_ids.append(self.team1_players[place].player_id)

			#If Player has already checked in for team2
			elif self.lineup_data.loc[index]['Person_id'] in self.team2_ids:
				place = self.team2_ids.index(self.lineup_data.loc[index]['Person_id'])
				self.team2_current_lineup.append(self.team2_players[place])
				self.team2_current_ids.append(self.team2_players[place].player_id)

			#If Player hasn't already checked in - e.g. at the start of the game
			else:
				new_player = Player(self.lineup_data.loc[index]['Person_id'])
				#New Player must be on team 1
				if self.lineup_data.loc[index]['Team_id'] == self.team1:
					self.team1_players.append(new_player)
					self.team1_ids.append(new_player.player_id)
					self.team1_current_lineup.append(new_player)
					self.team1_current_ids.append(new_player.player_id)

				#New Player must be on team 2
				else:
					self.team2_players.append(new_player)
					self.team2_ids.append(new_player.player_id)
					self.team2_current_lineup.append(new_player)
					self.team2_current_ids.append(new_player.player_id)

			index += 1


	def madeShot(self, id, value):

		#team1 made the shot
		if self.team1 == id:
			made_basket = self.team1_current_lineup
			gave_up_basket = self.team2_current_lineup

		#team2 made the shot
		else:
			made_basket = self.team2_current_lineup
			gave_up_basket = self.team1_current_lineup

		#Increment the +/- for all those on the current lineup of the team who made the basket
		for i in made_basket:
			i.increment(value)

		#Decrement the +/- for all those on the current lineup of the team who gave up the basket
		for i in gave_up_basket:
			i.decrement(value)


	def substitution(self, player1_id, player2_id):

		#Player1 is in the game for team1.
		if player1_id in self.team1_current_ids:
			place = self.team1_current_ids.index(player1_id)
			self.team1_current_lineup.pop(place)
			self.team1_current_ids.pop(place)
			#Now, player1 is effectively removed from the current lineup

			#Player2 has previously checked in for team1. We find him and then add him to the current lineup.
			if player2_id in self.team1_ids:
				place = self.team1_ids.index(player2_id)
				self.team1_current_lineup.append(self.team1_players[place])
				self.team1_current_ids.append(player2_id)

			#Player2 has not checked in for team1, so let's add him to the team and then the current lineup.
			else:
				new_player = Player(player2_id)
				self.team1_players.append(new_player)
				self.team1_ids.append(player2_id)
				self.team1_current_lineup.append(new_player)
				self.team1_current_ids.append(player2_id)

		#Player1 is in the game for team2.
		else:
			place = self.team2_current_ids.index(player1_id)
			self.team2_current_lineup.pop(place)
			self.team2_current_ids.pop(place)

			if player2_id in self.team2_ids:
				place = self.team2_ids.index(player2_id)
				self.team2_current_lineup.append(self.team2_players[place])
				self.team2_current_ids.append(player2_id)

			else:
				new_player = Player(player2_id)
				self.team2_players.append(new_player)
				self.team2_ids.append(player2_id)
				self.team2_current_lineup.append(new_player)
				self.team2_current_ids.append(player2_id)


	def foul(self, action, value):
		value = value

		#These action_types respresent all technical fouls, for which one free throw is due
		if action in [11, 12, 13, 17, 18, 19, 21, 25, 30]:
			value = 1

		#Let's fill in the fouled lineups lists so that we know who was on the court at the time of the foul
		index = 0
		#Assumption that there are five people on the court for each team
		while index < 5:
			#Quantiy how many free throws each player is due for the purposes of +/-
			self.team1_current_lineup[index].freeThrow_increment(value)
			self.team2_current_lineup[index].freeThrow_increment(value)
			#We do this check to ensure that we don't have duplicate players in a fouled lineup, which could only occur in the 
			#case of multiple fouls - shooting foul + technical - before all free throws are completed
			if self.team1_current_lineup[index] not in self.team1_fouled_lineup:
				self.team1_fouled_lineup.append(self.team1_current_lineup[index])
			if self.team2_current_lineup[index] not in self.team2_fouled_lineup:
				self.team2_fouled_lineup.append(self.team2_current_lineup[index])
			index += 1

	#After a free throw, decrement the free throw each of the first five players in the fouled lineup list are due, and removes them from
	#the list if they are no longer due any free throws
	def update_fouled_lineups(self):
		#Keeps track of whcih players from both teams are no longer due free throws
		removable_list1 = []
		removable_list2 = []

		index = 0
		#Only iterates through first five players in the fouled_lineup list, in the rare case that there are multiple due to a foul, substitution, and ensuing technical before
		#the second free throw of the first foul was shot

		while index < 5:
			self.team1_fouled_lineup[index].freeThrow_decrement(1)
			if self.team1_fouled_lineup[index].ft_factor == 0:
				removable_list1.append(self.team1_fouled_lineup[index])
			self.team2_fouled_lineup[index].freeThrow_decrement(1)
			if self.team2_fouled_lineup[index].ft_factor == 0:
				removable_list2.append(self.team2_fouled_lineup[index])
			index += 1

		for i in removable_list1:
			self.team1_fouled_lineup.remove(i)
		for i in removable_list2:
			self.team2_fouled_lineup.remove(i)


	def free_throw(self, action, value, player1_id):

		#only have to do a player lookup for the free throw tuple of (3, 16). Although, it may just be more efficient to do the lookup
		#as it is here. Can change later while consolidating. Once changed, however, no results should be altered - that can be your test case
		if player1_id in self.team1_ids:
			team_id = self.team1
		else:
			team_id = self.team2

		#Made free throw - this is the only instance for which we want to increment / decrement the plus minus ratios
		if value == 1:
			index = 0
			while index < 5:
				#Team1 made it
				if team_id == self.team1:
					self.team1_fouled_lineup[index].increment(value)
					self.team2_fouled_lineup[index].decrement(value)

				#Team2 made it
				else:
					self.team2_fouled_lineup[index].increment(value)
					self.team1_fouled_lineup[index].decrement(value)
				index += 1

		self.update_fouled_lineups()
