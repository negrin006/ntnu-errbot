import discourse_context
import time
import logging

DC_INIT, DC_SUCCESS, DC_CANCEL, DC_FINAL, DC_PROMPT, DC_OPTIONS, DC_PROMPT_SELECT, DC_WAIT, DC_RECEIVED = range(9)

CANCEL_RESPONSES = ["cancel", "quit", "no", "bye"]

class MenuDiscourse(discourse_context.DiscourseContext):
    def __init__(self, bot, dc_name, user, prompt, options, success_cmd = None, cancel_cmd = None, timeout = 5 ):
        super().__init__( bot, dc_name, user, success_cmd, cancel_cmd, timeout  )
        self.prompt = prompt
        self.options = options
             
    def step( self, response = None ):
        nxt = None

        while ( nxt is None ) and ( not self.is_done() ):
            self.end_time = time.time() + self.timeout
            self.log.info( f"MenuDiscourse.step({response}) state {self.state} values {self.values}")

            if (self.state == DC_INIT ):
                self.values = { 'answer' : None }
                self.state = DC_PROMPT
            elif (self.state == DC_PROMPT):
                nxt = ('send', self.user, self.prompt )
                self.state = DC_OPTIONS
                self.count = 0
            elif (self.state == DC_OPTIONS ):
                if self.count < len(self.options):
                    nxt = ('send', self.user, f"{self.count+1} {self.options[self.count]}")
                    self.count = self.count + 1
                else:
                    self.state = DC_PROMPT_SELECT
            elif ( self.state == DC_PROMPT_SELECT ):
                nxt = ('send', self.user, f'Select a number from 1 to {len(self.options)}')
                self.state = DC_WAIT
            elif (self.state == DC_WAIT):
                nxt = ('receive', self.user, 'answer' )
                self.state = DC_RECEIVED
            elif (self.state == DC_RECEIVED):
                if (response not in CANCEL_RESPONSES):
                    r_id = None
                    try:
                        r_id = int( response )
                    except ValueError:
                        pass
                    if r_id:
                        self.values['answer'] = self.options[r_id-1]
                        self.state = DC_SUCCESS
                        nxt = ( 'processed', self.user, self.values )
                        if (self.success_cmd):
                            self.success_cmd( self.bot, self.values )
                    else:
                        self.state = DC_PROMPT_SELECT
                else:
                    self.cancel()
                    nxt = ( 'cancelled', self.user, self.values )
                    if (self.cancel_cmd):
                        self.cancel_cmd( self.bot, "The command was cancelled")
        self.last = nxt
        self.log.info( f"MenuDiscourse.step returns state {self.state} values {self.values} nxt {nxt}")

        return nxt

    
