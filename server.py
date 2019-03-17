import os.path
import torndb
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os
from binascii import hexlify
import tornado.web
from tornado.options import define, options

define("port", default=6060, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="iutnet", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_password", default="", help="database password")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            #GET METHOD :
            (r"/signup", signup),
            (r"/login", login),
            (r".*", defaulthandler),
        ]
        settings = dict()
        super(Application, self).__init__(handlers, **settings)
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    def check_user(self,user):
        resuser = self.db.get("SELECT * from users where username = %s",user)
        if resuser:
            return True
        else :
            return False

    def check_api(self,api):
        resuser = self.db.get("SELECT * from users where api = %s", api)
        if resuser:
            return True
        else:
            return False
    def check_auth(self,username,password):
        resuser = self.db.get("SELECT * from users where username = %s and password = %s", username,password)
        if resuser:
            return True
        else:
            return False

class defaulthandler(BaseHandler):
    def get(self):
        output = {'status':'Wrong Command'}
        self.write(output)

    def post(self, *args, **kwargs):
        output = {'status':'Wrong Command'}
        self.write(output)


class signup(BaseHandler):
    def get(self,*args):
        username = str(self.get_argument('username'))
        password = str(self.get_argument('password'))
        fname = str(self.get_argument('firstname',''))
        lanme = str(self.get_argument('lastname',''))

        if not self.check_user(username):
            api_token = str(hexlify(os.urandom(16)))
            user_id = self.db.execute("INSERT INTO users (username, password, fname, lname ,api) "
                                     "values (%s,%s,%s,%s,%s) "
                                     , username,password,fname,lanme,api_token)

            output = {   'message': 'Signed Up Successfully',
                        'code': '200' }
            self.write(output)
        else:
            output = {'status': 'User Exist'}
            self.write(output)
    
class login(BaseHandler):
    def get(self):
        username = str(self.get_argument('username'))
        password = str(self.get_argument('password'))
        
        if self.check_auth(username,password):
            api_token = str(hexlify(os.urandom(16)))
            self.db.execute("update users set api=%s where username=%s",api_token,username)
            output = {
                'message' : 'Logged in Successfully',
                'code' : '200',
                'token' : api_token
            }
            self.write(output)
        else:
            output = {
                'message' : 'Invalid username or password',
                'code' : '401'
            }
            self.set_status(401)
            self.write(output)

class logout(BaseHandler):
    def get(self):
        username = str(self.get_argument('username'))
        password = str(self.get_argument('password'))
        
        if self.check_auth(username,password):
            api_token = str(hexlify(os.urandom(16)))
            self.db.execute("update users set api=%s where username=%s",api_token,username)
            output = {
                'message' : 'Logged out Successfully',
                'code' : '200',
            }
            self.write(output)
        else:
            output = {
                'message' : 'Invalid username or password',
                'code' : '401'
            }
            self.set_status(401)
            self.write(output)





def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
