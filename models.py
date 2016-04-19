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

    def total_ships(self, grid=1):
        """Return the total number of ships on the selected BattleGrid instance."""
        if grid is 1:
            return sum(self.ships_1.values())
        else:
            return sum(self.ships_2.values())

    def total_ship_cells(self, grid=1):
        """Returns the number of cells still intact with '+'"""
        ship_count = 0
        if grid is 1:
            for row in self.grid_1:
                ship_count += row.count('+')
        else:
            for row in self.grid_2:
                ship_count += row.count('+')
        return ship_count

    def total_destroyed_cells(self):
        """Returns the total number of cells that are destroyed ('X')"""
        destroy_count = 0 
        for row in self.board:
            destroy_count += row.count('X')
        return destroy_count

    def destroyed_locations(self):
        """Returns the locations of cells that are destroyed as a sequence
            of tuples containing their locations in the format:
            (row_number, column_number)
        """
        row_loc, col_loc = [], []
        for row_num, row in enumerate(self.board):
            for col_num, i in enumerate(row):
                if i == 'X':
                    # print "found an 'X' at location: row {0}, col {1}".format(row_num, col_num)
                    row_loc.append(row_num)
                    col_loc.append(col_num)
        locations = [list(x) for x in zip(row_loc, col_loc)]
        return locations

    def insert_user_1_ships(self, ships_dict_array):
        """Places user 1's ships throughout grid 1 within the
           selected cell co-ordinates and orientation (vert or horizontal).
           ships_array must be a dictionary with array values, providing the ships row,
           column and its orientation, in the format like the following example:
           ships_dict_array = {'Aircraft Carrier' : [2, 3, 'vertical=True']
                               'Battleship' : [4, 5, 'False']}
           The relevant data is passed forward into the place_ship function.
        """
        for ship, data in ships_dict_array:
            if ship is 'aircraft carrier':
                self.place_ship(5, data[0], data[1], vertical=data[2])
                self.ships_1['Aircraft Carrier'] += 1
            elif ship is 'battleship':
                self.place_ship(4, data[0], data[1], vertical=data[2])
                self.ships_1['Battleship'] += 1
            elif ship is 'submarine':
                self.place_ship(3, data[0], data[1], vertical=data[2])
                self.ships_1['Submarine'] += 1
            elif ship is 'destroyer':
                self.place_ship(3, data[0], data[1], vertical=data[2])
                self.ships_1['Destroyer'] += 1
            elif ship is 'patrol boat':
                self.place_ship(2, data[0], data[1], vertical=data[2])
                self.ships_1['Patrol boat'] += 1
            else:
                raise ValueError("The dict key does not match any ship types.")

    def insert_user_2_ships(self, ships_dict_array):
        """Places user 2's ships throughout grid 2 within the
           selected cell co-ordinates and orientation (vert or horizontal).
           ships_array must be a dictionary with array values, providing the ships row,
           column and its orientation, in the format like the following example:
           ships_dict_array = {'Aircraft Carrier' : [2, 3, 'vertical=True']
                               'Battleship' : [4, 5, 'False']}
           The relevant data is passed forward into the place_ship function.
        """
        for ship, data in ships_dict_array:
            if ship is 'aircraft carrier':
                self.place_ship(5, data[0], data[1], vertical=data[2], grid=2)
                self.ships_1['Aircraft Carrier'] += 1
            elif ship is 'battleship':
                self.place_ship(4, data[0], data[1], vertical=data[2], grid=2)
                self.ships_1['Battleship'] += 1
            elif ship is 'submarine':
                self.place_ship(3, data[0], data[1], vertical=data[2], grid=2)
                self.ships_1['Submarine'] += 1
            elif ship is 'destroyer':
                self.place_ship(3, data[0], data[1], vertical=data[2], grid=2)
                self.ships_1['Destroyer'] += 1
            elif ship is 'patrol boat':
                self.place_ship(2, data[0], data[1], vertical=data[2], grid=2)
                self.ships_1['Patrol boat'] += 1
            else:
                raise ValueError("The dict key does not match any ship types.")

    def place_ship(self, size, first_row_int, first_col_int, vertical=True, grid=1):
        """Places a ship of chosen size into the grid at the chosen co-ordinates,
        by default, the ship is placed vertically, with the given co-ords
        being the uppermost cell.
        If vertical=False, the ship is placed horizontally, starting from the
        left-most co-ordinates.
        """
        if vertical == True:
            for row in range(first_row_int, first_row_int+size):
                self.update_cell(row, first_col_int, grid=grid)
                return
                                
        if vertical == False:
            for col in range(first_col_int, first_col_int+size):
                self.update_cell(first_row_int, col, grid=grid)
                return

    def update_cell(self, row_int, col_int, status="ship", grid=1):
        """Update a cell at the chosen co-ordinates on the grid,
        Status may be: - "ship" (places a '+' on the cell)
                       - "destroy" (places an 'X' on the cell)
        """
        if grid == 1:
            if status == "ship":
                self.grid_1[row_int][col_int] = '+'
                return
            elif status == "destroy":
                # ensure the selected cell is not already destroyed, and update to 'X'
                if self.return_grid_status(row_int, col_int) != 'X':
                    self.grid_1[row_int][col_int] = 'X'
                    return
                # if the cell is already destroyed, raise ValueError notifying the user.
                else:
                    raise ValueError("The selected grid cell is already destroyed!")
            else:
                raise ValueError("The status argument must be either 'ship' or 'destroy'.")

        elif grid == 2:
            if status == "ship":
                self.grid_2[row_int][col_int] = '+'
                return
            elif status == "destroy":
                # ensure the selected cell is not already destroyed, and update to 'X'
                if self.return_grid_status(row_int, col_int) != 'X':
                    self.grid_2[row_int][col_int] = 'X'
                    return
                # if the cell is already destroyed, raise ValueError notifying the user.
                else:
                    raise ValueError("The selected grid cell is already destroyed!")
            else:
                raise ValueError("The status argument must be either 'ship' or 'destroy'.")

        else:
            raise ValueError("The selected grid must be either 1 or 2!")

    def destroy_cell(self, row_int, col_int, grid=1):
        """Destroys a selected grid cell, by inserting an "X".
        Returns True if a ship was present at the selected cell.
        """
        retval = False
        status = self.return_grid_status(row_int, col_int, grid=grid)
        if status == '+':
            retval = True
            self.update_cell(row_int, col_int, status="destroy", grid=grid)
            return retval

        if status == '-':
            self.update_cell(row_int, col_int, status="destroy", grid=grid)
            return retval

        # raise exception if grid cell is already destroyed.
        if status == 'X':
            raise ValueError('The chosen cell is already destroyed!')

    def return_grid_status(self, row_int, col_int, grid=1):
        """Return the status of a chosen grid cell,
        Returns: '-' for unoccupied,
        '+' for occupied by a ship,
        'x' for a destroyed cell.
        """
        if grid is 1:
            return self.grid_1[row_int][col_int]
        else:
            return self.grid_2[row_int][col_int]

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

