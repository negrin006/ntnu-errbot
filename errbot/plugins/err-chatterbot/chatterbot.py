from errbot import BotPlugin, re_botcmd, botcmd
import config

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer

class ErrChatterBot(BotPlugin):
    """
    This is a very basic plugin to try out your new installation and get you started.
    Feel free to tweak me to experiment with Errbot.
    You can find me in your init directory in the subdirectory plugins.
    """

    def activate(self):
        super().activate()
        self.chatbot = ChatBot('blue')
        self.trainer = ChatterBotCorpusTrainer(self.chatbot)
        # Train the chatbot based on the english corpus
        self.trainer.train("chatterbot.corpus.english")

        trainer = ListTrainer( self.chatbot )
        trainer.train( [
            "I would like to register for the course reinforcement learning",
            "Great. What is your name?",
            "My name is John Doe",
            "What is your student id?",
            "My student id is 012345689H"
            "Please tell me the department and university that you are attending"
            "I am in the Electrical Engineering Department at National Taiwan Normal University"
            "Good. I have finished your registration"
        ])

    @botcmd
    def card( self, msg, args ):
        self.send_card(title='Title + Body',
                body='text body to put in the card',
                thumbnail='https://raw.githubusercontent.com/errbotio/errbot/master/docs/_static/errbot.png',
                image='https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png',
                link='http://www.google.com',
                fields=(('First Key','Value1'), ('Second Key','Value2')),
                color='red',
                in_reply_to=msg)

    @botcmd
    def stream( self, msg, args ):
        stream = self.send_stream_request(msg.frm, open('/tmp/myfile.zip', 'rb'), name='bills.zip', stream_type="document" )

    # @re_botcmd(pattern=r"(^| )cookie( |$)")  # flags a command
    # def blue(self, msg, args):  # a command callable with !tryme
    #     """
    #     A test to received commands without prefix.
    #     """
        
    #     resp = self.chatbot.get_response(msg)
    #     return resp

    def callback_message(self, mess):
        if mess and mess.body[0] != config.BOT_PREFIX:
            #self.send(mess.frm, "Message: " + mess.body )
            resp = self.chatbot.get_response( mess.body )
            self.send( mess.frm, str(resp) )