from errbot import BotPlugin, botcmd
import spacy
import register_discourse
import threading
import time

class StudentsPlugin(BotPlugin):
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
        
        open_contexts = filter( lambda c:  c.user == msg.frm and c.state != DC_KILL, self.contexts )
        for o in open_contexts:
            o.kill()

        d = register_discourse.RegisterDiscourse( msg.frm )
        
        self.contexts.append( d )

    def callback_message(self, mess):
        self.log.debug( f'students.callback_message: {mess}')

        text = mess.body
        if (text[-1] not in ['.', '!', '?']):
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
        
        self.process_input( mess )

    def process_input( self, mess ):
        for c in self.contexts:
            if ( not c.is_killed() ) and ( c.user == mess.frm ):
                if c.is_blocked():
                    c.step( mess.body )

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
            self.log.debug("Running thread")
            for c in self.contexts:
                if (not c.is_killed() ): 
                    if not c.is_blocked():
                        nxt = c.step()
                        if nxt is not None:
                            com, to, mess = nxt
                            if com == 'send':
                                self.send( to, mess )
                    else:
                        if ( time.time() > c.end_time ):
                            c.cancel()

            time.sleep(1)


            