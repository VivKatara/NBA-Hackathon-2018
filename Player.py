class Player:
    
    def __init__(self, player_id):
        self.player_id = player_id
        self.plus_minus = 0
        #Indicates how many free throws a player is due towards +/- after being on the court at the time of a free throw inducing foul free throws
        self.ft_factor = 0
        

    def increment(self, value):
        self.plus_minus += value
    
    
    def decrement(self, value):
        self.plus_minus -= value


    def freeThrow_increment(self, value):
    	self.ft_factor += value


    def freeThrow_decrement(self, value):
    	self.ft_factor -= value