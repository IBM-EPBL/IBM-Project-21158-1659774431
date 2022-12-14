from flask import Flask, render_template, request, redirect, url_for, session,flash
import os
import ibm_db
from flask_mail import Mail, Message

conn= ibm_db.connect("DATABASE=bludb;HOSTNAME=55fbc997-9266-4331-afd3-888b05e734c0.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31929;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=qgl08366;PWD=HeV8ElaxRSImwZ5F",'','')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get('SENDGRID_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
mail = Mail(app)


@app.route("/",methods=['GET'])
def home():
  print(os.environ.get('MAIL_DEFAULT_SENDER'))
  if 'email' not in session:
    return redirect(url_for('login'))
  return render_template('home.html',name='Home')


@app.route("/Donorabout",methods=['GET'])
def Donorabout():
  return render_template('Donorabout.html')


@app.route("/Recepientabout",methods=['GET'])
def Recepientabout():
  return render_template('Recepientabout.html')


@app.route("/Donorhome",methods=['GET'])
def Donorhome():
  return render_template('Donorhome.html')

@app.route("/Recepienthome",methods=['GET'])
def Recepienthome():
  return render_template('Recepienthome.html')



@app.route("/register",methods=['GET','POST'])
def register():
  if request.method == 'POST':

    try:
      email = request.form['email']
      username = request.form['username']
      password = request.form['password']
      userType = request.form['type']
      if not email or not username or not password:
        return render_template('register.html',error='Please fill all fields')
      
      #hash=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

      query = "SELECT * FROM USERS WHERE Email=?"
      stmt = ibm_db.prepare(conn, query)
      ibm_db.bind_param(stmt,1,email)
      ibm_db.execute(stmt)
      isUser = ibm_db.fetch_assoc(stmt)
      
      print("entering1")
      if not isUser:
        insert_sql = "INSERT INTO Users(Name,email,PASSWORD,usertype) VALUES (?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, password)
        ibm_db.bind_param(prep_stmt, 4, userType)
        ibm_db.execute(prep_stmt)
        # print("entering2")


        return render_template('register.html',success="You can login")
      else:
        return render_template('register.html',error='Invalid Credentials')

    except Exception as e:
      print("error",e)

  return render_template('register.html',name='Home')

@app.route("/login",methods=['GET','POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']

    if not email or not password:
      return render_template('login.html',error='Please fill all fields')
    query = "SELECT * FROM USERS WHERE Email=?"
    stmt = ibm_db.prepare(conn, query)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    isUser = ibm_db.fetch_assoc(stmt)
    print(isUser,password)

    # userType = isUser.USERTYPE
    print("## ",isUser["USERTYPE"])

    if(isUser and isUser["USERTYPE"].strip()=="Donor"):
      return render_template('Donorhome.html',error='Invalid Credentials')

    if(isUser and isUser["USERTYPE"].strip()=="Recepient"):
      return render_template('Recepienthome.html',error='Invalid Credentials')

    if not isUser:
      return render_template('login.html',error='Invalid Credentials')
      
    #isPasswordMatch = bcrypt.checkpw(password.encode('utf-8'),isUser['PASSWORD'].encode('utf-8'))

    #if not isPasswordMatch:
    if(isUser['PASSWORD']!=password):
      return render_template('login.html',error='Invalid Credentials')

    session['email'] = isUser['EMAIL']
    return redirect(url_for('home'))

  return render_template('login.html',name='Home')


@app.route('/logout')
def logout():
  session.pop('email', None)
  return redirect(url_for('login'))




@app.route('/request',methods=['GET','POST'])
def req():
  if request.method == 'GET':
    return render_template('request.html',name='request')
  email = request.form['email']
  name = request.form['Name']
  phone = request.form['phone']
  BloodGroupReq = request.form['BloodGroup']
  Address = request.form['Address']
  #to_email = To(email)
  print(email,name,phone,BloodGroupReq,Address)
  query = "SELECT * FROM DONORS WHERE BloodGroup=?"
  stmt = ibm_db.prepare(conn, query)
  ibm_db.bind_param(stmt,1,BloodGroupReq)
  ibm_db.execute(stmt)
  ll = ibm_db.fetch_assoc(stmt)
  if(ll):
    listt = []
    while(ll!=False):
      listt.append(ll)
      ll = ibm_db.fetch_assoc(stmt)
    print(listt)

    donor_list = []
    for i in listt:
        donor_list.append(i["EMAIL"])

    try:  
      msg = Message('Urgent!! Plasma needed!!', recipients=donor_list)
      
      content = "This email is sent from Plasma Donor Application! \n"+"Request for plasma was made by: \n"+"Name: "+name+"\n Email: "+email+"\n Phone: "+phone+"\n Address: "+Address+"\n Please contact for further communications!"
      
      msg.body = content
      msg.html = f'<p>This email is sent from Plasma Donor Application!</p> \n <p>Request for plasma was made by: {name}</p> \n <p>Phone number: {phone}</p>\n <p>Address: {Address}</p> '
      mail.send(msg)
      print("mail successfully sent")
    except Exception as e:
      print("error: ",e)
    	
    return render_template('reqReplyS.html',name='reqReplyS',total=len(listt))
  else:  
    return render_template('reqReplyF.html',name='reqReplyF')


@app.route('/donate',methods=['GET','POST'])
def donate():
  if request.method == 'GET':
    return render_template('donate.html',name='donate')
  email = request.form['email']
  name = request.form['Name']
  phone = request.form['phone']
  BloodGroup = request.form['BloodGroup']
  Address = request.form['Address']
  print(email,name,phone,BloodGroup,Address)
  insert_sql = "INSERT INTO DONORS(Name,email,PHONE,BloodGroup,Address) VALUES (?,?,?,?,?)"
  prep_stmt = ibm_db.prepare(conn, insert_sql)
  ibm_db.bind_param(prep_stmt, 1, name)
  ibm_db.bind_param(prep_stmt, 2, email)
  ibm_db.bind_param(prep_stmt, 3, phone)
  ibm_db.bind_param(prep_stmt, 4, BloodGroup)
  ibm_db.bind_param(prep_stmt, 5, Address)
  ibm_db.execute(prep_stmt)
  return render_template('donSuccess.html',name='donSuccess')

@app.route('/stats',methods=['GET','POST'])
def stats():
  if request.method == 'GET':
    return render_template('stats.html',total=0,flag=1)
  email = request.form['email']
  query = "SELECT * FROM DONORS WHERE email=?"
  stmt = ibm_db.prepare(conn, query)
  ibm_db.bind_param(stmt,1,email)
  ibm_db.execute(stmt)
  ll = ibm_db.fetch_assoc(stmt)
  listt = []
  if(ll):
    while(ll!=False):
      listt.append(ll)
      ll = ibm_db.fetch_assoc(stmt)
    print(listt)
  return render_template('stats.html',total=len(listt),flag=0)

app.debug = True

if __name__ == "__main__":
  app.run(host="0.0.0.0")
