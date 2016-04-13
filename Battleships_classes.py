# coding: utf-8

class BattleGrid(object):
		"""10 x 10 Grid container for users ship objects
		Built using an implemented 2-D listwith rows and cols.
		"""
		def __init__(self):
				self.rows = [y for y in range(10)]
				self.columns = [x for x in range(10)]
				self.board = [['-' for row in self.rows] for col in self.columns]
				self.ships = { 'Aircraft Carrier' : 0, 'Battleship' : 0,
											 'Submarine' : 0, 'Destroyer' : 0,
											 'Patrol boat' : 0 }
											 
											 
		def print_grid(self):
				"""Print the instantiated grid, with a new line for each row"""
				for r in self.board:
						print r
		
		
		def total_ships(self):
				"""Return the total number of ships on the selected BattleGrid instance."""
				return sum(test_grid.ships.values())
		
		
		def total_ship_cells(self):
				"""Returns the number of cells still intact with '+'"""
				ship_count = 0
				for row in self.board:
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
				
				
		def insert_ship(self, ship_type, first_row_int, first_col_int, vertical=True):
				"""Insert a chosen ship type into the battlegrid location."""
				if ship_type == 'aircraft carrier':
						if vertical == True: 
								# verify that the ship will fit into the battle grid based on input.
								if int(first_row_int) < 5:
										print "Creating and inserting an aircraft carrier."
										self.place_ship(5, int(first_row_int), int(first_col_int), vertical)
										self.ships['Aircraft Carrier'] += 1
										return
								# if not raise ValueError for out of bounds input location.
								else: 
										raise ValueError("The ships first row location must be below 5 to fit!")
						elif vertical == False:
								# verify that horizontal location is within the grid limits.
								if int(first_col_int) < 5:
										# place ship using place_ship() and add to self.ships dict value.
										self.place_ship(5, int(first_row_int), int(first_col_int), vertical=False)
										self.ships['Aircraft Carrier'] += 1
										return
								# if not raise ValueError for out of bounds input horizontal location.
								else:
										raise ValueError("The ships first column location must be below 5 to fit!")
						else:
								# raise exception for incorrect vertical keyword if not true or false.
								raise ValueError("The 'vertical' keyword must be True or False!")
				
				elif ship_type == 'battleship':
						if vertical == True: 
								if int(first_row_int) < 6:
										self.place_ship(4, int(first_row_int), int(first_col_int), vertical)
										self.ships['Battleship'] += 1
										return
								else: 
										raise ValueError("The ships first row location must be below 6 to fit!")
						elif vertical == False:
								if int(first_col_int) < 6:
										self.place_ship(4, int(first_row_int), int(first_col_int), vertical=False)
										self.ships['Battleship'] += 1
										return
								else:
										raise ValueError("The ships first column location must be below 6 to fit!")
						else:
								raise ValueError("The 'vertical' keyword must be True or False!")
					
				elif ship_type == 'submarine':
						if vertical == True: 
								if int(first_row_int) < 7:
										self.place_ship(3, int(first_row_int), int(first_col_int), vertical)
										self.ships['Submarine'] += 1
										return
								else: 
										raise ValueError("The ships first row location must be below 7 to fit!")					
						elif vertical == False:
								if int(first_col_int) < 7:
										self.place_ship(3, int(first_row_int), int(first_col_int), vertical=False)
										self.ships['Submarine'] += 1
										return
								else:
										raise ValueError("The ships first column location must be below 7 to fit!")
						
						else:
								raise ValueError("The 'vertical' keyword must be True or False!")
					
				elif ship_type == 'destroyer':
						if vertical == True: 
								if int(first_row_int) < 7:
										self.place_ship(3, int(first_row_int), int(first_col_int), vertical)
										self.ships['Destroyer'] += 1
										return
								else: 
										raise ValueError("The ships first row location must be below 7 to fit!")					
						elif vertical == False:
								if int(first_col_int) < 7:
										self.place_ship(3, int(first_row_int), int(first_col_int), vertical=False)
										self.ships['Destroyer'] += 1
										return
								else:
										raise ValueError("The ships first column location must be below 7 to fit!")
						else:
								raise ValueError("The 'vertical' keyword must be True or False!")
					
				elif ship_type == 'patrol boat':
						if vertical == True: 
								if int(first_row_int) < 8:
										self.place_ship(2, int(first_row_int), int(first_col_int), vertical)
										self.ships['Patrol boat'] += 1
										return
								else: 
										raise ValueError("The ships first row location must be below 8 to fit!")					
						elif vertical == False:
								if int(first_col_int) < 8:
										self.place_ship(2, int(first_row_int), int(first_col_int), vertical=False)
										self.ships['Patrol boat'] += 1
										return
								else:
										raise ValueError("The ships first column location must be below 8 to fit!")
						else:
								raise ValueError("The 'vertical' keyword must be True or False!")
				
				else:
						message = ("The input ship type {0} is not valid! Please use either "
											"'aircraft carrier', 'battleship', 'submarine', 'destroyer' or "
											"'patrol boat'!".format(ship_type))
						return message
						

		def place_ship(self, size, first_row_int, first_col_int, vertical=True):
				"""Places a ship of chosen size into the grid at the chosen co-ordinates,
				by default, the ship is placed vertically, with the given co-ords
				being the uppermost cell.
				If vertical=False, the ship is placed horizontally, starting from the
				left-most co-ordinates.
				"""
				if vertical == True:
						for row in range(first_row_int, first_row_int+size):
								self.update_cell(row, first_col_int)
						return
								
				if vertical == False:
						for col in range(first_col_int, first_col_int+size):
								self.update_cell(first_row_int, col)
						return


		def destroy_cell(self, row_int, col_int):
				"""Destroys a selected grid cell, by inserting an "X".
				Returns True if a ship was present at the selected cell.
				"""
				retval = False
				status = self.return_grid_status(row_int, col_int)
				if status == '+':
						retval = True
						self.update_cell(row_int, col_int, status="destroy")
						return retval

				if status == '-':
						self.update_cell(row_int, col_int, status="destroy")
						return retval

				# raise exception if grid cell is already destroyed.
				if status == 'X':
						raise ValueError('The chosen cell is already destroyed!')


		def update_cell(self, row_int, col_int, status="ship"):
				"""Update a cell at the chosen co-ordinates on the grid,
				Status may be: - "ship" (places a '+' on the cell)
											 - "destroy" (places an 'X' on the cell)
				"""
				if status == "ship":
						self.board[row_int][col_int] = '+'
						return
				elif status == "destroy":
						# ensure the selected cell is not already destroyed, and update to 'X'
						if self.return_grid_status(row_int, col_int) != 'X':
								self.board[row_int][col_int] = 'X'
								return
						# if the cell is already destroyed, raise ValueError notifying the user.
						else:
								raise ValueError("The selected grid cell is already destroyed!")
				else:
						raise ValueError("The status argument must be either 'ship' or 'destroy'.")


		def return_grid_status(self, row_int, col_int):
				"""Return the status of a chosen grid cell,
				Returns: '-' for unoccupied,
				'+' for occupied by a ship,
				'x' for a destroyed cell.
				"""
				return self.board[row_int][col_int]


# instantiate a dummy test grid.
test_grid = BattleGrid()
# place multiple test ships into some grid cells
test_grid.insert_ship('battleship', 2, 3)
test_grid.insert_ship('aircraft carrier', 8, 3, vertical=False)
test_grid.insert_ship('patrol boat', 3, 9)
test_grid.insert_ship('submarine', 0, 6, vertical=False)
test_grid.insert_ship('patrol boat', 9, 0, vertical=False)

print test_grid.return_grid_status(3, 3)

# print the test grid, with the added test ship.
test_grid.print_grid()

# test ship count method
print test_grid.total_ship_cells()

# test the destroy cell method:
test_grid.destroy_cell(3, 3)
test_grid.destroy_cell(4, 3)

print test_grid.return_grid_status(3, 3)

# ensure that ValueError is raised.
# test_grid.destroy_cell(3, 3)

print "The number of ships on the grid is:", sum(test_grid.ships.values())

# test ship count method
print "The total number of ship grid cells is {0}".format(test_grid.total_ship_cells())

# re-print the grid to reflect updates
test_grid.print_grid()

# test the destroyed cell counter method and location methods.
print "The number of total destroyed cells is: {0}".format(test_grid.total_destroyed_cells())
print "The locations of destroyed cells are: {0}".format(test_grid.destroyed_locations())
