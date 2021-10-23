import discourse_context
import question_answer_discourse
import menu_discourse
import time
import asyncio

class RegisterDiscourse(discourse_context.DiscourseContext):
    def __init__(self, bot, user, timeout = 10 ):
        super().__init__( bot, 'Course Registration', user, timeout )
        self.child = None

    def run(self, msg, args ):
        super().run( self.register_cmd(  msg, args ) )
        self.bot.delete_context( self )

    async def register_cmd( self, msg, args ):
        self.log.debug("register_cmd started")

        await self.async_send( self.user, "Are you ready to test the system?")
        await self.async_send( self.user, "Please enter your name?")
        name, err = await self.async_receive( )
        self.log.debug( f"register_cmd received {name},{err}")
        if err:
            if err == "@Timeout":
                await self.async_send( self.user, "The command timed out")
                return "Command timeout"
            else:
                await self.async_send( self.user, f"The command was cancelled {err}")
                return "Command cancelled"
        await self.async_send( self.user, f"Nice to meet you user {name}")



