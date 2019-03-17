import sys,platform,os
import requests,time
import re

API_KEY=''
USERNAME=''
PASSWORD=''
def __api__(command,query_string):
    return 'http://localhost:6060/' + command + '?' + query_string



def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
       os.system('clear')

def menu():
    print("Hi, "+USERNAME+". Your API_KEY : " + API_KEY)
    print("""What Do You Prefer To Do :
    1. Send Ticket
    2. See Last Tickets
    3. Close a Ticket
    4. Logout
    5. Exit
    """)


while True:
    clear()
    print("""Hi, Please choose :
    1.Login
    2.Signup
    3.Exit""")

    choice = sys.stdin.readline()
    
    if choice[:-1] == '1':
        while True:
            print("Username:")
            username = sys.stdin.readline()
            print("Password:")
            password = sys.stdin.readline()
            qs = 'username='+username+'&password='+password
            res = requests.get(__api__('login',qs)).json()
            if res['code'] == '401':
                print("Invalid username or password")
                time.sleep(1)
                clear()
                continue
            elif res['code'] == '200':
                print("Your successfully logged in...")
                API_KEY = res['token']
                USERNAME= username
                PASSWORD = password
                time.sleep(1)
                break
        while True:
            clear()
            menu()
            choice = sys.stdin.readline()[:-1]
            if choice == '1':
                clear()
                print("Subject:")
                subject = sys.stdin.readline()
                print("Body:")
                body = sys.stdin.readline()
                qs = 'subject='+subject+'&body='+body+'&token='+API_KEY
                res = requests.get(__api__('sendticket',qs)).json()
                if res['code'] == '200':
                    print(res['message'])
                    print('id : '+str(res['id']))
                    time.sleep(2)
                    continue
            if choice == '2':
                clear()
                qs = 'token='+API_KEY
                res = requests.get(__api__('getticketcli',qs)).json()
                if res['code'] == '200':
                    print(res['tickets'])
                    print('----------------')
                    for i in range(int(re.findall(r'\d+',res['tickets'])[0])):
                        print('Subject : '+res['block '+str(i)]['subject'])
                        print('Body : '+res['block '+str(i)]['body'])
                        print('Status : '+res['block '+str(i)]['status'])
                        print('Id : '+str(res['block '+str(i)]['id']))
                        print('Date : '+res['block '+str(i)]['date'])
                        print('----------------')
                    print("press enter to return")
                    sys.stdin.readline()
            if choice == '3':
                clear()
                print('Please enter the ticket id:')
                id = sys.stdin.readline()
                qs = 'token='+API_KEY+'&id='+str(id)
                res = requests.get(__api__('closeticket',qs)).json()
                if res['code'] == '200':
                    print(res['message'])
                    time.sleep(2)
            if choice == '4':
                qs = 'username='+USERNAME+'&password='+PASSWORD
                res = requests.get(__api__('logout',qs)).json()
                
                if res['code'] == '200':
                    print(res['message'])
                    API_KEY = ''
                    USERNAME = ''
                    PASSWORD = ''
                    time.sleep(1)
                    break
            if choice == '5':
                sys.exit()

    elif choice[:-1] == '2':
        while True:
            print("Username*:")
            username = sys.stdin.readline()
            print("Password*:")
            password = sys.stdin.readline()
            print("First Name:")
            fname = sys.stdin.readline()
            print("Last Name:")
            lname = sys.stdin.readline()
            qs = 'username='+username+'&password='+password+'&firstname='+fname+'&lastname='+lname
            res = requests.get(__api__('signup',qs)).json()
            if res['code'] == '406':
                print("User already exists")
                continue
            elif res['code'] == '200':
                print("Signed up successfully, you can login now...")
                time.sleep(2)
                break
    elif choice[:-1] == '3':
        sys.exit()
        
