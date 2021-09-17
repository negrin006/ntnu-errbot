import discourse_context

DC_INIT, DC_END, DC_ERROR, DC_KILLED, DC_NAME, DC_FINISH  = range(6)

class RegisterDiscourse(discourse_context.DiscourseContext):
    def __init__(self, author ):
        super().__init__( 'Course Registration', author )
        self.values = {}

    def step( self, response = None ):
        nxt = None

        if (self.state == DC_INIT ):
            self.state = DC_NAME
            nxt = ('send', self.user, 'First, I need to know your name')
        elif (self.state == DC_NAME):
            self.values['name'] = response
            self.state = DC_FINISH
            nxt = ('recv', self.user, 'name' )
        elif (self.state == DC_FINISH):
            self.state = DC_KILLED
            nxt = ('send', self.user, f'User {self.user}/{self.values["name"]} registered successfully for the course')
        self.last = nxt
        return nxt
            
    def blocked( self ):
        return self.state == DC_NAME
