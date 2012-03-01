#!/usr/bin/env python
# coding: utf-8
#
# Botos - a python jabber bot
#
# Based on the example jabber bot from Arthur Furlan <afurlan@afurlan.org>
# which ships with the python-jabberbot package
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.



from jabberbot import JabberBot, botcmd
from datetime import datetime
import logging
import re
import sys
import os
import subprocess
import argparse
import ConfigParser

class BotosBot(JabberBot):

    ''' Add features in JabberBot to allow it to handle specific
    caractheristics of multiple users chatroom (MUC). '''

    def __init__(self, *args, **kwargs):
        ''' Initialize variables. '''

        # answer only direct messages or not?
        self.only_direct = kwargs.get('only_direct', False)
        try:
            del kwargs['only_direct']
        except KeyError:
            pass

        # initialize jabberbot
        super(BotosBot, self).__init__(*args, **kwargs)
        hdlr = logging.FileHandler(botos_logfile)
        self.log.addHandler(hdlr) 
        self.log.setLevel(logging.ERROR)

        # create a regex to check if a message is a direct message
        user, domain = str(self.jid).split('@')
        self.direct_message_re = re.compile('^%s(@%s)?[^\w]? ' \
                % (user, domain))

    def callback_message(self, conn, mess):
        ''' Changes the behaviour of the JabberBot in order to allow
        it to answer direct messages. This is used often when it is
        connected in MUCs (multiple users chatroom). '''

        message = mess.getBody()
        if not message:
            return

        if self.direct_message_re.match(message):
            mess.setBody(' '.join(message.split(' ', 1)[1:]))
            return super(BotosBot, self).callback_message(conn, mess)
        elif not self.only_direct:
            return super(BotosBot, self).callback_message(conn, mess)


class CPU5Bot(BotosBot):

    @botcmd
    def date(self, mess, args):
        reply = datetime.now().strftime('%Y-%m-%d')
        self.send_simple_reply(mess, reply)

    @botcmd
    def bt(self, mess, args):
        '''main bot commands

            - bt yt <url>: title of the youtube video'''
        args = args.strip().split(' ')
        if len(args) < 1:
            return "No"     
        self.log.info("botos cmd")
        reply=botos_cmd(args)
        self.send_simple_reply(mess, reply)
        

def botos_cmd(args):
    if args[0] == "yt":
        if len(args) < 2:
            return "usage: bt yt <youtubeurl>"
        if not re.match("http://www.youtube.com/", args[1]):
            return "usage: bt yt <youtubeurl>"
        cmd='lynx -dump "%s" | head -5 | tr -d "\n" | cut -d"]" -f4 | cut -d"[" -f1 | tr -s " "' % args[1]
        cmdout=subprocess.check_output(cmd,shell=True)
        return "Title: %s" % cmdout.strip()

    return "blu"



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--conffile' , help='specify the config file')
    args = parser.parse_args()
    conffile=vars(args)['conffile']

    if not conffile:
        parser.print_help()
        sys.exit(1)
    if not os.path.isfile(conffile):
        print "File %s does not exist or is not readable" % conffile
        sys.exit(1)

    config = ConfigParser.RawConfigParser()
    config.read(conffile)
    try: 
        username = config.get('connection', 'username')
        password = config.get('connection', 'password')
        nickname = config.get('connection', 'nickname')
        chatroom = config.get('connection', 'chatroom')
        chatpass = config.get('connection', 'chatpass')
        botos_logfile = config.get('logging', 'logfile')
    except ConfigParser.NoSectionError as err:
        print "Error: %s " % err
        sys.exit(1)
    except ConfigParser.NoOptionError as err:
        print "Error: %s " % err
        sys.exit(1)

    mucbot = CPU5Bot(username, password, only_direct=False)
    mucbot.join_room(chatroom, nickname, chatpass)
    mucbot.serve_forever()
