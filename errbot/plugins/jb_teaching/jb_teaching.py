from asyncio.queues import QueueEmpty
from jb_database import JB_Database
from errbot import BotPlugin, botcmd
import spacy
import register_discourse
import threading
import time
import asyncio
import threading
import functools
import discourse_context

class JB_TeachingPlugin(BotPlugin):
    """
    This plugin supports my teaching <jacky.baltes@ntnu.edu.tw>
    """

    def activate(self):
        super().activate()
        self.nlp = spacy.load( "en_core_web_lg" )

        self.register_prompts = [ self.nlp( "I would like to register for the course" ),
            self.nlp( "please register me in the course" ),
        ]

        self.courses = [ 
            [ self.nlp(s) for s in ["ai", "artificial intelligence"] ],
            [ self.nlp(s) for s in ["reinforcement learning", "rl"] ],
            [ self.nlp(s) for s in [ "simultaneous localization and mapping", "slam" ] ] 
        ]

        self.contexts = []

        # self.worker = threading.Thread( target=self.run_worker, args=( self ) )
        # self.do_work = True
        # self.worker.start()
        self.db = JB_Database( self.bot_config.JB_DATABASE )
        
    def deactivate(self):
        self.do_work = False
        self.worker.join()

    @botcmd  # flags a command
    def register( self, msg, args ):  # a command callable with /register
        "register for a course"
        d = register_discourse.RegisterDiscourse( self, msg.frm ) 
        err = self.add_context( d )
        if not err:
            ret = d.run( msg, args )
        elif err == "Already registered":
            self.send( msg.frm, "You are already in a dialogue")
            self.send( msg.frm, "Enter cancel to terminate previous dialog")

    def callback_message(self, mess):
        self.log.debug( f'jb_teaching.callback_message: {mess}')

        ret = self.process_waiting( mess )
        if ( not ret ):
            text = mess.body
            if (text) and (text[-1] not in ['.', '!', '?']):
                text = text + "."

            m = self.nlp( text )
            for r in self.register_prompts:
                if r.similarity( m ) > 0.80:
                    self.log.info( f'Found register prompt {text}' )
                    course = self.extract_course( m )
                    self.log.info( f'course {course}')
                    for token in m:
                        self.log.info( f'{token.text}, {token.pos_} {token.has_vector}, {token.vector_norm}, {token.is_oov}' )
                    break
        
    def find_context_by_user( self, user ):
        self.log.debug( f"find_context_by_user {self.contexts} {user}")
        ret = (-1, None)
        for i,con in enumerate( self.contexts ):
            if user == con.user:
                ret = ( i, con )
                break
        self.log.debug( f"find_context_by_user returns {ret}")
        return ret
    
    def delete_context_by_index( self, ind ):
        del self.contexts[ind]

    def delete_context( self, con ):
        return self.contexts.remove( con )

    def add_context(self, con):
        ind, _ = self.find_context_by_user( con.user )
        err = None
        if ( ind < 0 ):
            self.contexts.append( con )
            self.log.debug( f"added context for user {con.user} contexts: {self.contexts}")
        else:
            err = "Already registered"
        return err 

    def process_waiting( self, mess ):
        ret = False
        text = mess.body

        if text[0] != '/':
            ind, con = self.find_context_by_user( mess.frm )
            if ind >= 0:
                self.log.debug( f"process_waiting {con}")
                if con.waiting:
                    asyncio.run_coroutine_threadsafe( con.queue.put( mess ), con.loop )
                    self.log.debug("value entered into queue")
                ret = True
        return ret
    
    def extract_course( self, mess ):
        course = None
        start_tokens = [ 'in' ]
        end_tokens = [ '.', '?', '!' ]
        pattern_course = [ [ {'LEMMA' : {'IN' : ['in'] } },
            { 'LEMMA' : {'IN': ['class', 'course'] }, 'OP' : '?' },
            {'POS': { 'IN': ['NOUN', 'ADJ', 'PROPN'] }, 'OP' : '+'},
#            {'LOWER' : {'IN' : end_tokens}} ] ]
            {'IS_PUNCT': True } ] ]
        matcher = spacy.matcher.Matcher(self.nlp.vocab) 
        matcher.add("matching_course", pattern_course)
        
        matches = matcher( mess )
        self.log.info( f'matches {matches}')

        for match_id, start, end in matches:
            # Create the matched span and assign the match_id as a label
            span = spacy.tokens.Span(mess, start, end, label=match_id)
            self.log.info( f'span.text {span.text}, span.label_ {span.label_}' )

        sub_text = ''
        if(len(matches) > 0):
            span = mess[matches[0][1]:matches[0][2]] 
            sub_text = span.text
            tokens = sub_text.split(' ')
            self.log.info( f'extract_course: tokens {tokens}' )
            course = tokens[1:-1]
        return course

    def run_worker( self ):
        while( self.do_work ):
            # self.log.debug("Running thread")
            # for c in self.contexts:
            #     if not c.is_filled(): 
            #         if not c.is_waiting():
            #             nxt = c.step()
            #             if nxt is not None:
            #                 com, to, mess = nxt
            #                 if com == 'send':
            #                     self.send( to, mess )
            #                 elif com == 'send_card':
            #                     self.send_card( ** mess )
            #         else:
            #             if ( time.time() > c.end_time ):
            #                 c.cancel()
            #     elif not c.is_processed():
            #         pass
            time.sleep(0.5)

    # @botcmd
    # def qatest( self, msg, args ):  # a command callable with /register
    #     asyncio.run( self.qa_test_cmd_runner( msg.frm, msg, args ) )

    # async def qa_test_cmd_runner( self, user, msg, args ):
    #     ind, con = self.find_context_by_user( user )
    #     resp = "NO RESPONSE"

    #     if ( ind < 0 ):
    #         con = discourse_context.DiscourseContext(self, "dc_qa_test", msg.frm, 10 )
    #         self.contexts.append( con )
    #         self.log.debug( f"added context for user {user} contexts: {self.contexts}")
    #         ret = await self.qa_test_cmd( user, msg, args )
    #         self.delete_context( ind )
    #     else:
    #         self.send( user, "You are already in a dialogue")
    #         self.send( user, "Enter cancel to terminate previous dialog")            
    #         return "User already started a discourse"
        
    # async def qa_test_cmd( self, user, msg, args ):
    #     self.log.debug("qa_test_cmd started")
    #     ind, con = self.find_context_by_user( user )
    #     if ind >= 0:
    #         await con.async_send( user, "Are you ready to test the system?")
    #         await con.async_send( user, "Please enter your name?")
    #         name, err = await con.async_receive( )
    #         self.log.debug( f"qa_test_cmd received {name},{err}")
    #         if err:
    #             if err == "Timeout":
    #                 await con.async_send(user, "The command timed out")
    #                 return "Command timeout"
    #             else:
    #                 await con.async_send( user, f"The command was cancelled {err}")
    #                 return "Command cancelled"
    #         await con.async_send( user, f"Nice to meet you user {name}")
    #         return None
    #     else:
    #         self.send( f" qatest: context {user} not found")
    #     return "Invalid Context"

