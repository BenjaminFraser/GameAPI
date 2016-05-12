from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile to store the details of each user registered.
    Attributes:
        name: The name of the user (str).
        email: The email address of the user (str).
        wins: The total games the user has won (int).
        total_played: The total games played by the user (int).
    """
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    wins = ndb.IntegerProperty(default=0)
    total_played = ndb.IntegerProperty(default=0)

    @property
    def win_percentage(self):
        """Returns the users win percentage calculated using wins and total_played.
        Returns:
            the win / total_played ratio as a float if a user has played at least 1 game,
            else returns 0.
        """
        if self.total_played > 0:
            return float(self.wins) / float(self.total_played)
        else:
            return 0

    def to_form(self):
        """Returns the user entity object as a UserForm message object suitable for 
        outbound messages.
        Returns:
            UserForm message containing the User entities name, email, wins, total played 
            and win percentage.
        """
        return UserForm(name=self.name,
                        email=self.email,
                        wins=self.wins,
                        total_played=self.total_played,
                        win_percentage=self.win_percentage)

    def add_win(self):
        """Add a to the users win property."""
        self.wins += 1
        self.total_played += 1
        self.put()

    def add_loss(self):
        """Add a loss to the user, by only incrementing total_played property."""
        self.total_played += 1
        self.put()


class Score(ndb.Model):
    """Score entity designed to store the results of a finished game.
    Attributes:
        date: The date of the game when it ended.
        winner: The username of the winner of the game.
        loser: The username of the looser of the game.
    """
    date = ndb.DateProperty(required=True)
    winner = ndb.KeyProperty(required=True)
    loser = ndb.KeyProperty(required=True)

    def to_form(self):
        """Returns the score entity as a ScoreForm message object suitable for 
        outbound messages.
        Returns:
            ScoreForm message containing the Score entity date, winner and loser 
            properties.
        """
        return ScoreForm(date=str(self.date),
                         winner=self.winner.get().name,
                         loser=self.loser.get().name)


class InsertShipsForm(messages.Message):
    """Used to insert ships into a users grid prior to starting. 
    Attributes:
        ship_type: The ship type to be inserted, as a string.
        start_row: An integer relating to the ship starting row.
        start_column: An integer relating to the ship starting column.
        orientation: The orientation of the ship as a string: 'horizontal' or 'vertical'
        """
    ship_type = messages.StringField(1, required=True)
    start_row = messages.IntegerField(2, required=True)
    start_column = messages.IntegerField(3, required=True)
    orientation = messages.StringField(4, required=True)


class InsertShipsForms(messages.Message):
    """Used for multiple insertships forms during ship insert"""
    ships = messages.MessageField(InsertShipsForm, 1, repeated=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game.
    Attributes:
        user_name: The users name who is making a game move.
        target_row: The chosen target row, as an int between 0-9.
        target_col: The chosen target column, as an int between 0-9.
    """
    user_name = messages.StringField(1, required=True)
    target_row = messages.IntegerField(2, required=True)
    target_col = messages.IntegerField(3, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information messages.
    Attributes:
        date: A string representation of the date of the game.
        winner: A string representation of the winner users name.
        loser: A string representation of the losers users name.
    """
    date = messages.StringField(1, required=True)
    winner = messages.StringField(2, required=True)
    loser = messages.StringField(3, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForm messages.
    Attributes:
        items: The ScoreForm messages, as a repeated property.
    """
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message.
    Attributes:
        message: The outbound message to be sent, as a string.
    """
    message = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """User Form for outbound user messages.
    Attributes:
        name: The name of the user as a string.
        email: The email of the user as a string.
        wins: User wins, as an int.
        total_played: User total played games, as an int.
        win_percentage: Users win percentage, as a float.
    """
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    total_played = messages.IntegerField(4, required=True)
    win_percentage = messages.FloatField(5, required=True)


class UserForms(messages.Message):
    """Container for multiple User Form messages.
    Attributes:
        items: The UserForm messages, as a repeated property.
    """
    items = messages.MessageField(UserForm, 1, repeated=True)
