from flask import Flask,request
import sqlite3
import json
from random import choice
from string import digits, ascii_lowercase
import datetime

app=Flask(__name__)
DATABASE='ewallet.db'
con = sqlite3.connect(DATABASE)
con.execute('''CREATE TABLE IF NOT EXISTS wallets (id TEXT PRIMARY KEY,balance INTEGER NOT NULL,coin_symbol TEXT NOT NULL);''')
con.execute('''CREATE TABLE IF NOT EXISTS transactions (from_wallet TEXT, to_wallet TEXT, amount INTEGER NOT NULL,time_stamp TEXT NOT NULL,txn_hash TEXT PRIMARY KEY,status TEXT NOT NULL, FOREIGN KEY(from_wallet) REFERENCES wallets(id),FOREIGN KEY(to_wallet) REFERENCES wallets(id));''')
con.close()

@app.route("/wallets", methods=['POST'])
def insertwallet():
	conn=sqlite3.connect(DATABASE)
	cur=conn.cursor()
	try:
		id=str(request.form['id'])
		balance=int(request.form['balance'])
		coin_symbol=str(request.form['coin_symbol'])
		cur.execute('''INSERT INTO wallets VALUES (?,?,?)''',(id,balance,coin_symbol))
		conn.commit()
		msg="Wallet Created"
		conn.close()
		return json.dumps({'msg':msg}),201
	except:
		conn.rollback()
		conn.close()
		msg="Error: Try Again with unique wallet id and all fields filled"
		return json.dumps({'msg':msg}),400


@app.route("/wallets/<id>", methods=['GET','DELETE'])
def getwallet(id):
	assert id==request.view_args['id']
	id=str(id)
	if request.method=='GET':
		conn=sqlite3.connect(DATABASE)
		cursor=conn.execute('''SELECT * FROM wallets WHERE id = ?''',(id,))
		wallet=cursor.fetchone()
		conn.close()
		if wallet==None:
			return json.dumps({'msg':'invalid ID'}),400
		return json.dumps({'id':id,'balance':wallet[1],'coin_symbol':wallet[2]}, indent=2),200

	if request.method=='DELETE':
		conn=sqlite3.connect(DATABASE)
		delete_wallet=conn.execute('''DELETE FROM wallets WHERE id LIKE ? ;''',(id,))
		conn.commit()
		conn.close()
		return json.dumps({'msg':'DELETED'}),204
#"".join([choice(chars) for i in range(2)])


@app.route("/txns",methods=['POST'])
def inserttxns():
	fwallet=str(request.form['from_wallet'])
	twallet=str(request.form['to_wallet'])
	amount=int(request.form['amount'])
	date=str(request.form['time_stamp'])
	status="pending"
	#chars = digits + ascii_lowercase
	txn_hash=str(request.form['txn_hash'])#"".join([choice(chars) for i in range(63)])
	conn=sqlite3.connect(DATABASE)
	cur=conn.cursor()
	try:
		cur.execute('''INSERT INTO transactions VALUES (?,?,?,?,?,?)''',(fwallet,twallet,amount,date,txn_hash,status))
		conn.commit()
		msg="transaction Created"
		conn.close()
		return json.dumps({'msg':msg}),201
	except:
		conn.rollback()
		conn.close()
		msg="Error: Try Again with all fields filled"
		return json.dumps({'msg':msg}),400


@app.route("/txns/<txn_hash>",methods=['GET'])
def gettxns(txn_hash):
	assert txn_hash==request.view_args['txn_hash']
	txn_hash=txn_hash
	conn=sqlite3.connect(DATABASE)
	cursor=conn.execute('''SELECT * FROM transactions WHERE txn_hash = ?''',(txn_hash,))
	txn=cursor.fetchone()
	conn.close()
	if txn==None:
		return json.dumps({'msg':'invalid hash'}),400
	return json.dumps({'from_wallet':txn[0],'to_wallet':txn[1],'amount':txn[2],'time_stamp':txn[3],'txn_hash':txn_hash,'status':txn[5]}, indent=2),200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

