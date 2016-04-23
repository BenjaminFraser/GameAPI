    def _shipInsertPosnValid(self, ship_type, first_row_int, first_col_int, vertical=True):
        """Checks the validatity of the ships starting co-ordinates and characteristics.
           returns a tuple, consisting of a retval and a message. 
                 - The retval is equal to True if the data is valid, and false if not.
                 - The message gives an indication as to the problem is retal is false.
        """

        if ship_type == 'aircraft carrier':
            if vertical == True: 
                # verify that the ship will fit into the battle grid based on input.
                if int(first_row_int) < 5:
                        retval, message = True, None
                        return True, message
                # if not set retval false and message for out of bounds input location.
                else: 
                        retval = False
                        message = "Aircraft carrier is size 5 and cannot fit there!"
                        return False, message
            elif vertical == False:
                # verify that horizontal location is within the grid limits.
                if int(first_col_int) < 5:
                    retval, message = True, None
                    return True, message
                # if not raise ValueError for out of bounds input horizontal location.
                else:
                    retval = False
                    message = "Aircraft carrier is size 5 and cannot fit there!"
                    return retval, message
            else:
                # raise exception for incorrect vertical keyword if not true or false.
                raise ValueError("The 'vertical' keyword must be True or False!")
                
        elif ship_type == 'battleship':
            if vertical == True: 
                if int(first_row_int) < 6:
                    retval, message = True, None
                    return True, message
                else:
                    retval = False
                    message = "The battleships first row must be below 6 to fit vertically!"
                    return retval, message
            elif vertical == False:
                if int(first_col_int) < 6:
                    retval, message = True, None
                    return True, message
                else:
                    retval = False
                    message = "The battleships first column must be below 6 to fit horizontally!"
                    return retval, message
            else:
                raise ValueError("The 'vertical' keyword must be True or False!")
                    
        elif ship_type == 'submarine':
            if vertical == True: 
                if int(first_row_int) < 7:
                    retval, message = True, None
                    return True, message
                else:
                    retval = False
                    message = "The submarines first row must be below 7 to fit vertically!" 
                    return retval, message                
            elif vertical == False:
                if int(first_col_int) < 7:
                    retval, message = True, None
                    return True, message
                else:
                    retval = False
                    message = "The submarines first column must be below 7 to fit horizontally!"
                    return retval, message    
            else:
                raise ValueError("The 'vertical' keyword must be True or False!")
                    
        elif ship_type == 'destroyer':
            if vertical == True: 
                if int(first_row_int) < 7:
                    retval, message = True, None
                    return True, message
                else: 
                    retval = False
                    message = "The destroyers first row must be below 7 to fit vertically!" 
                    return retval, message                  
            elif vertical == False:
                if int(first_col_int) < 7:
                    retval, message = True, None
                    return True, message
                else:
                    retval = False
                    message = "The destroyers first column must be below 7 to fit horizontally!"
                    return retval, message
            else:
                raise ValueError("The 'vertical' keyword must be True or False!")
                    
        elif ship_type == 'patrol boat':
            if vertical == True: 
                if int(first_row_int) < 8:
                    retval, message = True, None
                    return True, message
                else:
                    retval = False
                    message = "The patrol boats first row must be below 8 to fit vertically!"
                    return retval, message                   
            elif vertical == False:
                if int(first_col_int) < 8:
                    retval, message = True, None
                    return True, message
                else:
                    retval = False
                    message = "The patrol boats first column must be below 8 to fit horizontally!"
                    return retval, message
            else:
                raise ValueError("The 'vertical' keyword must be True or False!")

        else:
            retval = False
            message = ("The input ship type {0} is not valid! Please use either "
                        "'aircraft carrier', 'battleship', 'submarine', 'destroyer' or "
                        "'patrol boat'!".format(ship_type))
            return retval, message