#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import socket

class Ircbot(object):

    __debugging = True
    __admin = None

    __nick = "unknown"
    __password = None
    __ident = "banned"
    __realname = "None"
    __usermode = 0

    __connected = False

    def __init__(self, debugging=True):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__debugging = debugging

    def set_admin(self, admin):
        self.__admin = admin

    def set_ident(self, ident):
        self.__ident = ident

    def get_ident(self, ident):
        return self.__ident

    def set_nick(self, nick):
        self.__nick = nick

    def get_nick(self):
        return self.__nick

    def set_realname(self, realname):
        self.__realname = realname

    def get_realname(self):
        return self.__realname

    def send_socket(self, message):
        #if self.__debugging:
        #    print message

        self.__sock.send("%s\n" % message)

    # irc commands
    def connect(self, host, port=6667):
        self.__sock.connect((host, port))
        if self.__password:
            self.send_socket("PASS %s" % self.__password)

        self.send_socket("NICK %s" % self.__nick)
        self.send_socket("USER %s %s * :%s" % (self.__ident, self.__usermode, self.__realname))
        
        self.__connected = True

    def disconnect(self):
        if self.__connected:
            self.__sock.close()
            self.__connected = False
            return True

        return False

    def send_privmsg(self, nick, msg):
        self.send(nick, msg)

    def send(self, channel, msg):
        self.send_socket("PRIVMSG %s :%s" % (channel, msg))

    def channel_join(self, channel):
        self.send_socket("JOIN %s" % channel)

    def channel_part(self, channel, reason=""):
        self.send_socket("PART %s :%s" % (channel, reason))

    def quit(self, reason=""):
        self.send_socket("QUIT :%s" % reason);

    # callbacks
    def on_motd_end(self): pass

    def on_channel_nicklist(self, channel, nicklist): pass
    def on_channel_joined(self, channel): pass
    def on_channel_failed(self, channel, modes): pass
    def on_channel_message(self, nick, channel, message): pass

    def on_private_message(self, nick, message): pass
    def on_message(self, nick, channel, message): pass
    def on_ping(self, randomstring): pass

    # helper functions
    def is_highlighted(self, nick, message):
        return message[:len(nick)+2] == "%s: " % nick 

    def filter_highlight(self, message):
        if self.is_highlighted(self.__nick, message):
            return message[len(self.__nick)+2:]

        return message

    def parse_command(self, message, prefix="!"):
        command = self.filter_highlight(message).split(" ")

        if len(command) > 0 and len(command[0]) > len(prefix):
            if command[0][:len(prefix)] == prefix:
                command[0] = command[0][len(prefix):]
                return command

        return None

    # main loop
    def start(self):
        running = True

        while running:
            ircmsg = self.__sock.recv(2048)
            ircmsg = ircmsg.strip('\n\r')

            for msg in ircmsg.split("\n"):

                if self.__debugging:
                    print("%s\n" % ircmsg)

                code = None
                data = None

                matches = re.match(":.+ (\d+) (.+)", msg)
                if matches:
                    code = int(matches.group(1))
                    data = matches.group(2)

                try:
                    if len(msg) > 0:
                        self.__parse_irc(code, data, msg)
                except Exception, e:
                    if self.__admin and self.__debugging:
                        if self.__connected:
                            self.send_privmsg(self.__admin, e)
                        else:
                            print("Error: %s" % e)

    def __parse_irc(self, code, data, ircmsg):
        if code == 376: #ircmsg.find(':End of /MOTD command') != -1:
            self.on_motd_end()

        if code == 474:
            matches = re.match(":.+ \d+ .+ (#.+) :Cannot join channel \((.*)\)", ircmsg)
            channel = matches.group(1)
            modes = matches.group(2)
            self.on_channel_failed(channel, modes)

        if code == 353:
            matches = re.match(":.+ \d+ .+ = (#.+) :(.+)", ircmsg)
            channel = matches.group(1)
            nicklist = matches.group(2).split(" ")
            nicklist = filter(lambda nick: len(nick) > 1, nicklist)
            self.on_channel_nicklist(channel, nicklist)

        if code == 366:
            channel = ircmsg.split("#")[1][:-21]
            self.on_channel_joined("#%s" % channel)

        if ircmsg.find(' PRIVMSG ') != -1:
            nick = ircmsg.split('!')[0][1:]
            channel = ircmsg.split(' PRIVMSG ')[-1].split(' :')[0]
            message = ircmsg.split(' PRIVMSG ')[-1].split(' :')[1]

            if channel == self.__nick:
                self.on_private_message(nick, message)
            else:
                self.on_channel_message(nick, channel, message)

            self.on_message(nick, channel, message)

        if ircmsg[:4] == "PING":
            randomstring = ircmsg.split(':')[1]
            self.send_socket("PONG :%s\r\n" % randomstring)
            self.on_ping(randomstring)
