import time
import logging
import asyncio

import errbot

class DiscourseContext:
    def __init__( self, bot, dc_name, user, timeout = 5 ):
        self.log = logging.getLogger( "discourse" )
        self.bot = bot
        # self.success_cmd = success_cmd
        # self.cancel_cmd = cancel_cmd
        self.user = user
        self.dc_name = dc_name
        self.timeout = timeout

        self.parent = None
        self.children = []

        self.waiting = False

    def run( self, fut ):
        asyncio.run( self.runner( fut ) )
        # t = asyncio.create_task( self.runner( fut ) ) 
        # done,pending = asyncio.wait( {t} )
        # if t in done:
        #     self.bot.delete_context(self)

    async def runner(self, fut ):
        self.queue = asyncio.Queue( 1 )
        self.loop = asyncio.get_running_loop()
        return await fut

    def send( self, to, msg ):
        return self.bot.send( to, msg )

    async def async_send( self, to, msg ):
        return self.send( to, msg )

    async def async_receive( self ):
        self.log.debug("async_receive")
        
        self.waiting = True
        self.log.debug( f"waiting for the queue waiting {self.waiting}")
        
        resp = None
        err = None
        try:
            resp = await asyncio.wait_for( self.queue.get( ), self.timeout )
            self.log.debug( f"queue received value {resp}")
            #self.queue.task_done()
            if resp.body == "cancel":
                err = "@Cancel"
        except asyncio.TimeoutError:
            err = "@Timeout"

        self.waiting = False
        return ( resp, err )
    
    def __str__(self):
        return f"con: user {self.user} {self.waiting}"

    def __repr__(self):
        return str(self)

    def __del__(self):
        self.log.debug( f"destructor called for context {self.dc_name}")

    async def qa(self, prompt ):
        await self.async_send( self.user, prompt )
        data, err = await self.async_receive( )
        self.log.debug( f"qa received {data},{err}")
        if err:
            if err == "@Timeout":
                await self.async_send( self.user, "Prompt cancelled due to timeout")
            else:
                await self.async_send( self.user, f"The command was cancelled by the user {err}")
        return data

    async def menu(self, options ):
        for i,o in enumerate( options ):
            await self.async_send( self.user, f'{i+1}: {o}' )
    
        select = -1
        while ( select < 0 ) or ( select >= len(options) ):
            await self.async_send( self.user, f"Enter a number from 1 tp {len(options)}")
            data, err = await self.async_receive( )
            self.log.debug( f"menu received {data},{err}")
            if err:
                if err == "@Timeout":
                    await self.async_send( self.user, "Prompt cancelled due to timeout")
                    return None
                else:
                    await self.async_send( self.user, f"The command was cancelled by the user {err}")
                    return None
            try:
                select = int(data.body) - 1
            except ValueError:
                select = -1
        return select