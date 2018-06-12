import MySQLdb
from flask import Flask, request, Response ,jsonify,render_template,session
import json
import pyqrcode
import shutil
import message
app = Flask(__name__)
app.secret_key = 'randomstring'


@app.route('/signup',methods=['GET'])
def signup():
	return render_template('signup.html')

@app.route('/success',methods=['GET'])
def success():
	db = MySQLdb.connect("localhost","root","","movie" )
	cursor = db.cursor()
	cursor.execute("SELECT name from user1 where mobile_no='{}'".format(session['mobile_no']))
	name = cursor.fetchone()[0]
	cursor.execute("SELECT money from wallet where mobile_no='{}'".format(session['mobile_no']))
	money = cursor.fetchone()[0]
	return render_template('ind.html',name=name,money=money,mobile_no=session['mobile_no'])

@app.route('/register',methods=['POST'])
def register():
	'''
		TODO: Create a entry in wallet for this user wis

	'''
	password = request.form['password']
	email = request.form['email']
	name = request.form['name']
	mobile_no = request.form['mobile_no']

	# otp= message.generateOTP(mobile)
	# session[otp]=lpno

	db = MySQLdb.connect("localhost","root","","movie" )
	cursor = db.cursor()
	sql= "INSERT INTO user1(name,password,email,mobile_no) VALUES('"+name+"','"+password+"','"+email+"','"+mobile_no+"')"
	pwd = cursor.execute(sql)
	if(pwd):
		sql= "INSERT INTO wallet(mobile_no,money) VALUES('"+mobile_no+"',50)"
		cursor.execute(sql)
		db.commit()
		db.close()
	return render_template('login.html')

@app.route('/Loginotp',methods=['POST'])
def otps():
	otp = request.form['otp']
	if str(otp) in session:
		return render_template('')

@app.route('/',methods=['GET'])
@app.route('/login',methods=['GET'])
def login():
	return render_template('login.html')


@app.route('/register1', methods = ['POST'])
def register1():
	
	password = request.form['password']
	mobile_no = request.form['mobile_no']
	session['mobile_no'] = str(mobile_no)
	db = MySQLdb.connect("localhost","root","","movie")
	cursor = db.cursor()
	cursor.execute("SELECT name,mobile_no from user1 where mobile_no='"+mobile_no+"' and password='"+password+"'")
	pwd = cursor.fetchone()
	if pwd:
		name=pwd[0]
		mobile_no = pwd[1]
		cursor.execute("SELECT money from wallet where mobile_no='{}'".format(mobile_no))
		money = cursor.fetchone()[0]	
		return  render_template('ind.html',name=name,money=money,mobile_no=mobile_no)
	else:
		return redirect('/404')

@app.route('/ind',methods=['GET'])
def ind():
	return render_template('ind.html')

@app.route('/addmoney',methods=['GET'])
def addmoney():
	return render_template('add.html')

@app.route('/add', methods = ['POST'])
def add():
        money = request.form['money']
        mobile_no = session['mobile_no']
        session['money']=str(money)
        db = MySQLdb.connect("localhost","root","","movie")
        cursor = db.cursor()
        cursor.execute("UPDATE wallet set money=money+'"+money+"' where mobile_no='"+mobile_no+"'")
        db.commit()
        db.close()
        return render_template('card.html')

@app.route('/recharge',methods=['GET'])
def recharge():
	return render_template('recharge.html')

@app.route('/rechar', methods = ['POST'])
def rechar():
        mobile_no = request.form['mobile_no']
        amt=request.form['amt']
        db = MySQLdb.connect("localhost","root","","movie")
        cursor = db.cursor()
        y=session['mobile_no']
        cursor.execute("SELECT money from wallet where mobile_no='"+y+"'")
        x=cursor.fetchone()
        if int(x[0])>int(amt):
        	sq="INSERT INTO recharge(receiver,sender,amt) VALUES ('"+mobile_no+"','"+session['mobile_no']+"','"+amt+"')"
        	cursor.execute(sq)
        	cursor.execute("UPDATE wallet set money=money-'"+amt+"' where mobile_no='"+session['mobile_no']+"'")
        	return render_template('rechsuccess.html',money=amt)
        else:
        	return render_template('rechfailure.html')
        db.commit()
        db.close()
        # return "The person with mobile number " +str(session['mobile_no'])+ " recharged " +str(mobile_no)+ " with Rs " +str(amt)


@app.route('/pay',methods=['GET'])
def pay():
	return render_template('pay.html')
@app.route('/payu', methods = ['POST'])
def payu():
	mobile_no = request.form['mobile_no']
	amt=request.form['amt']
	db = MySQLdb.connect("localhost","root","","movie")
	cursor = db.cursor()
	y=session['mobile_no']
	cursor.execute("SELECT money from wallet where mobile_no='"+y+"'")
	x=cursor.fetchone()
	if int(x[0])>int(amt): 
		cursor.execute("UPDATE wallet set money=money+'"+amt+"' where mobile_no='"+mobile_no+"'")
		cursor.execute("UPDATE wallet set money=money-'"+amt+"' where mobile_no='"+session['mobile_no']+"'")
		cursor.execute("INSERT into transaction(destination,source,money) VALUES('"+mobile_no+"','"+session['mobile_no']+"','"+amt+"')")
		return render_template('paysuccess.html',money=amt)
	else:
		return render_template('rechfailure.html')
	db.commit()
	db.close()
	
@app.route('/passbook',methods=['GET'])
def passbook():
	return render_template('passbook.html')
@app.route('/pass',methods=['GET'])
def passb():
	db = MySQLdb.connect("localhost","root","","movie")
	cursor = db.cursor()
	cursor.execute("SELECT * FROM transaction where source='"+session['mobile_no']+"'")
	result=cursor.fetchall()
	items=[]
	if(result):
		for row in result:
			r = {'destination':str(row[1]),'source':str(row[2]),'money':str(row[3])}
			items.append(r)
	return jsonify(items)

@app.route('/cardmoney',methods=['GET'])
def cardmoney():
	return render_template('card.html')

@app.route('/card', methods = ['POST'])
def card():
        cardno = request.form['cardno']
        cvv = request.form['cvv']
        money= session['money']
        db = MySQLdb.connect("localhost","root","","movie")
        cursor = db.cursor()
        sql="INSERT INTO card(cardno,cvv) VALUES ('"+cardno+"','"+cvv+"')"
        cursor.execute(sql)
        db.commit()
        db.close()
        return render_template('success.html',money=money)
@app.route('/trans',methods=['GET'])
def trans():
	cursor = db.cursor()
	cursor.execute("SELECT money,date FROM transaction where source='"+session['mobile_no']+"'")
	result=cursor.fetchall()
@app.route('/qr/<receiver>/')
def qrc(receiver):
	return render_template('qr.html')

@app.route('/qr/<receiver>/payy',methods=['POST'])
def qr(receiver):
	password = request.form['password']
	mobile_no = request.form['mobile_no']
	amt = request.form['amt']
	db = MySQLdb.connect("localhost","root","","movie")
	cursor = db.cursor()
	cursor.execute("SELECT * from user1 where mobile_no='"+mobile_no+"' and password='"+password+"'")
	pwd = cursor.fetchone()
	if pwd:
		cursor.execute("SELECT money from wallet where mobile_no='"+mobile_no+"'")
		x=cursor.fetchone()
		if int(x[0])>int(amt): 
			cursor.execute("UPDATE wallet set money=money+'"+amt+"' where mobile_no='"+receiver+"'")
			cursor.execute("UPDATE wallet set money=money-'"+amt+"' where mobile_no='"+mobile_no+"'")
			cursor.execute("INSERT into transaction(destination,source,money) VALUES('"+receiver+"','"+mobile_no+"','"+amt+"')")
			return render_template('paysuccess.html',money=amt)
		else:
			return render_template('rechfailure.html')
	db.commit()
	db.close()
	

@app.route('/accept',methods=['GET'])
def accept():
	mobile_no = session['mobile_no']
	q = pyqrcode.create('http://192.168.43.215:5000/qr/'+mobile_no)
	q.png(''+mobile_no+'.png',scale=8)
	shutil.move("E:/Code/Ecommerce/Ankita/"+mobile_no+".png", "E:/Code/Ecommerce/Ankita/static/"+mobile_no+".png")
	mobile ={'mobile_no':mobile_no+".png"}
	return render_template('accept.html',mobile=mobile)

if __name__=="__main__":
        app.run(host="192.168.43.215",port=5000,debug=True)