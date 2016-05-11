from protorpc import messages
from google.appengine.ext import ndb


class Game(ndb.Model):
    """Game object for storing each game within the database.
    Attributes:
        grid_1: A 2-D list representing user 1's 100 square grid. Stored as an
            NDB PickleProperty.
        grid_2: A 2-D list representing user 2's 100 square grid. Stored as an
            NDB PickleProperty.
        ships_1: A Python dict of the current ships on grid 1. NDB PickleProperty.
        ships_2: A Python dict of the current ships on grid 2. NDB PickleProperty.
        loc_ships_1: A python dict with the locations of current ships throughout grid 1, 
            stored as an NDB PickleProperty.
        loc_ships_2: A python dict with the locations of current ships throughout grid 2,
            stored as an NDB PickleProperty.
        next_move: The username who is to make a move next.
        user_1: The key corresponding to user 1's User key.
        user_2: The key corresponding to user 2's User key.
        game_over: Boolean True if the game is over, False if still in progress.
        winner: Stores the key corresponding to the winners User key when game ends.
        history: A dict that stores the history of moves throughout the game for both
            grid 1 and grid 2. Each grid is a dict key, and their values corresponding
            to a sequence of tuples detailing the move, like so: [row, column, hit or miss]
    """
    grid_1 = ndb.PickleProperty(required=True)
    grid_2 = ndb.PickleProperty(required=True)
    ships_1 = ndb.PickleProperty(required=True) # dict of user 1's current ships
    ships_2 = ndb.PickleProperty(required=True) 
    loc_ships_1 = ndb.PickleProperty(required=True) # locations of user 1's ships
    loc_ships_2 = ndb.PickleProperty(required=True)
    next_move = ndb.KeyProperty(required=True) # The User's whose turn it is
    user_1 = ndb.KeyProperty(required=True, kind='User')
    user_2 = ndb.KeyProperty(required=True, kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty()
    history = ndb.PickleProperty(required=True)

    @classmethod
    def new_game(cls, user_1, user_2):
        """Creates and returns a new game using two input username args as strings.
        Args:
            user_1 (str): The username of user_1.
            user_2 (str): The username of user_2.
        Returns:
            The created game object.
        """
        game = Game(user_1=user_1,
                    user_2=user_2,
                    next_move=user_1)
        # create an empty 10 x 10 grid and update grid 1 and 2.
        rows = [y for y in range(10)]
        columns = [x for x in range(10)]
        new_board = [['-' for row in rows] for col in columns]
        game.grid_1 = game.grid_2 = new_board
        # create a dict object with default 0 ships of each type.
        empty_ships = { 'aircraft carrier' : 0, 'battleship' : 0,
                        'submarine' : 0, 'destroyer' : 0,
                        'patrol boat' : 0 }
        # set user 1 and user 2 ships to the default
        game.ships_1 = game.ships_2 = empty_ships
        empty_locs = { 'aircraft carrier' : [], 'battleship' : [],
                        'submarine' : [], 'destroyer' : [],
                        'patrol boat' : [] }
        game.loc_ships_1 = game.loc_ships_2 = empty_locs
        # Set initial empty history dict for game.
        game.history = {'grid_1' : [], 'grid_2' : []}
        game.put()
        return game

    def total_ships(self, grid=1):
        """Return the total number of ships on the selected BattleGrid instance.
        Args:
            grid: Set to either 1 or 2, to indicate which grid is selected. 1 by default.
        Returns:
            An integer corresponding to the sum of the number of ships currently on the grid.
        """
        if grid is 1:
            # Sum of the ships dict values.
            return sum(self.ships_1.values())
        else:
            return sum(self.ships_2.values())

    def total_ship_cells(self, grid=1):
        """Returns the number of cells still intact with '+' as an integer.
        Args:
            grid: Set to either 1 or 2, to indicate which grid is selected. 1 by default.
        Returns:
            An integer corresponding to the total ship cells on the selected grid.
        """
        # set a ship cell counter to zero as default.
        ship_count = 0
        # set the ship grid accordingly.
        ship_grid = "grid_1" if grid == 1 else 'grid_2'
        # count the number of '+'s within each row.
        for row in getattr(self, ship_grid):
            ship_count += row.count('+')
        return ship_count

    def total_destroyed_cells(self, grid=1):
        """Returns the total number of cells that are destroyed ('X') as an integer.
        Args:
            grid: Set to either 1 or 2, to indicate which grid is selected. 1 by default.
        Returns:
            An integer corresponding to the number of destroyed cells in the selected grid.
        """
        # set the ship grid from the grid arg.
        ship_grid = "grid_1" if grid == 1 else 'grid_2'
        destroy_count = 0 
        for row in getattr(self, ship_grid):
            destroy_count += row.count('X')
        return destroy_count

    def destroyed_locations(self, grid=1):
        """Returns the locations of cells that are destroyed as a sequence
            of tuples containing their locations in the format:
            (row_number, column_number)
        Args:
            grid: Set to either 1 or 2, to indicate which grid is selected. 1 by default.
        Returns:
            A sequence of tuples that indicate the destroyed locations on the chosen grid, in the
            format: [(row_number, column_number), ..]
        """
        ship_grid = "grid_1" if grid == 1 else 'grid_2'
        row_loc, col_loc = [], []
        for row_num, row in enumerate(getattr(self, ship_grid)):
            for col_num, i in enumerate(row):
                if i == 'X':
                    row_loc.append(row_num)
                    col_loc.append(col_num)
        locations = [list(x) for x in zip(row_loc, col_loc)]
        return locations

    def insert_user_ships(self, ships_dict_array, user='user_1'):
        """Places user 1's ships throughout grid 1 within the selected cell co-ordinates 
            and orientation (vert or horizontal). The relevant data is passed forward 
            into the class function place_ship.
        Args:
            ships_dict_array (dict): a python dictionary with keys corresponding to 
                battleship ship types, and values in the form of a list with values
                providing the ships row, column and orientation, in the format:
                {'ship_type' : [row, col, vertical=True/False]}
            user: Should be equal to either 'user_1' or 'user_2'. 'user_1' by default.
        Raises:
            ValueError: the dict key does not match a valid ship type.
        """
        ship_grid = "ships_2" if user == 'user_2' else 'ships_1'
        grid = 2 if user == 'user_2' else 1
            # iterate through dict object using iteritems()
        for ship, data in ships_dict_array.iteritems():
            if ship == 'aircraft carrier':
                # place ship object onto the grid dependent on inputs.
                self.place_ship(ship, 5, data[0], data[1], vertical=data[2], grid=grid)
                # add the ship to the ships dict for that user.
                getattr(self, ship_grid)[ship] += 1
            elif ship == 'battleship':
                self.place_ship(ship, 4, data[0], data[1], vertical=data[2], grid=grid)
                getattr(self, ship_grid)[ship] += 1
            elif ship == 'submarine':
                self.place_ship(ship, 3, data[0], data[1], vertical=data[2], grid=grid)
                getattr(self, ship_grid)[ship] += 1
            elif ship == 'destroyer':
                self.place_ship(ship, 3, data[0], data[1], vertical=data[2], grid=grid)
                getattr(self, ship_grid)[ship] += 1
            elif ship == 'patrol boat':
                self.place_ship(ship, 2, data[0], data[1], vertical=data[2], grid=grid)
                getattr(self, ship_grid)[ship] += 1
            else:
                raise ValueError("The dict key does not match any ship types.")
        return

    def place_ship(self, ship_type, size, first_row_int, first_col_int, vertical=True, grid=1):
        """Places a ship of chosen size into the grid at the chosen co-ordinates.
            by default, the ship is placed vertically (vertical=True), with the given co-ords being the 
            uppermost cell.
        Args:
            ship_type (str): string corresponding to the type of ship. Must be a valid ship.
            size (int): Size of the ship, as an integer.
            first_row_int (int): Integer corresponding to the first row of the ship.
            first_col_int (int): Integer corresponding to the first column of the ship.
            vertical (Boolean): Boolean True for vertical, False for horizontal. If horizontal, the ship
                starting point is the left-most co-ordinate, and expands out to the right.
            grid (int): The grid the ship is to be placed into, either 1 or 2. 1 by default.
        """
        if vertical == True:
            for row in range(first_row_int, first_row_int+size):
                self.update_cell(row, first_col_int, grid=grid)
                # Add the ship locations to the relevant loc_ships dict
                self.update_ship_loc_values(ship_type, row, first_col_int, grid=grid)
            return
                                
        if vertical == False:
            for col in range(first_col_int, first_col_int+size):
                self.update_cell(first_row_int, col, grid=grid)
                # Add the ship locations to the relevant loc_ships dict
                self.update_ship_loc_values(ship_type, first_row_int, col, grid=grid)
            return

    def update_ship_loc_values(self, ship_type, row_int, col_int, grid=1, remove=False):
        """Updates the values of locations within loc_ships_1 or loc_ships_2.
            If a ship has been hit, the remove arg should be set to True.
        Args: 
            ship_type (str): the type of ship, as a string.
            row_int (int): The row of the grid cell as an integer.
            col_int (int): The column of the grid cell as an integer.
            remove (Boolean): Set to True if ship locations are to be removed, else False
                by default.
        Raises:
            ValueError: incorrect co-ordinates, grid or ship type.
        """ 
        if not remove:
            if grid == 1:
                # append the cell co-ordinate to the relevant key of the loc dict.
                self.loc_ships_1[ship_type].append((row_int, col_int))
                return
            elif grid == 2:
                self.loc_ships_2[ship_type].append((row_int, col_int))
                return
            else:
                # raise error if grid is anything other than 1 or 2.
                raise ValueError("The grid must be 1 or 2.")

        if remove:
            # if ship type is unknown, search the ship loc dict and find co-ordinates.
            if grid == 1 and ship_type == 'unknown':
                found = False
                for ship, locations in self.loc_ships_1.iteritems():
                    if (row_int, col_int) in locations:
                        self.loc_ships_1[ship].remove((row_int, col_int))
                        if len(self.loc_ships_1[ship]) == 0:
                            # update the ships dict to indicate destruction of the ship.
                            self.ships_1[ship] -= 1
                        return
                if found == False:
                        raise ValueError("Those co-ordinates are not in the ship loc 1 dict!")

            elif grid == 2 and ship_type == 'unknown':
                found = False
                for ship, locations in self.loc_ships_2.iteritems():
                    if (row_int, col_int) in locations:
                        found = True
                        self.loc_ships_2[ship].remove((row_int, col_int))
                        if len(self.loc_ships_2[ship]) == 0:
                            # update the ships dict to indicate destruction of the ship.
                            self.ships_2[ship] -= 1
                        return
                if found == False:
                        raise ValueError("Those co-ordinates are not in the ship loc 2 dict!")

            else:
                raise ValueError("The ship type is always 'unknown' during removal.")

    def update_cell(self, row_int, col_int, status="ship", grid=1):
        """Update a cell at the chosen co-ordinates on the grid with either a 
            ship ('+') or a destroy signal ('X'). Raises an exception if incorrect
            data is provided.
        Args:
            row_int (int): the row of the chosen cell, as an integer.
            col_int (int): the column of the chosen cell, as an integer.
            status: Set to 'ship' to place a '+' on the cell by default. If a cell is 
                to be destroyed, status should be equal to 'destroy' to place an 'X'
                on the cell.
            grid (int): The grid number corresponding to the selected grid. 1 (default) or 2.
        Raises:
            ValueError: grid already destroyed, incorrect status or incorrect grid.
        """
        if grid == 1:
            if status == "ship":
                # add a '+' to the selected cell.
                self.grid_1[row_int][col_int] = '+'
                return
            elif status == "destroy":
                # ensure the selected cell is not already destroyed, and update to 'X'
                if self.return_grid_status(row_int, col_int, grid=grid) != 'X':
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
                if self.return_grid_status(row_int, col_int, grid=grid) != 'X':
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
        """Destroys a selected grid cell, by inserting an "X". Returns True if a ship
            was present at the selected cell.
        Args:
            row_int (int): the row of the chosen cell, as an integer.
            col_int (int): the column of the chosen cell, as an integer.
            grid (int): The grid number corresponding to the selected grid. 1 (default) or 2.
        Returns:
            a retval, which is True if a ship cell was destroyed, and False if not.
        Raises:
            ValueError: chosen cell already destroyed.
        """
        retval = False
        status = self.return_grid_status(row_int, col_int, grid=grid)
        if status == '+':
            # set the retval to True, indicating the attack as a successful hit.
            retval = True
            # Update the cell to display an 'X' using update_cell() method.
            self.update_cell(row_int, col_int, status="destroy", grid=grid)
            # Update the ship location dictionary, removing the relevant co-ordinates.
            self.update_ship_loc_values('unknown', row_int, col_int, grid=grid, remove=True)
            return retval

        if status == '-':
            self.update_cell(row_int, col_int, status="destroy", grid=grid)
            return retval

        # raise exception if grid cell is already destroyed.
        if status == 'X':
            raise ValueError('The chosen cell is already destroyed!')

    def return_grid_status(self, row_int, col_int, grid=1):
        """Return the status of a chosen grid cell as either unoccupied, destroyed or
            occupied by a ship.
        Args:
            row_int (int): the row of the chosen cell, as an integer.
            col_int (int): the column of the chosen cell, as an integer.
            grid (int): The grid number corresponding to the selected grid. 1 (default) or 2.
        Returns:
            '+' if the cell is occupied by a ship, and 'X' if a cell is destroyed, and
            '-' if a cell is unoccupied.
        """
        if grid is 1:
            return self.grid_1[row_int][col_int]
        else:
            return self.grid_2[row_int][col_int]

    def check_winner(self):
        """Check both battle grids. If there is a winner, report that user_win as True.
           Returns two values: user_1_win and user_2_win.
        Returns:
            A tuple that contains two Boolean values: user_1_win and user_2_win. If there
            is no winner and the game is still in progress, both values will equal False. 
            If there is a winner, that user's value (user_1_win or user_2_win) will be 
            equal to True.
        Example:
            If user 1 had won the game, the function would return: (True, False)
        """
        # Check both grids total ship cells remaining.
        ship_cells_1 = self.total_ship_cells(grid=1)
        ship_cells_2 = self.total_ship_cells(grid=2)

        # set both users to False by default.
        user_1_win, user_2_win = False, False

        if ship_cells_1 == 0:
            # user 1 has lost the game. Report user 2 as winner by returning user_2 = True.
            user_1_win = True

        if ship_cells_2 == 0:
            # user 2 has lost the game. Report user 1 as winner by returning user_1 = True.
            user_2_win = True

        return (user_1_win, user_2_win)

    def to_form(self):
        """Returns a GameForm representation of the Game.
        Returns:
            A GameForm message that contains all of the game entities properties 
            in a suitable format for an outbound message.
        """
        form = GameForm(urlsafe_key=self.key.urlsafe(),
                        grid_1 = str(self.grid_1),
                        grid_2 = str(self.grid_2),
                        ships_1 = str(self.ships_1),
                        ships_2 = str(self.ships_2),
                        loc_ships_1 = str(self.loc_ships_1),
                        loc_ships_2 = str(self.loc_ships_2),
                        user_1=self.user_1.get().name,
                        user_2=self.user_2.get().name,
                        next_move=self.next_move.get().name,
                        game_over=self.game_over)
        if self.winner:
            form.winner = self.winner.get().name
        return form

    def end_game(self, winner):
        """Ends the game using the winners username (str) as an argument. Sets the 
        current games property game_over to True, to indicate the game is over.
        Args:
            winner (str): The username of the winner.
        """
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


class GameForm(messages.Message):
    """GameForm for outbound game state information.
    Attributes:
        urlsafe_key: A urlsafe string representation of the Game entity key.
        grid_1: A string representation of user 1's grid state.
        grid_2: A string representation of user 2's grid state.
        ships_1: A string representation of ships_1 dictionary.
        ships_2: A string representation of ships_2 dictionary.
        loc_ships_1: A string representation of loc_ships_1 dictionary.
        loc_ships_2: A string representation of loc_ships_2 dictionary.
        user_1: The name of user 1, as a string.
        user_2: The name of user 2, as a string.
        next_move: The name of the next player to take a turn, as a string.
        game_over: True if the game is over, else False.
        winner: The name of the winner, if the game is over.
    """
    urlsafe_key = messages.StringField(1, required=True)
    grid_1 = messages.StringField(2, required=True)
    grid_2 = messages.StringField(3, required=True)
    ships_1 = messages.StringField(4, required=True)
    ships_2 = messages.StringField(5, required=True)
    loc_ships_1 = messages.StringField(6, required=True)
    loc_ships_2 = messages.StringField(7, required=True)
    user_1 = messages.StringField(8, required=True)
    user_2 = messages.StringField(9, required=True)
    next_move = messages.StringField(10, required=True)
    game_over = messages.BooleanField(11, required=True)
    winner = messages.StringField(12)


class GameForms(messages.Message):
    """Container for multiple GameForm.
    Attributes:
        items: The GameForm messages, as a repeated property.
    """
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game using two selected user names.
    Attributes:
        user_1: The selected username for user 1 as a string.
        user_2: The selected username for user 2 as a string.
    """
    user_1 = messages.StringField(1, required=True)
    user_2 = messages.StringField(2, required=True)