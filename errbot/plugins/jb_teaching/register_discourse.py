import discourse_context
import question_answer_discourse
import menu_discourse
import time

DC_INIT, DC_SUCCESS, DC_CANCEL, DC_FINAL, \
DC_NAME_INIT, DC_NAME, DC_NAME_FINISH, \
DC_ID_INIT, DC_ID, DC_ID_FINISH, \
DC_COURSE_INIT, DC_COURSE, DC_COURSE_FINISH, \
DC_REGISTER_PROMPT_1, DC_REGISTER_INIT, DC_REGISTER, DC_REGISTER_FINISH, DC_REGISTER_CONFIRM  = range(18)

CANCEL_RESPONSES = ["cancel", "quit", "no", "bye"]

class RegisterDiscourse(discourse_context.DiscourseContext):
    def __init__(self, bot, author, success_cmd = None, cancel_cmd = None, timeout = 5 ):
        super().__init__( 'Course Registration', bot, author, success_cmd, cancel_cmd, timeout )
        self.child = None

    def step( self, response = None ):
        nxt = None

        while (nxt is None ) and (not self.is_done() ):
            self.end_time = time.time() + self.timeout
            self.log.info( f"RegisterDiscourse.step({response}) state {self.state} values {self.values}")
            if (self.state == DC_INIT ):
                nxt = ('send', self.user, 'Starting course registration. You can cancel registration by entering "quit" when prompted for information')
                self.values = { 'name' : None, 'id' : None, 'course' : None }
                self.state = DC_NAME_INIT
            elif (self.state == DC_NAME_INIT):
                self.child = question_answer_discourse.QADiscourse(self.bot, "register name", self.user, "What is your name?" )
                self.state = DC_NAME
            elif (self.state == DC_NAME):
                if ( not self.child.is_done() ):
                    nxt = self.child.step( response )
                else:
                    self.state = DC_NAME_FINISH
            elif ( self.state == DC_NAME_FINISH ):
                    if ( self.child.state == DC_SUCCESS ):
                        self.values["name"] = self.child.values["answer"]
                        self.state = DC_ID_INIT
                    else:
                        self.cancel()
                        if (self.cancel_cmd):
                            self.cancel_cmd( self.bot, "Command was cancelled" )
                    self.child.reclaim()
                    self.child = None
            elif (self.state == DC_ID_INIT):
                self.child = question_answer_discourse.QADiscourse(self.bot, "register id", self.user, "What is your student id?")
                self.state = DC_ID
            elif (self.state == DC_ID):
                if ( not self.child.is_done() ):
                    nxt = self.child.step( response )
                else:
                    self.state = DC_ID_FINISH
            elif ( self.state == DC_ID_FINISH ):
                    if ( self.child.state == DC_SUCCESS ):
                        self.values["id"] = self.child.values["answer"]
                        self.state = DC_COURSE_INIT
                    else:
                        self.state = DC_CANCEL
                    self.child.reclaim()
                    self.child = None
            elif (self.state == DC_COURSE_INIT ):
                self.child = menu_discourse.MenuDiscourse( self.bot, "course menu", self.user, "Which course do you want to register in?", [ "Artificial Intelligence (NKUST)", "Simultaneous Localization and Mapping (NTNU)", "Reinforcement Learning (NTNU)"] )
                self.state = DC_COURSE
            elif (self.state == DC_COURSE ):
                if ( not self.child.is_done() ):
                    nxt = self.child.step( response )
                else:
                    self.state = DC_COURSE_FINISH
            elif (self.state == DC_COURSE_FINISH):
                    if ( self.child.state == DC_SUCCESS ):
                        self.values["course"] = self.child.values["answer"]
                        self.state = DC_REGISTER_PROMPT_1
                    else:
                        self.state = DC_CANCEL
                    self.child.reclaim()
                    self.child = None
            elif (self.state == DC_REGISTER_PROMPT_1):
                card = {
                    'title' : 'Course Registration',
                    'fields' : (
                        ('Name', self.values['name'] ),
                        ('Student Id', self.values['id'] ),
                        ('Course', self.values['course']),
                    ),
                    'to': self.user
                }
                nxt = ('send_card', self.user, card )
                self.state = DC_REGISTER_INIT
            elif (self.state == DC_REGISTER_INIT ):
                self.child = question_answer_discourse.QADiscourse(self.bot, "register id", self.user, "Do you want to register this user?")                
                self.state = DC_REGISTER
            elif (self.state == DC_REGISTER):
                if ( not self.child.is_done() ):
                    nxt = self.child.step( response )
                else:
                    self.state = DC_REGISTER_FINISH
            elif ( self.state == DC_REGISTER_FINISH ):
                if ( self.child.state == DC_SUCCESS ):
                    ans = self.child.values["answer"]
                    if (ans.lower() == 'yes' ):
                        self.state = DC_REGISTER_CONFIRM
                else:
                    self.state = DC_CANCEL
                self.child.reclaim()
                self.child = None
            elif ( self.state == DC_REGISTER_CONFIRM ):
                if self.success_cmd:
                    self.success_cmd( self.bot, self.values )
                self.state = DC_FINAL
        self.last = nxt
        self.log.info( f"RegisterDiscourse.step returns state {self.state} values {self.values} nxt {nxt}")

        return nxt
    
