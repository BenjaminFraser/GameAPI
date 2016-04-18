import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    wins = ndb.IntegerProperty(default=0)
    total_played = ndb.IntegerProperty(default=0)

    @property
    def win_percentage(self):
        """Returns the users win percentage"""
        if self.total_played > 0:
            return float(self.wins)/float(self.total_played)
        else:
            return 0

    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email,
                        wins=self.wins,
                        total_played=self.total_played,
                        win_percentage=self.win_percentage)

    def add_win(self):
        """Add a win"""
        self.wins += 1
        self.total_played += 1
        self.put()

    def add_loss(self):
        """Add a loss"""
        self.total_played += 1
        self.put()


class Game(ndb.Model):
    """Game object"""
    grid_1 = ndb.PickleProperty(required=True)
    grid_2 = ndb.PickleProperty(required=True)
    ships_1 = ndb.PickleProperty(required=True)
    ships_2 = ndb.PickleProperty(required=True)
    next_move = ndb.KeyProperty(required=True) # The User's whose turn it is
    user_1 = ndb.KeyProperty(required=True, kind='User')
    user_2 = ndb.KeyProperty(required=True, kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty()
    history = ndb.PickleProperty(required=True)

    @classmethod
    def new_game(cls, user_1, user_2):
        """Creates and returns a new game"""
        game = Game(user_1=user_1,
                    user_2=user_2,
                    next_move=user_1)
        # create an empty 10 x 10 grid and update grid 1 and 2.
        rows = [y for y in range(10)]
        columns = [x for x in range(10)]
        new_board = [['-' for row in rows] for col in columns]
        game.grid_1 = game.grid_2 = new_board
        # create a dict object with default 0 ships of each type.
        empty_ships = { 'Aircraft Carrier' : 0, 'Battleship' : 0,
                        'Submarine' : 0, 'Destroyer' : 0,
                        'Patrol boat' : 0 }
        # set user 1 and user 2 ships to the default
        game.ships_1 = game.ships_2 = empty_ships
        game.history = []
        game.put()
        return game

    def insert_user_1_ships(self, ships_dict_array):
        """Places user 1's ships throughout grid 1 within the
           selected cell co-ordinates and orientation (vert or horizontal).
           ships_array must be a dictionary with array values, providing the ships row,
           column and its orientation, in the format like the following example:
           ships_dict_array = {'Aircraft Carrier' : [2, 3, 'vertical']
                               'Battleship' : [4, 5, 'horizontal']}
        """


    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = GameForm(urlsafe_key=self.key.urlsafe(),
                        grid_1 = str(self.grid_1),
                        grid_2 = str(self.grid_2),
                        ships_1 = str(self.grid_1),
                        ships_2 = str(self.grid_2),
                        user_1=self.user_1.get().name,
                        user_2=self.user_2.get().name,
                        next_move=self.next_move.get().name,
                        game_over=self.game_over)
        if self.winner:
            form.winner = self.winner.get().name
        return form

    def end_game(self, winner):
        """Ends the game"""
        self.winner = winner
        self.game_over = True
        self.put()
        loser = self.user_2 if winner == self.user_1 else self.user_1
        # Add the game to the score 'board'
        score = Score(date=date.today(), winner=winner, loser=loser)
        score.put()

        # Update the user models
        winner.get().add_win()
        loser.get().add_loss()


class Score(ndb.Model):
    """Score object"""
    date = ndb.DateProperty(required=True)
    winner = ndb.KeyProperty(required=True)
    loser = ndb.KeyProperty(required=True)

    def to_form(self):
        return ScoreForm(date=str(self.date),
                         winner=self.winner.get().name,
                         loser=self.loser.get().name)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    grid_1 = messages.StringField(2, required=True)
    grid_2 = messages.StringField(3, required=True)
    ships_1 = messages.StringField(4, required=True)
    ships_2 = messages.StringField(5, required=True)
    user_1 = messages.StringField(6, required=True)
    user_2 = messages.StringField(7, required=True)
    next_move = messages.StringField(8, required=True)
    game_over = messages.BooleanField(9, required=True)
    winner = messages.StringField(10)


class GameForms(messages.Message):
    """Container for multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_1 = messages.StringField(1, required=True)
    user_2 = messages.StringField(2, required=True)

class InsertShipsForm(messages.Message):
    """Used to insert ships into a users grid prior to starting"""
    ship_type = messages.StringField(1, required=True)
    start_row = messages.IntegerField(2, required=True)
    start_column = messages.IntegerField(3, required=True)
    orientation = messages.StringField(4, required=True)

class InsertShipsForms(messages.Message):
    """Used for multiple insertships forms during ship insert"""
    ships = messages.MessageField(InsertShipsForm, 1, repeated=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    location = messages.IntegerField(2, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    date = messages.StringField(1, required=True)
    winner = messages.StringField(2, required=True)
    loser = messages.StringField(3, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """User Form for outbound user messages"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    total_played = messages.IntegerField(4, required=True)
    win_percentage = messages.FloatField(5, required=True)


class UserForms(messages.Message):
    """Container for multiple User Form messages"""
    items = messages.MessageField(UserForm, 1, repeated=True)

