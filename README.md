TwingeBot-Proto
===============
A very simple proof-of-concept bot framework for bots similar to the late twingebot.

Dependencies
============
TwingeBot-Proto only needs Python 3 to run.

How To Use
==========
To create a new twingebot instance, simply use
```py
import twingebot
PORT = 6667
tbot = twingebot.TwingeBot('IRC_SERVER', PORT, 'NAME', 'OAUTH')
tbot.set_channels(['CHANNEL1', 'CHANNEL2', 'CHANNEL3'])
```
To add triggers to an instance, use `connect_regex`, `connect_command`, or `connect_timer`.
All `connect_*` commands can take a string or a function as their callback.
```py
def get_current_song(irc_dict):
    return "Unimplemented."

tbot.connect_command('sibg' get_current_song)
tbot.connect_regex('(hello|hi)', "Hello person.")
tbot.connect_timer(300, "Five minute timer.")
```
To run the bot, use `.run()`.
```py
tbot.run()
```
