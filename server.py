import os.path
import torndb
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os
from binascii import hexlify
import tornado.web
import datetime
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
            (r"/sendticket", sendticket),
            (r"/getticketcli", getticketcli),
            (r"/closeticket", closeticket),
            (r"/getticketmod", getticketmod),
            (r"/h", h), # testing 
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
    def is_admin(self,token):
        res = int(self.db.get("select role from users where api=%s",token)['role'])
        if res == 1:
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
            user_id = self.db.execute("INSERT INTO users (username, password, fname, lname ,api, role) "
                                     "values (%s,%s,%s,%s,%s,0) "
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

# SendTIcket
class sendticket(BaseHandler):
    def get(self):
        token = str(self.get_argument('token'))
        subject = str(self.get_argument('subject'))
        body = str(self.get_argument('body'))

        if self.check_api(token):
            user_id = int(self.db.get("select ID from users where api=%s",token)['ID'])
            currentDT = datetime.datetime.now()
            ticket_id = self.db.execute("INSERT INTO tickets (title, body, userID, status, date) "
                                     "values (%s,%s,%s,%s,%s) "
                                     , subject,body,user_id,0,currentDT.strftime("%Y-%m-%d %H:%M:%S"))
            output = {
                'message':'Tikcet Snet Successfully',
                'id':ticket_id,
                'code':'200'
            }
            self.write(output)
        else:
            output = {
                'message':'Invalid token',
                'code':'401'
            }
            self.set_status(401)
            self.write(output)


def getStatus(code):
    if code == 0:
        return 'Open'
    elif code == 1:
        return 'Wating'
    else:
        return 'Closed'

# Get Ticket CLI
class getticketcli(BaseHandler):
    def get(self):
        token = str(self.get_argument('token'))

        if self.check_api(token):
            user_id = int(self.db.get("select ID from users where api=%s",token)['ID'])
            tickets = self.db.query("select * from tickets where userID=%s",user_id)
            tickets_num = len(tickets)
            output = {
                'tickets':'There are -'+str(tickets_num)+'- Tickets',
                'code' : '200',
            }
            i=0
            for ticket in tickets:
                out = {
                    'subject' : ticket.title,
                    'body' : ticket.body,
                    'status' : getStatus(ticket.status),
                    'id' : ticket.ID,
                    'date': ticket.date.strftime("%Y-%m-%d %H:%M:%S"),
                }
                output['block '+str(i)] = out
                i+=1
            
            self.write(output)

        else:
            output = {
                'message':'Invalid token',
                'code':'401'
            }
            self.set_status(401)
            self.write(output)

class h(BaseHandler):
    def get(self):
        row = self.db.get("SELECT * from users where username = %s",'amir')
        self.write({'u':row['username']})

# Close Ticket
class closeticket(BaseHandler):
    def get(self):
        token = str(self.get_argument('token'))
        id = str(self.get_argument('id'))

        if self.check_api(token):
            self.db.execute("update tickets set status=2 where id=%s",id)
            output = {
                'message':'Ticket with id -'+id+'- Closed Successfully',
                'code':'200',
            }
            self.write(output)
        else:
            output = {
                'message':'Invalid token',
                'code':'401'
            }
            self.set_status(401)
            self.write(output)

class getticketmod(BaseHandler):
    def get(self):
        token = str(self.get_argument('token'))

        if self.check_api(token):
            if self.is_admin(token):
                tickets = self.db.query("select * from tickets")
                tickets_num = len(tickets)
                output = {
                    'tickets':'There are -'+str(tickets_num)+'- Tickets',
                    'code' : '200',
                }
                i=0
                for ticket in tickets:
                    out = {
                        'subject' : ticket.title,
                        'body' : ticket.body,
                        'status' : getStatus(ticket.status),
                        'id' : ticket.ID,
                        'date': ticket.date.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    output['block '+str(i)] = out
                    i+=1
                
                self.write(output)
            else:
                output = {
                'message':'Forbidden',
                'code':'403'
                }
                self.set_status(403)
                self.write(output)    
        else:
            output = {
                'message':'Invalid token',
                'code':'401'
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
