import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from models import User, Score
from models import StringMessage, MakeMoveForm,\
    ScoreForms, UserForm, UserForms, InsertShipsForms
from game_models import Game, GameForm, GameForms, NewGameForm
from utils import get_by_urlsafe

# Fields for conference query options.
SHIP_TYPES = [
            'aircraft carrier',
            'battleship',
            'submarine',
            'destroyer',
            'patrol boat'
            ]

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)

GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)

GRID_ATTACKS_REQUEST = endpoints.ResourceContainer(
    user_number=messages.StringField(1),
    urlsafe_game_key=messages.StringField(2),)

INSERT_SHIPS_REQUEST = endpoints.ResourceContainer(
    InsertShipsForms,
    urlsafe_game_key=messages.StringField(1),)

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2))

MEMCACHE_USER_SHIPS_REMAINING = 'SHIPS_REMAINING'


@endpoints.api(name='battleships', version='v1')
class BattleshipsAPI(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username, which is compared with the 
        pre-existing names stored in the database. If the name is already taken an 
        exception will be raised
        Args:
            request: the request object containing the chosen user name and email strings
        Returns:
            A StringMessage alerting the user that the user was successfully created
        Raises:
            endpoints.ConflictException
        """
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))


    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all Users ranked by their win percentage.
        Args:
            request: the request object
        Returns:
            A UserForms object contaning the indivual UserForm objects for each user
        """
        users = User.query(User.total_played > 0).fetch()
        users = sorted(users, key=lambda x: x.win_percentage, reverse=True)
        return UserForms(items=[user.to_form() for user in users])


    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game with the requested user 1 and user 2 names. Checks the 
            datastore to ensure players with those names specified exist. If an 
            input name does not correspond to a registered player an endpoints
            NotFoundException is raised.
        Args:
            request: contains the requested message, including user 1 and user 2 input names
        Returns:
            returns a gameform representation of the created game, using the game instance
            to_form() method.
        Raises:
            endpoints.NotFoundException:
        """
        user_1 = User.query(User.name == request.user_1).get()
        user_2 = User.query(User.name == request.user_2).get()
        if not user_1 and user_2:
            raise endpoints.NotFoundException(
                    'One of users with that name does not exist!')

        game = Game.new_game(user_1.key, user_2.key)

        return game.to_form()


    @endpoints.method(request_message=INSERT_SHIPS_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/user_1_ships',
                      name='user_1_ships',
                      http_method='PUT')
    def insert_user_1_ships(self, request):
        """Inserts user 1 ships into the Game entity grid 1 field. Takes in multiple
            Message objects through a GameForms request object. Makes use of the
            _formatShipInserts(ships) and game class insert_user_ships(ships) methods. 
            Raises an exception if no game is found, a player has already inserted ships
            or the ship insert data is invalid.
        Args:
            request: the request object containing the urlsafe_game_key and ship messages
                        within a GameForms object. 
        Returns:
            A StringMessage alerting the user that the ships were inserted.
        Raises:
            endpoints.BadRequestException
            endpoints.NotFoundException
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        # check game exists.
        if game:
            # ensure ships haven't already been added.
            if game.total_ship_cells(grid=1) == 0:
                # check validity of input ship data. Insert into game if valid.
                try:
                    ship_data = self._formatShipInserts(request.ships)
                    game.insert_user_ships(ship_data)
                    game.put()
                # raise exception with error message if the data is not valid.
                except Exception as e:
                    msg = e
                    raise endpoints.BadRequestException(msg)
                return StringMessage(message='Player 1 ships successfully added to grid.')
            else:
                raise endpoints.BadRequestException('Player 1 has already inserted ships!')
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=INSERT_SHIPS_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/user_2_ships',
                      name='user_2_ships',
                      http_method='PUT')
    def insert_user_2_ships(self, request):
        """Inserts user 2 ships into the Game entity grid 2 field. Takes in multiple
            Message objects through a GameForms request object. Makes use of the
            _formatShipInserts(ships) and game class insert_user_ships(ships) methods. 
            Raises an exception if no game is found, a player has already inserted ships
            or the ship insert data is invalid.
        Args:
            request: the request object containing the urlsafe_game_key and ship messages
                        within a GameForms object. 
        Returns:
            A StringMessage alerting the user that the ships were inserted.
        Raises:
            endpoints.BadRequestException
            endpoints.NotFoundException
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        # check game exists.
        if game:   
            # ensure ships haven't already been added.
            if game.total_ship_cells(grid=2) == 0:
                # check validity of input ship data. Insert into game if valid.
                try:
                    ship_data = self._formatShipInserts(request.ships)
                    game.insert_user_ships(ship_data, user='user_2')
                    game.put()
                # raise exception with error message if the data is not valid.
                except Exception as e:
                    msg = e
                    raise endpoints.BadRequestException(msg)
                return StringMessage(message='Player 2 ships successfully added to grid.')
            else:
                raise endpoints.BadRequestException('Player 2 has already inserted ships!')
        else:
            raise endpoints.NotFoundException('Game not found!')


    def _formatShipInserts(self, ships):
        """Parse, check validity and format ship insert data into an appropriate dict.
            Raises an exception if the ship type within the ships dict is incorrect, or
            if the position data within the dict is invalid.
        Args:
            ships: the requested ships MessageField object, containing multiple message fields 
                    for each input ship.
        Returns:
            The formatted ships in the form of a dictionary with ship type as the key, and
            a list for each key containing start_row int, start_col int and the boolean 
            vertical keyword, like the following example:
            { 'aircraft carrier' : [1, 2, vertical=True], ... }
        Raises:
            ValueError
            endpoints.BadRequestException
        """
        formatted_ships = {}

        for ship in ships:
            # create a dict containing all the input ship data for the ship.
            ship_data = {field.name: getattr(ship, field.name) for field in ship.all_fields()}
            # ensure the ship type entered is of a valid type.
            ship_type = ship_data['ship_type'].lower()

            if ship_type not in SHIP_TYPES:
                raise ValueError("Please enter a valid ship type. '{0}' is not valid! "
                                "A ship can be one of either: aircraft carrier, battleship, "
                                 "submarine, destroyer or a patrol boat!".format(ship_type))
            # ensure more than one ship type is not being inserted into the grid.

            if ship_type in formatted_ships:
                raise endpoints.BadRequestException('More than one ship type cannot be inserted! '
                            'You have tried to insert more than one {0}!'.format(ship_type))

            start_row, start_col = int(ship_data['start_row']), int(ship_data['start_column'])
            # check whether orientation is horizontal or vertical.
            if ship_data['orientation'].lower().startswith('h'):
                vertical = False

            else: 
                # default to vertical orientation if horizontal not given.
                vertical = True

            # check the validity of the given ship data using _shipInsertPosnValid helper.
            check_ship, msg = self._shipInsertPosnValid(ship_type, start_row, 
                                                        start_col, vertical)

            # format the ship dict as appropriate if the ship data is valid.
            if check_ship:
                formatted_ships[ship_type] = [start_row, start_col, vertical]

            else:
                raise ValueError("There was a problem with a ship insert. {0}".format(msg))

        return formatted_ships


    def _shipInsertPosnValid(self, ship_type, first_row_int, first_col_int, vertical=True):
        """Checks the validatity of the ships starting co-ordinates and characteristics.
           Returns a tuple, consisting of a retval and a message. retval is True to indicate
           valid position data, and is false when not, along with a message indicating why.
           Raises an exception if vertical is not True or False.
        Args:
            ship_type: The type of ship the user wants to insert. Must be of type str and
                        equal to either 'aircraft carrier', 'battleship', 'destroyer', 
                        'submarine' or 'battleship'
            first_row_int: An integer between 0-9, representing the first row the ship
                            shall occupy
            first_col_int: An integer between 0-9, representing the first column the ship
                            shall occupy
            vertical: Must be of type boolean and equal to True or False. True by default
        Returns:
            A tuple, consisting of two objects: retval and message:
                - The retval is equal to True if the data is valid, and false if not
                - The message gives an indication as to the problem if retval is false
        Raises:
            ValueError
        """
        if ship_type == 'aircraft carrier':
            limit, size = 5, 5
        elif ship_type == 'battleship':
            limit, size = 6, 4
        elif ship_type == 'submarine':
            limit, size = 7, 3
        elif ship_type == 'destroyer':
            limit, size = 7, 3
        elif ship_type == 'patrol boat':
            limit, size = 8, 2
        else:
            retval = False
            message = ("The input ship type {0} is not valid! Please use either "
                        "'aircraft carrier', 'battleship', 'submarine', 'destroyer' or "
                        "'patrol boat'!".format(ship_type))
            return retval, message

        if vertical == True:
            # verify that the ship will fit into the battle grid based on input.
            if int(first_row_int) < limit:
                retval, message = True, None
                return retval, message
            # if not set retval false and message for out of bounds input location.
            else:
                retval = False
                message = "{0} is size {1} and cannot fit there!".format(ship_type, size)
                return retval, message

        elif vertical == False:
            # verify that horizontal location is within the grid limits.
            if int(first_col_int) < limit:
                retval, message = True, None
                return retval, message
            # if not raise ValueError for out of bounds input horizontal location.
            else:
                retval = False
                message = "{0} is size {1} and cannot fit there!".format(ship_type, size)
                return retval, message

        else:
            # raise exception for incorrect vertical keyword if not true or false.
            raise ValueError("The 'vertical' keyword must be True or False!")


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state using the urlsafe_game_key. Raises an exception
            if the game cannot be found based on the urlsafe_game_key.
        Args:
            request: request object containing urlsafe_game_key
        Returns:
            A GameForm representation of the selected game
        Raises:
            endpoints.NotFoundException
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form()

        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all a selected User's active games. If no user is found
            within the database an endpoints exception is raised
        Args:
            request: request object containing user name and email input data
        Returns:
            GameForms message with all the queried user games as GameForm messages
        Raises:
            endpoints.BadRequestException
        """
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.BadRequestException('User not found!')
        games = Game.query(ndb.OR(Game.user_1 == user.key,
                                  Game.user_2 == user.key)).\
            filter(Game.game_over == False)
        return GameForms(items=[game.to_form() for game in games])


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Delete a game. Game must not have already ended in order to be deleted. Raises
            an endpoints exception if either the game is over or the game is not found.
        Args:
            request: request containing urlsafe_game_key
        Returns:
            A StringMessage informing deletion of the selected game
        Raises:
            endpoints.BadRequestException: game is already over.
            endpoints.NotFoundException: game not found.
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        # check to ensure the game is not already over.
        if game and not game.game_over:
            game.key.delete()
            return StringMessage(message='Game with key: {} deleted.'.
                                 format(request.urlsafe_game_key))

        elif game and game.game_over:
            raise endpoints.BadRequestException('Game is already over!')

        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move by updating the users attack on the opponents battlegrid. Returns a game 
            state with message based on outcome. Ends the game using the game method end_game() 
            if a user destroys all an opponents ships.
        Args: 
            request: contains the urlsafegamekey and MakeMoveForm user input data, which
                     consists of user_name, target_row and target_col
        Returns:
            A StringMessage indicating either the outcome of the attack or that the game is
            over.
        Raises:
            endpoints.NotFoundException
            endpoints.BadRequestException
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if not game:
            raise endpoints.NotFoundException('Game not found')

        # ensure the game is not already over.
        if game.game_over:
            raise endpoints.NotFoundException('Game already over')

        # ensure that ships have been inserted onto both grids prior to a move.
        if game.total_ships(grid=1) == 0 or game.total_ships(grid=2) == 0:
            raise endpoints.BadRequestException('Both users must have inserted ships '
                                                'prior to beginning the game.')

        # ensure the correct user is making a move.
        user = User.query(User.name == request.user_name).get()
        if user.key != game.next_move:
            raise endpoints.BadRequestException('It\'s not your turn!')

        # User signifier. True if current user is player 1, otherwise False.
        user_1 = True if user.key == game.user_1 else False

        # set target grid to 2 if current user is user 1, and vice versa.
        target_grid = 2 if user_1 else 1

        row_loc, col_loc = int(request.target_row), int(request.target_col)

        # Verify move is valid
        if row_loc < 0 or row_loc > 9 or col_loc < 0 or col_loc > 9:
            raise endpoints.BadRequestException('Invalid move! Rows and columns must be '
                                                'between 0 and 9')

        # check if grid cell is already destroyed.
        if game.return_grid_status(row_loc, col_loc, target_grid) == 'X':
            raise endpoints.BadRequestException('That grid cell is already destroyed! '
                                                'Try picking another!')

        # check whether the move was a hit or miss.
        target_hit = game.destroy_cell(row_loc, col_loc, grid=target_grid)

        # Append a move to the relevant history dict key dependent on user and hit status.
        history_msg = 'Ship hit!' if target_hit else 'No ship hit!'
        history_entry = (row_loc, col_loc, history_msg)
        game.history['grid_2' if user_1 else 'grid_1'].append(history_entry)

        # set next move within the game.
        game.next_move = game.user_2 if user_1 else game.user_1

        # check for any winners, end game and report winner if true.
        winner_p1, winner_p2 = game.check_winner()
        if winner_p1:
            game.end_game(game.user_1)
            game.put()
            return StringMessage(message='The game is over! {0} has won the match!'.
                                 format(game.user_1.get().name))

        if winner_p2:
            game.end_game(game.user_2)
            game.put()
            return StringMessage(message='The game is over! {0} has won the match!'.
                                 format(game.user_2))

        else:
            # Send reminder email
            taskqueue.add(url='/tasks/send_move_email',
                          params={'user_key': game.next_move.urlsafe(),
                                   'game_key': game.key.urlsafe()})

            # update memcache with user ships remaining
            taskqueue.add(url='/tasks/cache_ships_remaining',
                          params=None)

        target_hit_msg = 'You hit a ship! Well done!'
        target_miss_msg = 'No ship hit! Better luck next time!'

        # create a message to notify the player that they hit or missed.
        ret_msg = ("{0} You have now made the following moves: {1}. "
                        "{2} is up next!".format(target_hit_msg if target_hit else target_miss_msg,
                                                game.history['grid_2' if user_1 else 'grid_1'],
                                                game.next_move.get().name))
        
        game.put()
        return StringMessage(message=ret_msg)


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a Game's move history. The history is represented as a dict
            with two values: grid_1 and grid_2. Each grid has a sequence
            of tuples representing the moves carried out. Raises an endpoints exception
            if the game cannot be found.
        Args:
            request: request object containing urlsafe_game_key
        Returns:
            A StringMessage containing a string representation of the history dict
        Raises:
            endpoints.NotFoundException
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))


    @endpoints.method(request_message=GRID_ATTACKS_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/attacks',
                      name='get_game_attacks',
                      http_method='GET')
    def get_game_attacks(self, request):
        """Return a Game's grid attacks for both player 1 and player 2
        Args:
            request: a request object containing the urlsafegamekey and the grid attacks
                     request input data, consisting of user_number (1 or 2)
        Returns:
            A StringMessage that displays a string representation of the selected 
            users opponents game grid
        Raises:
            endpoints.BadRequestException
            endpoints.NotFoundException
        """
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        user_num = int(request.user_number)
        # verify requested user number is either 1 or 2.
        if user_num != 1 and user_num != 2:
            raise endpoints.BadRequestException('User number must be 1 or 2!')
        # set user grid as appropriate.
        grid = 'grid_2' if request.user_number == 1 else 'grid_1'
        if not game:
            raise endpoints.NotFoundException('Game not found')
        # format the grid strings so that no user ships are displayed, only attacks.
        shipfree_grid = str(getattr(game, grid)).replace('+', '-')
        msg = ("The enemy grid is currently like so: {0}".format(shipfree_grid))
        return StringMessage(message=msg)


    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores records for the game from Datastore. The results
            are unordered.
        Args: 
            request: the request object
        Returns:
            ScoreForms object, containing the individual score records from Datastore
        """
        return ScoreForms(items=[score.to_form() for score in Score.query()])


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores
        Args:
            request: the request object
        Returns:
            A ScoreForms object, containing the users individual ScoreForm messages
        Raises:
            endpoints.NotFoundException
        """
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(ndb.OR(Score.winner == user.key,
                                    Score.loser == user.key))
        return ScoreForms(items=[score.to_form() for score in scores])


    @endpoints.method(response_message=StringMessage,
                      path='games/ships_remaining',
                      name='get_ships_remaining',
                      http_method='GET')
    def get_ships_remaining(self, request):
        """Get the cached ships remaining for each current game
        Args:
            request: the request object
        Returns:
            A StringMessage object, containing the stored memcache entry or an empty
            string if no message exists.
        """
        return StringMessage(message=memcache.get(MEMCACHE_USER_SHIPS_REMAINING) or '')


    @staticmethod
    def _cache_ships_remaining():
        """Populates memcache with the number of ships remaining for both users
           of the current Games still in progress
        """
        games = Game.query(Game.game_over == False).fetch()
        if games:
            ship_game_data = []
            for game in games:
                websafe_game_key = game.key.urlsafe()
                ships_1, ships_2 = game.total_ships(grid=1), game.total_ships(grid=2)
                user_1, user_2 = game.user_1.get().name, game.user_2.get().name
                msg = ("Game key {0}, user 1 is {1} with {2} ships, user 2 is {3} "
                        "with {4} ships.".format(websafe_game_key, user_1, ships_1, user_2, ships_2))
                ship_game_data.append(msg)
            memcache.set(MEMCACHE_USER_SHIPS_REMAINING,
                         'The current games in progress, along with the number of ships '
                         'each user has is: {0}'.format('::'.join(ship_game_data)))


api = endpoints.api_server([BattleshipsAPI])