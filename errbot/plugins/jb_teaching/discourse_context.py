import time
import logging
import asyncio

class DiscourseContext:
    def __init__( self, bot, dc_name, user, timeout = 5 ):
        self.log = logger = logging.getLogger( "discourse" )
        self.bot = bot
        # self.success_cmd = success_cmd
        # self.cancel_cmd = cancel_cmd
        self.user = user
        self.dc_name = dc_name
        self.timeout = timeout
        self.parent = None
        self.children = []
        self.queue = asyncio.Queue( 1 )
        self.loop = asyncio.get_running_loop()
        self.waiting = False

    async def async_send( self, to, msg ):
        return self.bot.send( to, msg )

    async def async_receive( self ):
        self.log.debug("async_receive")
        
        self.waiting = True
        self.log.debug( f"waiting for the queue waiting {self.waiting}")
        
        resp = await self.queue.get( )
        self.queue.task_done()
        self.waiting = False
        self.log.debug( f"queue received value {resp}")
        err = None

        if resp.body == "cancel":
            err = "Cancel"
        return ( resp, err )
    
    def __str__(self):
        return f"con: user {self.user} {self.waiting}"

    def __repr__(self):
        return str(self)


