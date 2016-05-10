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


class Score(ndb.Model):
    """Score object"""
    date = ndb.DateProperty(required=True)
    winner = ndb.KeyProperty(required=True)
    loser = ndb.KeyProperty(required=True)

    def to_form(self):
        return ScoreForm(date=str(self.date),
                         winner=self.winner.get().name,
                         loser=self.loser.get().name)


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
    target_row = messages.IntegerField(2, required=True)
    target_col = messages.IntegerField(3, required=True)


class GridAttackForm(messages.Message):
    """Used to request a users current attacks on an opponents grid"""
    user_number = messages.IntegerField(1, required=True)


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

