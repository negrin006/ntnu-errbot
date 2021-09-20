import sqlite3
import logging

logger = logging.getLogger(__name__)
logger.setLevel( logging.DEBUG )


class JB_Database:

    def __init__(self, db_name ):
        self.db_name = db_name
        self.opened = False
        self.open_db()

    def open_db( self ):
        self.db = sqlite3.connect( self.db_name )
        self.opened = True

    def close_db( self ):
        self.db.commit()
        self.db.close()
        self.opened = False

    def check_table( self, table ):
        found = False
        if not self.opened:
            self.open_db()
        c = self.db.cursor()
        c.execute( f'''SELECT count(name) FROM sqlite_master WHERE type='table' AND name=? ''', (table,) )
        f = c.fetchone()
        #print( 'c.fetchone', f )
        if f[0] > 0:
            found = True
        return found

    def get_table( self, table ):
        self.open_db()
        c = self.db.cursor()
        c.execute( f''' SELECT * from '{table}'; ''' )
        res = c.fetchall()
        self.close_db()
        return res

    def execute_sql(self, statement, values = None ):
        self.open_db()
        c = self.db.cursor()
        statement = statement.lstrip( " \t\n" )
        if values:
            ret = c.execute( statement, values )
        else:
            ret = c.execute( statement )
        print('execute_sql', 'ret', ret )
        if statement.startswith( "SELECT" ) or statement.startswith( "PRAGMA table_info("):
            ret = c.fetchall()
        self.db.commit()
        self.close_db()
        return ret

    def convert_to_canonical_title( self, title ):
        return title.lower().replace(" ","-")

    def setup_db( self, reset = False ):
        if reset:
            self.db.truncate()
            self.db.drop_tables()

    def get_participant( self, discord_id ):
        self.open_db()
        c = self.db.cursor()
        cols = [ "name", "email", "discord_id", "seed", "state" ]
        cs = ",".join( cols )
        c.execute( f'''SELECT {cs} 
                       FROM participants 
                       WHERE (discord_id=?)''', (discord_id,) )
        f = c.fetchone()
        self.close_db() 
        if f:
            print('f', f)
            p = dict( zip( cols, f ) )
        else:
            p = None
        return p

    def get_question( self, discord_id, q_ord, q_state ):
        self.open_db()
        c = self.db.cursor()
        cols = [ "question_body", "hint", "solution", "seed", "template", "participant", "ord", "state" ]
        cs = ",".join( cols )
        c.execute( f'''SELECT {cs} 
                       FROM questions 
                       WHERE participant=? AND state=?
                       ORDER BY ord ASC
                    ''', (discord_id, q_state ) )
        f = c.fetchone()
        self.close_db() 
        if f:
            logger.debug( f'fetchone: {f}' )
            p = dict( zip( cols, f ) )
        else:
            p = None
        return p

    def update_question( self, q ):
        sql = '''
        REPLACE INTO questions( question_body, hint, solution, seed, template, participant, ord, state )
            VALUES(?,?,?,?,?,?,?,?)
        '''
        return self.execute_sql( sql, ( q['question_body'], q['hint'], 
                                        q['solution'], q['seed'], 
                                        q['template'], q['participant'], q['ord'], q['state'] ) )

    def update_participant(self, p ):
        sql = '''
        REPLACE INTO participants( name, email, discord_id, seed, state )
            VALUES(?,?,?,?,?)
        '''
        return self.execute_sql( sql, ( p['name'], p['email'], p['discord_id'], p['seed'], p['state'] ) )

    def get_question_template(self, min_level ):
        cols = ["title", "file_name", "ord" ]
        cs = ",".join(cols)
        sql = f"""
            SELECT {cs}
            FROM question_templates
            WHERE ord >= ?
            ORDER by ord
        """
        f = self.execute_sql( sql, ( min_level, ) )[0]
        print('question_templates', f )
        if f:
            ques = dict( zip(cols, f ) )
        else:
            ques = None
        return ques

    def __del__(self):
        self.close_db()



    
