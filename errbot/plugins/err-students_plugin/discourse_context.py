import time

DC_INIT, DC_END, DC_CANCEL, DC_KILLED = range(4)

class DiscourseContext:
    def __init__( self, dc_name, user, timeout = 5 ):
        self.user = user
        self.dc_name = dc_name
        self.children = []
        self.state = DC_INIT
        self.last = None
        self.timeout = timeout
        self.end_time = None

    def step( response = None ):
        self.end_time = time.time() + self.timeout
        next_act = None
        if self.state == DC_INIT:
            self.state = DC_END
            next_act = ('send', self.user, f'Starting the {self.dc_name} discourse' )
        elif self.state == DC_END:
            self.state = DC_KILLED
            next_act = ('send', self.user, f'Finished the {self.dc_name} discourse' )
        elif self.state == DC_CANCEL:
            self.state = DC_KILLED
            next_act = ('send', self.user, f'Timeout waiting for response' )
        self.last = next_act
        return next_act

    def kill( self ):
        self.state = DC_KILLED

    def is_killed( self ):
        return self.state == DC_KILLED

    def cancel( self ):
        self.state = DC_CANCEL