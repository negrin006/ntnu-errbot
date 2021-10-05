from jb_database import JB_Database
from errbot import BotPlugin, botcmd
import spacy
import register_discourse
import threading
import time
import asyncio

class JB_TeachingPlugin(BotPlugin):
    """
    This is a very basic plugin to try out your new installation and get you started.
    Feel free to tweak me to experiment with Errbot.
    You can find me in your init directory in the subdirectory plugins.
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

        self.worker = threading.Thread( target=self.run_worker, args=( self ) )
        self.do_work = True
        self.worker.start()
        self.db = JB_Database( self.bot_config.JB_DATABASE )

    def deactivate(self):
        self.do_work = False
        self.worker.join()

    @botcmd  # flags a command
    def register( self, msg, args ):  # a command callable with /register
        """
        Execute to check if Errbot responds to command.
        Feel free to tweak me to experiment with Errbot.
        You can find me in your init directory in the subdirectory plugins.
        """
        
        open_contexts = filter( lambda c:  c.user == msg.frm and c.is_processed(), self.contexts )
        for o in open_contexts:
            o.reclaim()

        d = register_discourse.RegisterDiscourse( self, msg.frm, self.register_course_cmd, self.cancel_cmd )       
        self.contexts.append( d )

    def register_course_cmd( self, user, values ):
        self.log.info( f"Execute register course {values}" )

    def cancel_cmd( self, user, mess = None ):
        return
        self.send( user, "Command cancelled")
        if mess:
            self.send( user, mess )

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
        

    def process_input( self, mess ):
        for c in self.contexts:
            user, queue = c
            if user == mess.frm:
                queue.put( mess )
    
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

    @botcmd
    def qatest( self, msg, args ):  # a command callable with /register
        asyncio.run( self.qa_test_cmd(msg.frm, msg, args) )

    async def async_send( self, to, msg ):
        return self.send( to, msg )

    async def async_receive( self, user ):
        q = asyncio.Queue()
        cont = ( user, q )

        self.contexts.append( cont )
        resp = await q.get()
        err = None

        if resp == "cancel":
            err = "Cancel"
        return ( resp, err )

    async def qa_test_cmd( self, user, msg, args ):
        await self.async_send( user, "Are you ready to test the system?")
        await self.async_send( user, "Please enter your name?")
        name, err = await self.async_receive( user )
        if err:
            if err == "Timeout":
                await self.async_send(user, "The command was cancelled")
            else:
                await self.async_send( user, "The command was cancelled")
        await self.async_send( user, f"Nice to meet you user {name}")

    
        
