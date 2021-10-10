import time
import logging
import queue

class DiscourseContext:
    def __init__( self, bot, dc_name, user, success_cmd = None, cancel_cmd = None, timeout = 5 ):
        self.bot = bot
        self.success_cmd = success_cmd
        self.cancel_cmd = cancel_cmd
        self.user = user
        self.dc_name = dc_name
        self.children = []
        self.timeout = timeout
        self.parent = None
        self.log = logger = logging.getLogger( "discourse" )
        self.queue = queue.Queue()

