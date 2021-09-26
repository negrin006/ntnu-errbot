import discourse_context
import time
import logging

DC_INIT, DC_SUCCESS, DC_CANCEL, DC_FINAL, DC_PROMPT, DC_WAIT, DC_RECEIVED = range(7)

CANCEL_RESPONSES = ["cancel", "quit", "no", "bye"]

class QADiscourse(discourse_context.DiscourseContext):
    def __init__(self, bot, dc_name, user, prompt, success_cmd = None, cancel_cmd = None, timeout = 5 ):
        super().__init__( bot, dc_name, user, success_cmd, cancel_cmd, timeout  )
        self.prompt = prompt
             
    def step( self, response = None ):
        nxt = None

        while ( nxt is None ) and ( not self.is_done() ):
            self.end_time = time.time() + self.timeout
            self.log.info( f"QADiscourse.step({response}) state {self.state} values {self.values}")

            if (self.state == DC_INIT ):
                self.values = { 'answer' : None }
                self.state = DC_PROMPT
            elif (self.state == DC_PROMPT):
                nxt = ('send', self.user, self.prompt )
                self.state = DC_WAIT
            elif (self.state == DC_WAIT):
                nxt = ('receive', self.user, 'answer' )
                self.state = DC_RECEIVED
            elif (self.state == DC_RECEIVED):
                if (response not in CANCEL_RESPONSES):
                    self.values['answer'] = response
                    self.state = DC_SUCCESS
                    nxt = ( 'processed', self.user, self.values )
                    if (self.success_cmd):
                        self.success_cmd( self.bot, self.values )
                else:
                    self.cancel()
                    nxt = ( 'cancelled', self.user, self.values )
                    if (self.cancel_cmd):
                        self.cancel_cmd( self.bot, "The command was cancelled")
        self.last = nxt
        self.log.info( f"QADiscourse.step returns state {self.state} values {self.values} nxt {nxt}")

        return nxt

    
