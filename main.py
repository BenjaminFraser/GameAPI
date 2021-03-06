#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import logging

import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from api import BattleshipsAPI
from utils import get_by_urlsafe

from models import User
from game_models import Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email who has
        games in progress. Email body includes a count of active games and their
        urlsafe keys
        Called every 12 hours using a cron job"""
        users = User.query(User.email != None)

        for user in users:
            games = Game.query(ndb.OR(Game.user_1 == user.key,
                                      Game.user_2 == user.key)). \
                filter(Game.game_over == False)
            if games.count() > 0:
                subject = 'This is a reminder!'
                body = 'Hello {}, you have {} games in progress. Their' \
                       ' keys are: {}'. \
                    format(user.name,
                           games.count(),
                           ', '.join(game.key.urlsafe() for game in games))
                logging.debug(body)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.
                               format(app_identity.get_application_id()),
                               user.email,
                               subject,
                               body)


class UpdateGameShipsRemaining(webapp2.RequestHandler):
    def post(self):
        """Update the ships remaining for users with current games in progress."""
        BattleshipsAPI._cache_ships_remaining()
        self.response.set_status(204)


class SendMoveEmail(webapp2.RequestHandler):
    def post(self):
        """Send an email to a User that it is their turn"""
        user = get_by_urlsafe(self.request.get('user_key'), User)
        game = get_by_urlsafe(self.request.get('game_key'), Game)
        subject = 'It\'s your turn!'
        body = '{}, It\'s your turn to play Battleships! The game key is: {}'. \
            format(user.name, game.key.urlsafe())
        logging.debug(body)
        mail.send_mail('noreply@{}.appspotmail.com'.
                       format(app_identity.get_application_id()),
                       user.email,
                       subject,
                       body)


app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_ships_remaining', UpdateGameShipsRemaining),
    ('/tasks/send_move_email', SendMoveEmail),
], debug=True)
