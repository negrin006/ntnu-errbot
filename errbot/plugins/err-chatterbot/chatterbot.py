from errbot import BotPlugin, re_botcmd
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

class ChatterBot(BotPlugin):
    """
    This is a very basic plugin to try out your new installation and get you started.
    Feel free to tweak me to experiment with Errbot.
    You can find me in your init directory in the subdirectory plugins.
    """

    def activate(self):
        super().activate()
        self.chatbot = ChatBot('Blue')
        self.trainer = ChatterBotCorpusTrainer()
        # Train the chatbot based on the english corpus
        self.trainer.train("chatterbot.corpus.english")

    @re_botcmd(pattern=r"(^| )cookie( |$)")  # flags a command
    def blue(self, msg, args):  # a command callable with !tryme
        """
        A test to received commands without prefix.
        """
        
        resp = self.chatbot.get_response(msg)
        return resp