import asyncio

class TwitchIrc(object):
    def __init__(self, host, port, nick, password, **params):
        self.host = host
        self.port = port
        self.nick = nick
        self.password = password

        if 'loop' in params:
            self.loop = params.loop
        else:
            self.loop = asyncio.get_event_loop()

        self.reader = None
        self.writer = None
        self.buf = bytearray()

    def run(self):
        self.loop.run_until_complete(self.start_bot())

    async def start_bot(self):
        await self.connect()
        await self.process()

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self.send_raw('CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership')
        self.send_pass(self.password)
        self.send_nick(self.nick)

    async def process(self):
        while True:
            new_data = await self.reader.read(4096)
            if not new_data:
                return
            self.buf += new_data
            while b'\r\n' in self.buf:
                irc_line = self.buf.partition(b'\r\n')
                await self.process_line(irc_line[0])
                self.buf = irc_line[2]

    async def process_line(self, irc_line):
        irc_str = irc_line.decode('utf-8')
        irc_dict = dict()

        if irc_str.startswith('@'):
            temp = irc_str.partition(' ')
            twitch_str = temp[0][1:]

            twitch_map = dict()
            for key_value in twitch_str.split(';'):
                key, _, value = key_value.partition('=')
                twitch_map[key] = value
            irc_dict['twitch'] = twitch_map

            irc_str = temp[2]

        if irc_str.startswith(':'):
            temp = irc_str.partition(' ')
            irc_dict['from'] = temp[0][1:]
            irc_str = temp[2]

        temp = irc_str.partition(' ')
        irc_dict['command'] = temp[0]
        irc_str = temp[2]

        irc_dict['arguments'] = list()
        while irc_str:
            temp = irc_str.partition(' ')
            if temp[0].startswith(':'):
                irc_dict['arguments'].append(irc_str[1:])
                break
            else:
                irc_dict['arguments'].append(temp[0])
            irc_str = temp[2]

#        print(irc_dict)

        if irc_dict['command'] == '001':
            await self.on_welcome(irc_dict)
        if irc_dict['command'].lower() == 'ping':
            await self.on_ping(irc_dict)
        if irc_dict['command'].lower() == 'privmsg':
            await self.on_privmsg(irc_dict)

    # SEND FUNCTIONS
    def send_raw(self, string):
        self.writer.write('{}\r\n'.format(string).encode('utf-8'))
#        print(string)

    def send_pong(self, pong):
        self.send_raw('PONG {}'.format(pong))

    def send_nick(self, nick):
        self.send_raw('NICK {}'.format(nick))

    def send_pass(self, password):
        self.send_raw('PASS {}'.format(password))

    def send_privmsg(self, channel, string):
        self.send_raw('PRIVMSG {} :{}'.format(channel, string))

    def send_join(self, channel):
        self.send_raw('JOIN {}'.format(channel))

    # EVENT FUNCTIONS
    async def on_welcome(self, irc_dict):
        pass

    async def on_ping(self, irc_dict):
        try:
            pong = irc_dict['arguments'][0]
        except IndexError:
            pong = ''
        self.send_pong(pong)

    async def on_privmsg(self, irc_dict):
        pass
