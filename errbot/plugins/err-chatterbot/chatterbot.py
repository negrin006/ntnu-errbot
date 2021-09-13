from errbot import BotPlugin, re_botcmd


class ChatterBot(BotPlugin):
    """
    This is a very basic plugin to try out your new installation and get you started.
    Feel free to tweak me to experiment with Errbot.
    You can find me in your init directory in the subdirectory plugins.
    """

    @re_botcmd(pattern=r"(^| )cookie( |$)")  # flags a command
    def blue(self, msg, args):  # a command callable with !tryme
        """
        A test to received commands without prefix.
        """
        yield "Here's a cookie for you, {}".format(msg.frm)
        yield "/me hands out a cookie."