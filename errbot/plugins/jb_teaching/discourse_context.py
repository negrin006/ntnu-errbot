import time
import logging

DC_INIT, DC_SUCCESS, DC_CANCEL, DC_FINAL = range(4)

class DiscourseContext:
    def __init__( self, bot, dc_name, user, success_cmd = None, cancel_cmd = None, timeout = 5 ):
        self.bot = bot
        self.success_cmd = success_cmd
        self.cancel_cmd = cancel_cmd
        self.user = user
        self.dc_name = dc_name
        self.children = []
        self.state = DC_INIT
        self.timeout = timeout
        self.end_time = None
        self.last = ("init", "system", "" )
        self.values = {}
        self.parent = None
        self.log = logger = logging.getLogger( "discourse" )

    def step( response = None ):
        self.log.info( f"DiscourseContext.step({response}) state {self.state} values {self.values}")

    def reclaim( self ):
        self.state = DC_FINAL

    def cancel( self ):
        if ( self.cancel_cmd ):
            self.cancel_cmd( self )
        self.state = DC_CANCEL

    def is_waiting( self ):
        return ( self.last ) and ( self.last[0].lower().startswith('receive') )

    def add_child( self, child ):
        child.parent = self
        self.children.append( child )

    def is_filled( self ):
        return ( self.state == DC_SUCCESS ) or ( self.state == DC_CANCEL )

    def is_processed( self ):
        return ( self.state == DC_FINAL )


