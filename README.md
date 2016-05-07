# Full Stack Nanodegree Project 4 - Battleships

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting your local server's address (by default localhost:8080.)
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
## Game Description:
Battleships is a simple two player game. Game instructions are available
[here](https://en.wikipedia.org/wiki/Battleship_(game)).

Each players grid is represented as a two dimensional list of 100 squares, consisting of 10 
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


 ## Game Instructions - with no Front-end client:
 In order to play a game of Battleships with no front-end client, you must use the Google App Engine API explorer to manually carry out game commands and functions. Once you have the API explorer up and running, carrying out the following actions:
 1. Create two new user profiles, using the create_user endpoint. Enter a unique player name and email for each user.
 2. Create a new game using the new_game endpoint and the two players names that are playing.
 3. Insert ships into both players grids, using the insert_user_1_ships and insert_user_2_ships endpoints. There is no mandatory number of ships that must be inserted, however player 1 and player 2 must have the same number of ships, and only 1 of each ship can be inserted into each grid. Ships must be placed within the grid boundaries (between rows 0-9 and columns 0-9), and cannot overlap any other ships on the grid. For each ship inserted, it must have:
    - An orientation field, which must be either 'vertical' or 'horizontal'
    - A ship type, which can be either 'aircraft carrier', 'battleship', 'destroyer', 'submarine' or 'patrol boat'
    - A first row, which is the very top ship cell row if vertical, or the very left cell row if horizontal
    - A first column, which is the very top ship cell column if vertical, or the very left cell column if horizontal
4. The game can now be started, with user 1 making a move using the make_move endpoint. The players name, along with target row and target column to attack must be entered in order to make a move. 
5. Players alternate turns using the make_move endpoint, until one player no longer has any ship cells remaining, at which point the game ends.


## Files Included:
 - api.py: Contains endpoints and game playing logic and functions.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including many helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.
 - design.txt: documentation explaining the design decisions made for the project.

## Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. `user_name` provided must be unique. Will 
    raise a ConflictException if a User with that `user_name` already exists.
    
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
    
 - **get_game_attacks**
    - Path: 'game/{urlsafe_game_key}/attacks'
    - Method: POST
    - Parameters: user_number
    - Returns: StringMessage
    - Description: Return a Game's grid attacks for both player 1 and player 2.

- **get_ships_remaining**
    - Path: 'games/ships_remaining'
    - Mathod: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Get the cached ships remaining for each current game in progress.

## Models Included:
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
    - Contains many class methods for game functionalities, including total ship counts, insertion of ships, updating grid values and checking for a winner. 

 - **Score**
    - Records completed games. Associated with Users model via KeyProperty as
    well.
    
## Forms Included:
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
    
    
## Design Decisions
- Creating a means to store a grid for each players battleships was an interesting choice, and I ended up choosing a PickleProperty. I chose this since it allowed me to store a two dimensional list, which was both a simple and an effective means of storing a grid state that changes after each turn. Through using a PickleProperty, it meant I could easily change the state of a grid cell(s) through using various Game class methods, which is a much easier approach than parsing a string representation of the same game grid. 
- Along with using next_move, user_1, user_2 and winner (all KeyProperty) to keep track of users and the next move, I also added a ships_1, ships_2, loc_ships_1 and loc_ships_2 to the Game model to help the game mechanics. The ships_1 and ships_2 fields are Python dictionaries that keep track of the current ships on a players field after each turn. Each dict key is a ship type, with an integer as its value, corresponding to how many of those ships there are currently on the players grid. loc_ships_1 and loc_ships_2 are both Python dictionaries that store the grid cells occupied by each ship type on a players grid. This design means that it is possible to work out whether a ship is partially destroyed, or completely destroyed from a players grid. The design of these four PickleProperty's could have been collated into 1 or 2 PickleProperty's through using a Python dict within a dict, however I decided that this adds too much complexity and potential for input error, so I decided against it and went with the simple approach.
- I made extensive use of Game class methods within `models.py`, rather than external helper functions within `api.py`. I decided to do this since it made applying changes and updates to my game fields much easier than it would have been querying the Datastore model each time in api.py. It also made my endpoints methods and helper functions within the `api.py` file more abstract and less prone to error, since they can carry out all game functionality using the Game class methods, rather than directly altering the game entities properties. 
- I created helper functions within `api.py` for inserting ships into a users battlegrid, as a means of making the endpoint method code much easier to understand and follow. 
- I made use of a 'game_over' flag to mark completed games in the Datastore.
- I modified the Score model to record which player won and lost each game, as a means of more easily obtaining user statistics.

The 1-d list to represent the board was the simplest solution I could think of, 
but it would make it very hard to scale the game to 4x4 or nxn versions of 
tic-tac-toe because there's no way to automatically partition each row with a 
1-d array. Also the winner checking logic is very hard-coded. 
I don't feel great about the logic to track which player's turn it is, 
but everything seems to work.

## Additional endpoints
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

 - **get_game_attacks**
    - Path: 'game/{urlsafe_game_key}/attacks'
    - Method: POST
    - Parameters: user_number
    - Returns: StringMessage
    - Description: Return a Game's grid attacks for both player 1 and player 2.

- **get_ships_remaining**
    - Path: 'games/ships_remaining'
    - Mathod: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Get the cached ships remaining for each current game in progress. This is carried out each time a player makes a game move within any game.