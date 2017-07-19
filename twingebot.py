import twitchirc
import asyncio
import re
import traceback

class TwingeBot(twitchirc.TwitchIrc):
    def __init__(self, host, port, nick, password, **params):
        super(TwingeBot, self).__init__(host, port, nick, password, **params)
        self.channels = list()
        self.commands = dict()
        self.regexes = list()

    def run(self):
        super(TwingeBot, self).run()
        print("Disconnected from chat.")

    async def on_welcome(self, irc_dict):
        print("connected to twitch IRC")
        # Join all channels
        for channel in self.channels:
            self.send_join(channel)

    async def on_privmsg(self, irc_dict):
        # Check number of args to make sure we have both
        # channel and message
        arguments = irc_dict['arguments']
        if len(arguments) < 2:
            return
        channel = arguments[0]
        message = arguments[1]

        # Is this potentially a command?
        if message.startswith('!'):
            # Returns true if we should stop processing
            if self.on_command(channel, message, irc_dict):
                return

        # Does this match a regex?
        for regex, func in self.regexes:
            if regex.search(message):
                try:
                    # Get the response to the trigger
                    response = func(irc_dict)
                    self.send_privmsg(channel, response)
                except Exception as e:
                    # Don't die if the command had an exception.
                    # It should actually mostly be fine.
                    # Instead, print out what went wrong.
                    traceback.print_exc()
                return

    def on_command(self, channel, message, irc_dict):
        # TODO: Possibly extract arguments for the command?
        command = message[1:].split(' ', 1)[0]
        try:
            func = self.commands[command]
        except KeyError:
            return False 

        try:
            # Get the response to the command
            response = func(irc_dict)
            self.send_privmsg(channel, response)
        except Exception as e:
            # Don't die if the command had an exception.
            # It should actually mostly be fine.
            # Instead, print out what went wrong.
            traceback.print_exc()
        return True

    async def timer(self, seconds, func):
        while True:
            await asyncio.sleep(seconds)
            try:
                # Get the response to the trigger
                response = func()
                # Send response to all channels
                for channel in self.channels:
                    self.send_privmsg(channel, response)
            except Exception as e:
                # Don't die if the command had an exception.
                # It should actually mostly be fine.
                # Instead, print out what went wrong.
                traceback.print_exc()

    def set_channels(self, channels):
        self.channels = channels

    def connect_command(self, command, func):
        if isinstance(func, str):
            func = string_func_helper(func)
        self.commands[command] = func

    def connect_regex(self, regex_str, func, flags=0):
        if isinstance(func, str):
            func = string_func_helper(func)
        # TODO: Allow regex flags for better regexes
        regex = re.compile(regex_str, flags)
        self.regexes.append((regex, func))

    def connect_timer(self, seconds, func):
        if isinstance(func, str):
            func = string_func_helper(func)
        asyncio.ensure_future(self.timer(seconds, func))

def string_func_helper(string):
    def return_string(*params):
        return string
    return return_string

# Custom stuff below

def get_current_song(unused_irc_dict):
    # Do some stuff here
    song = 'There is no song currently playing.'
    return song

if __name__ == '__main__':
    # Create a new twingebot
    twingebot = TwingeBot('irc.twitch.tv', 6667, 'twingebot', 'OAUTH HERE')
    # Takes in a list (aka array). channel names should be lowercase and start with a '#'
    twingebot.set_channels(['#darktwinge'])
    # Second arguments can also be a function if wanted
    twingebot.connect_command('sibg', get_current_song)
    twingebot.connect_regex('so much for heroes', 'Something something so much for heroes.')
    # Timer is in seconds (Can be a decimal value)
    twingebot.connect_timer(10, "Follow Like Subscribe.")
    # Run the bot
    twingebot.run()
