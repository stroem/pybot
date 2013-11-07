from bot import Ircbot

class MyBot(Ircbot):

    __commands = {}

    def __init__(self):
        super(MyBot, self).__init__(True)

        # switch for bot commands
        self.__commands = {
            'help': self.command_help,
            'echo': self.command_echo
        }

        self.set_nick("bettan3")
        self.set_realname("This is a great darn bot")

        self.connect("irc.chalmers.it")
        self.start()

    # commands
    def command_help(self, nick, channel, command, args):
        self.send(channel, "%s: No help yet (try !echo <message>)" % nick)

    def command_echo(self, nick, channel, command, args):
        if len(args) > 0:
            self.send(channel, "%s: %s" % (nick, args[0]))

    # definitions of callbacks
    def on_channel_failed(self, channel, modes):
        print "CHANNEL: failed to join channel %s: %s" % (channel, modes)

    def on_channel_joined(self, channel):
        print "CHANNEL: joined: %s" % channel

    def on_channel_nicklist(self, channel, nicklist):
        print "CHANNEL: nicklist for %s: %s" % (channel, ", ".join(nicklist))
    
    def on_motd_end(self):
        self.channel_join("#bottest3")

    def on_message(self, nick, channel, message):
        pass # called if it was written in the channel or private message

    def on_private_message(self, nick, message):
        self.send(nick, "No support for private messages")

    def on_channel_message(self, nick, channel, message):
        command = self.parse_command(message)
        if command:
            callback = self.__commands.get(command[0])
 
            # doesnt the command exist?
            if callback:
               callback(nick, channel, command[0], command[1:])
            else:
               pass # command not found
        else:
            # message for me (it isnt a command)
            if self.is_highlighted(self.get_nick(), message):
                self.send(channel, "%s: %s" % (nick, "Write !help for more info"))
            # message for someone other
            else: 
                pass

if __name__ == "__main__":
    MyBot()
