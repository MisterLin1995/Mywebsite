from flask import Flask,render_template, Markup,url_for, redirect
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
import pandas as pd
import datetime

def picpositioning(pics):
	tall=[]
	short=[]
	newpiclist=[]
	for pic in pics:
		if pic['width'] < pic['length']:
			tall.append(pic)
		else:
			short.append(pic)
	if len(tall)%2:
		tail=tall.pop()
	else:
		tail=0
	while tall:
		newpiclist.append(tall.pop(0))
		newpiclist.append(tall.pop(0))
		if short:
			newpiclist.append(short.pop(0))
	while short:
		newpiclist.append(short.pop(0))
	if tail:
		newpiclist.append(tail)
	return newpiclist
	
def create_app():
	app = Flask(__name__)
	Bootstrap(app)
	return app


@app.route('/index')
def cover():
    return render_template('cover2.html')

@app.route('/')
def index():
	return redirect('/index')

@app.route('/blog')
def blog():
	engine = create_engine('mysql+pymysql://username:password@127.0.0.1/databasename?charset=utf8',encoding = 'utf-8' )
	mysqlconn = engine.connect()
	posts = pd.read_sql("select post_id,title,subtitle,postDate from post limit 0,4",con=mysqlconn)
	mysqlconn.close()
	posts['postDate']=posts['postDate'].apply(lambda x:datetime.datetime.strftime(x,format('%Y-%m-%d')))
	posts=posts.to_dict(orient='records')
	return render_template('blog.html',posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
	engine = create_engine('mysql+pymysql://username:password@127.0.0.1/databasename?charset=utf8',encoding = 'utf-8' )
	mysqlconn = engine.connect()
	post = pd.read_sql("select * from post where post_id={0}".format(post_id),con=mysqlconn)
	post['postDate']=post['postDate'].apply(lambda x:datetime.datetime.strftime(x,format('%Y-%m-%d')))
	mysqlconn.close()
	return render_template('post.html',post=post.loc[0])

@app.route('/album')
def album():
	engine = create_engine('mysql+pymysql://username:password@127.0.0.1/databasename?charset=utf8',encoding = 'utf-8' )
	mysqlconn = engine.connect()
	photoInfo = pd.read_sql("select * from photoInfo;",con=mysqlconn)
	mysqlconn.close()
	photoInfo['takenTime']=photoInfo['takenTime'].apply(lambda x:datetime.datetime.strftime(x,format('%Y-%m-%d')))
	piclist=photoInfo.to_dict(orient='records')
	pics=picpositioning(piclist)
	return render_template('album.html',methods=['GET', 'POST'],pics=pics)

@app.route('/code')
def code():
	return redirect("https://code.mrlin.website",code=302)	

if __name__ == "__main__":
    app=create_app()
    app.run(host='0.0.0.0')
    
