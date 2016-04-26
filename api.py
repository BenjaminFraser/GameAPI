import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, GameForms, UserForm, UserForms, InsertShipsForms
from utils import get_by_urlsafe

# Fields for conference query options.
SHIP_TYPES =    [
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

INSERT_SHIPS_REQUEST = endpoints.ResourceContainer(
    InsertShipsForms,
    urlsafe_game_key=messages.StringField(1),)

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='battleships', version='v1')
class BattleshipsAPI(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
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
        """Return all Users ranked by their win percentage"""
        users = User.query(User.total_played > 0).fetch()
        users = sorted(users, key=lambda x: x.win_percentage, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
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
                      http_method='POST')
    def insert_user_1_ships(self, request):
        """Inserts user 1 ships into the Game grid 1"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            # retrieve multiple ship insert forms and format the data into
            # a dictionary with array values containing starting row, col and orientation.
            # ensure ships have not already been inserted.
            if game.total_ship_cells(grid=1) == 0:
                # uses _formatShipInsert helper function to validate 
                # and create the dictionary Python objects.
                try:
                    ship_data = self._formatShipInserts(request.ships)
                    game.insert_user_ships(ship_data)
                    game.put()
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
                      http_method='POST')
    def insert_user_2_ships(self, request):
        """Inserts user 2 ships into the Game grid 2"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            # retrieve multiple ship insert forms and format the data into
            # a dictionary with array values containing starting row, col and orientation.
            # ensure ships have not already been inserted.
            if game.total_ship_cells(grid=2) == 0:
                try:
                    ship_data = self._formatShipInserts(request.ships)
                    game.insert_user_2_ships(ship_data, user='user_2')
                    game.put()
                except Exception as e:
                    msg = e
                    raise endpoints.BadRequestException(msg)
                return StringMessage(message='Player 2 ships successfully added to grid.')
            else:
                raise endpoints.BadRequestException('Player 2 has already inserted ships!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    def _formatShipInserts(self, ships):
        """Parse, check validity and format ship insert data into an appropriate dict"""
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

            start_row, start_col = int(ship_data['start_row']), int(ship_data['start_column'])

            if ship_data['orientation'].lower().startswith('h'):
                vertical = False
            else: 
                # default to vertical orientation if horizontal not given.
                vertical = True

            # check the validity of the given ship data using _shipInsertPosnValid helper.
            check_ship, msg = self._shipInsertPosnValid(ship_type, start_row, 
                                                        start_col, vertical)
            if check_ship:
                formatted_ships[ship_type] = [start_row, start_col, vertical]
                # process the ship using the created class method for insertion of a ship.
            else:
                raise ValueError("There was a problem with a ship insert. {0}".format(msg))

        return formatted_ships

        # ensure that the ship insert data is within limits for each ship type and start locations.
        # create a helper function _shipInsertPosnValid(self, ship_type, start_row, start_col, orientation)

    def _shipInsertPosnValid(self, ship_type, first_row_int, first_col_int, vertical=True):
        """Checks the validatity of the ships starting co-ordinates and characteristics.
           returns a tuple, consisting of a retval and a message. 
                 - The retval is equal to True if the data is valid, and false if not.
                 - The message gives an indication as to the problem is retal is false.
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
                return True, message
            # if not set retval false and message for out of bounds input location.
            else:
                retval = False
                message = "{0} is size {1} and cannot fit there!".format(ship_type, size)
                return False, message
        elif vertical == False:
            # verify that horizontal location is within the grid limits.
            if int(first_col_int) < limit:
                retval, message = True, None
                return True, message
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
        """Return the current game state."""
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
        """Return all User's active games"""
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
        """Delete a game. Game must not have ended to be deleted"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.key.delete()
            return StringMessage(message='Game with key: {} deleted.'.
                                 format(request.urlsafe_game_key))
        elif game and game.game_over:
            raise endpoints.BadRequestException('Game is already over!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        if game.game_over:
            raise endpoints.NotFoundException('Game already over')

        user = User.query(User.name == request.user_name).get()
        if user.key != game.next_move:
            raise endpoints.BadRequestException('It\'s not your turn!')

        # User signifier. True if current user is player 1, otherwise False.
        user_1 = True if user.key == game.user_1 else False

        # set target grid to 2 if current user is user 1, and vice versa.
        if user_1 == True:
            target_grid = 2
        else:
            target_grid = 1

        row_loc, col_loc = int(request.target_row), int(request.target_col)
        # Verify move is valid
        if row_loc < 0 or row_loc > 9 or col_loc < 0 or col_loc > 9:
            raise endpoints.BadRequestException('Invalid move! Rows and columns must be '
                                                'between 0 and 9')

        if game.return_grid_status(row_loc, col_loc, target_grid) == 'X':
            raise endpoints.BadRequestException('That grid cell is already destroyed! '
                                                'Try picking another!')

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
        if winner_p2:
            game.end_game(game.user_2)
        else:
            # Send reminder email
            taskqueue.add(url='/tasks/send_move_email',
                          params={'user_key': game.next_move.urlsafe(),
                                  'game_key': game.key.urlsafe()})
        game.put()
        return game.to_form()

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a Game's move history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(ndb.OR(Score.winner == user.key,
                                    Score.loser == user.key))
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                        for game in games])
            average = float(total_attempts_remaining)/count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([BattleshipsAPI])