import discourse_context
import time

DC_INIT, DC_END, DC_CANCEL, DC_KILLED, DC_NAME_PROMPT, DC_NAME, DC_NAME_RECEIVED, DC_COURSE_PROMPT, DC_COURSE, DC_COURSE_RECEIVED, DC_ID_PROMPT, DC_ID, DC_ID_RECEIVED, DC_FINISH  = range(14)

CANCEL_RESPONSES = ["cancel", "quit", "no", "bye"]

class RegisterDiscourse(discourse_context.DiscourseContext):
    def __init__(self, author ):
        super().__init__( 'Course Registration', author )

    def step( self, response = None ):
        nxt = None

        self.end_time = time.time() + self.timeout

        if (self.state == DC_INIT ):
            nxt = ('send', self.user, 'Starting course registration. You can cancel registration by entering "quit" when prompted for information')
            self.values = { 'name' : None, 'id' : None, 'course' : None }
            self.state = DC_NAME_PROMPT
        elif (self.state == DC_NAME_PROMPT):
            nxt = ('send', self.user, 'What is your name?')
            self.state = DC_NAME
        elif (self.state == DC_NAME):
            nxt = ('recv', self.user, 'name' )
            self.state = DC_NAME_RECEIVED
        elif (self.state == DC_NAME_RECEIVED):
            if (response not in CANCEL_RESPONSES):
                self.values['name'] = response
                self.state = DC_ID_PROMPT
            else:
                self.cancel()
        elif (self.state == DC_ID_PROMPT):
            self.state = DC_ID
            nxt = ('send', self.user, 'What is your student id?')
        elif (self.state == DC_ID):
            nxt = ('recv', self.user, 'id' )
            self.state = DC_ID_RECEIVED
        elif (self.state == DC_ID_RECEIVED):
            if (response not in CANCEL_RESPONSES):
                self.values['id'] = response
                self.state = DC_COURSE_PROMPT
            else:
                self.cancel()
        elif (self.state == DC_COURSE_PROMPT):
            self.state = DC_COURSE
            nxt = ('send', self.user, 'What course do you want to join?')
        elif (self.state == DC_COURSE):
            nxt = ('recv', self.user, 'name' )
            self.state = DC_COURSE_RECEIVED
        elif (self.state == DC_COURSE_RECEIVED):
            if (response not in CANCEL_RESPONSES):
                self.values['course'] = response
                self.state = DC_FINISH
            else:
                self.cancel()
        elif (self.state == DC_FINISH):
            self.state = DC_KILLED
            nxt = ('send', self.user, f'User {self.user}/{self.values["name"]} {self.values["id"]} registered successfully for the course {self.values["course"]}')
        elif self.state == DC_CANCEL:
            self.state = DC_KILLED
            nxt = ('send', self.user, f'Timeout waiting for response' )
        self.last = nxt
        return nxt
            
    def is_blocked( self ):
        return ( self.state == DC_NAME ) or ( self.state == DC_ID ) or ( self.state == DC_COURSE )

    
