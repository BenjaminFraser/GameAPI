#Full Stack Nanodegree Project 4 - Battleships

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting your local server's address (by default localhost:8080.)
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
##Game Description:
Battleships is a simple two player game. Game instructions are available
[here](https://en.wikipedia.org/wiki/Battleship_(game)).

Each players grid is represented as a two dimensional array of 100 squares, consisting of 10 
rows and 10 columns. When initialised, the grid is as follows:

[['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], 
['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], 
['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], 
['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], 
['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], 
['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], 
['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], 
['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], 
['-', '-', '-', '-', '-', '-', '-', '-', '-', '-'], 
['-', '-', '-', '-', '-', '-', '-', '-', '-', '-']]

- Each cell is labelled as '-', which signifies an empty cell. 
- When a ship is inserted into the grid, it is represented by a series of cells marked as '+'.
- When a ship or grid cell is destroyed, it is labelled with a 'X'.
- A game is over once all of a players ship cells ('+') are replaced by an 'X'. The player who destroys
all of the opponents ships first is the winner of the match.

 There are five classes of ships a player may place on their grid:
 - Aircraft carrier: occupies 5 grid squares
 - Battleship: occupies 4 grid squares
 - Submarine: occupies 3 grid squares
 - Destroyer: occupies 3 grid squares
 - Patrol boat: occupies 2 grid squares

 Each ship is positioned onto a users grid prior to a game through entering 
 the starting location for the ship, using a starting row and starting column, 
 and is then positioned using the orientation field, by entering 'vertical' or
 'horizontal'.
 

##Files Included:
 - api.py: Contains endpoints and game playing logic and functions.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including many helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_1, user_2
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. `user_1` and `user_2` are the names of the
    two players, each of whom have a new grid 1 and grid 2 initialised for them
    respectively.

- **insert_user_1_ships**
    - Path: 'game/{urlsafe_game_key}/user_1_ships'
    - Method: POST
    - Parameters: urlsafe_game_key, insert ship data forms.
    - Returns: Message confirming the ship insertion.
    - Description: Inserts initial ships into the grid 1 battlegrid, prior to a 
    game beginning. The user may input a maximum of one of each ship type onto
    their grid, and ships must fit within the grid cells, and each ship must not
    conflict with the grid cells of any other ships.

- **insert_user_2_ships**
    - Path: 'game/{urlsafe_game_key}/user_2_ships'
    - Method: POST
    - Parameters: urlsafe_game_key, insert ship data forms.
    - Returns: Message confirming the ship insertion.
    - Description: Inserts initial ships into the grid 2 battlegrid, prior to a 
    game beginning. The user may input a maximum of one of each ship type onto
    their grid, and ships must fit within the grid cells, and each ship must not
    conflict with the grid cells of any other ships.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, user_name, target_row, target_col
    - Returns: Message confirming a hit, miss or ending of the game.
    - Description: Accepts an attack and returns the result of the attack.
    An attack is a row number from 0 - 9 and a column number from 0 - 9, corresponding 
    to one of the 100 possible grid cells on the opponents board.
    If this causes a game to end, a corresponding Score entity will be created listing
    the winner and looser of the game.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_active_game_count**
    NOT IMPLEMENTED
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    - Also keeps track of wins and total_played.
    
 - **Game**
    - Stores unique game states. Associated with User models via KeyProperties
    user_1 and user_2.
    - Stores information about each users game state using `ships` and `loc_ships`
    dictionaries for each user. `ships` stores the number of ships currently on the
    users battlegrid, whilst loc_ships dict stores the associated locations of these ships 
    using an array of tuples.

 - **Score**
    - Records completed games. Associated with Users model via KeyProperty as
    well.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, board,
    user_x, user_o, game_over, winner).
 - **NewGameForm**
    - Used to create a new game (user_x, user_o)
- **InsertShipsForm**
    - Used to insert a specified ship type into a battlegrid.
- **InsertShipsForms**
    - Creates a message consisting of multiple InsertShipsForm's.
 - **MakeMoveForm**
    - Inbound make move form (user_name, target_row, target_col).
 - **ScoreForm**
    - Representation of a completed game's Score (date, winner, loser).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **UserForm**
    - Representation of User. Includes winning percentage
 - **UserForms**
    - Container for one or more UserForm.
 - **StringMessage**
    - General purpose String container.
    
    
##Design Decisions
- I added a field to store the board in Game. I used PickleProperty because it allowed
me to store a Python List in the datastore which seemed like the simplest way
to record the state of the board.
- I also added next_move, user_x, user_o, and winner (all KeyProperty) to the Game
model to keep track of which User was either 'X' or 'O' and who's move it was.
- I used a 'game_over' flag as well to mark completed games.
- I modified the Score model to record which player won and lost each game.

The 1-d list to represent the board was the simplest solution I could think of, 
but it would make it very hard to scale the game to 4x4 or nxn versions of 
tic-tac-toe because there's no way to automatically partition each row with a 
1-d array. Also the winner checking logic is very hard-coded. 
I don't feel great about the logic to track which player's turn it is, 
but everything seems to work.

##Additional endpoints
 - **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms with 1 or more GameForm inside.
    - Description: Returns the current state of all the User's active games.
    
 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage confirming deletion
    - Description: Deletes the game. If the game is already completed an error
    will be thrown.
    
 - **get_user_rankings**
    - Path: 'user/ranking'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: Rank all players that have played at least one game by their
    winning percentage and return.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: StringMessage containing history dictionaries.
    - Description: Returns the move history of a game as a stringified dictionary,
    which contains two keys: grid_1 and grid_2. Each of these keys has an associated
    list of tuples detailing the game history in the form: 
    (row, col, hit_or_miss_message) 
    eg: { 'grid_1' : [(1, 3, 'You hit a ship!''), (5, 6, 'No ship hit!')], ..}