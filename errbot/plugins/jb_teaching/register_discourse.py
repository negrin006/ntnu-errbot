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
        name = await self.qa( "Please enter your name?" )
        if name:
            id = await self.qa( "Please enter your student id")
            if id:
                courses = ["SLAM", "CV", "RL" ]
                select = await self.menu( courses )
                if select:
                    await self.async_send( self.user, f"Registering studentd {name} with {id} for course {courses[select]}" )


