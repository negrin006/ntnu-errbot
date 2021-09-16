from errbot import BotPlugin, botcmd
import spacy

class Students(BotPlugin):
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
    

    @botcmd  # flags a command
    def register( self, msg, course ):  # a command callable with !tryme
        """
        Execute to check if Errbot responds to command.
        Feel free to tweak me to experiment with Errbot.
        You can find me in your init directory in the subdirectory plugins.
        """
        return f"Let me help you register for the course {{course}}"  # This string format is markdown.

    @botcmd
    def name( self, msg, args ):
        """
        Request the name from the user
        """
        yield f"What is your name?"
