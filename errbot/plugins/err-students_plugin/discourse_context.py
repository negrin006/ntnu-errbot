DC_INIT, DC_END, DC_ERROR, DC_KILLED = range(4)

class DiscourseContext:
    def __init__( self, dc_name, user ):
        self.user = user
        self.dc_name = dc_name
        self.children = []
        self.state = DC_INIT
        self.last = None

    def step( response = None ):
        next_act = None
        if self.state == DC_INIT:
            self.state = DC_END
            next_act = ('send', self.user, f'Starting the {self.dc_name} discourse' )
        elif self.state == DC_END:
            self.state = DC_KILLED
            next_act = ('send', self.user, f'Finished the {self.dc_name} discourse' )
        else:
            next_act = None
        self.last = next_act
        return next_act

    def kill( self ):
        self.state = DC_KILLED

    def is_killed( self ):
        return self.state == DC_KILLED