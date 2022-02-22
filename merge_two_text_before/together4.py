import matplotlib.pyplot as plt
import cv2
import random
import os
import json
from page_utils import Pagination
from utils import move_file
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from werkzeug.utils import secure_filename
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from keras_preprocessing.image import load_img, img_to_array
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, flash, g
from flask_bootstrap import Bootstrap
import trainmodel  # 一些函数在这个文件里

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import logging  # 日志记录
import os, shutil

import sqlite3

import calendar;
import time;


app = Flask(__name__)
#下面这些应该是关于log的
#######################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

file_handler = logging.FileHandler('sample.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

#######################################


label_dict = {0: 'airplane', 1: 'automobile', 2: 'bird', 3: 'cat', 4: 'deer', 5: 'dog', 6: 'frog', 7: 'horse',
              8: 'ship', 9: 'truck'}

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///F:\\1\\dachuang\\merge_two_text_before\\database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
#管理用户登录的；
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

basedir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\testpicture")  # 用户上传的图片都会先存进去

traindir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\newlable")  # 用来训练的数据
testdir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\test")  # 用来测试的数据
olddir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\old-labled")

x_test = trainmodel.getx_test(testdir)  # x,y来自F:\mini_cifar10\test
y_test = trainmodel.gety_test(testdir)

y_foracc = trainmodel.gety_foracc(y_test)

modelcifar10 = load_model('VGG16.h5')
modelpath = "VGG.h5"

dataset = []

##############以下用于图表
count = 0  # 用户标注次数
global countlist
countlist = [0]

global losslist
losslist = []
global singlelist
singlelist = []
global doublelist
doublelist = []
global threelist
threelist = []


##############


##############

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


# 文件上传数据库

class Files(db.Model):
    filenumber = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    userid = db.Column(db.Integer)
    picture_url = db.Column(db.String(100), unique=True)  # 先试试string类型能不能


class Chart(db.Model):
    datanumber = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer)
    count = db.Column(db.Integer)
    loss = db.Column(db.Float)
    single = db.Column(db.Float)
    double = db.Column(db.Float)
    three = db.Column(db.Float)


# 商家上传数据库
class Work(db.Model):
    workID = db.Column(db.Integer, primary_key=True)
    cover = db.Column(db.String(100))
    userID = db.Column(db.Integer)
    isfinish = db.Column(db.Integer)
    isacceptall = db.Column(db.Integer)
    workfile = db.relationship('Workfile', backref=db.backref('work'))


class Workfile(db.Model):
    filenumber = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    picture_url = db.Column(db.String(100), unique=True)
    workID = db.Column(db.Integer, db.ForeignKey('work.workID'))
    workIDofuser = db.Column(db.Integer, db.ForeignKey('stateofwork.workIDofuser'))


class Fileofuser(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    workID = db.Column(db.Integer)
    picture_url = db.Column(db.String(100), unique=True)
    filename = db.Column(db.String(50))
    userID = db.Column(db.Integer)
    workIDofuser = db.Column(db.Integer)

class Stateofwork(db.Model):
    workIDofuser = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer)
    state = db.Column(db.Integer)
    cover = db.Column(db.String(100))

    workID = db.Column(db.Integer)
    workfileofuser = db.relationship('Workfile', backref=db.backref('stateofwork'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('用户', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('密码', validators=[InputRequired(), Length(min=8, max=80)])


class RegisterForm(FlaskForm):
    email = StringField('邮箱', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('用户', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('密码', validators=[InputRequired(), Length(min=8, max=80)])

@app.route('/start', methods=['GET', 'POST'])
@login_required
def begin():
    workset = Work.query.all()

    worksetfromdb = []
    for b in workset:
        data = [b.workID, b.cover, b.isacceptall]
        worksetfromdb.append(data)
    print(worksetfromdb)  # ["xx", "xx", "xx", "xx"]


    return render_template("start.html", workset=worksetfromdb)


# 选择哪个模型部分
@app.route('/choosepage/<workid>', methods=['GET', 'POST'])
@login_required
def choosepage(workid):

    #假设商家设置的每个uwork的文件数量为10

    filenumofuwork = 10

    workfiles = Workfile.query.filter_by(workID=workid).all()
    work = Work.query.filter_by(workID=workid).first()
    cover = work.cover
    print(cover)

    ts = calendar.timegm(time.gmtime())
    i = 0
    j = 0

    for b in workfiles:
        if b.workIDofuser:
            i=i+1
            continue
        else:
            j=j+1
            i=i+1
            url=b.picture_url
            filename=b.filename
            workidofuser = int (str(workid)+str(current_user.id)+str(ts)) #同一个用户接同一个商家的任务会报错 #改了，加了时间戳
            print(workidofuser)
            b.workIDofuser=workidofuser
            new_file = Fileofuser(userID=current_user.id, picture_url=url, filename=filename,workID=workid,workIDofuser=workidofuser)
            db.session.add(new_file)
            db.session.commit() #这个好像只用提交一次？
            if j==10:
                break
    if i==len(workfiles):
        work.isacceptall=1

    new_work = Stateofwork(userID=current_user.id, state=0, cover=cover, workIDofuser=workidofuser, workID=workid)
    db.session.add(new_work)
    db.session.commit()


    return render_template("choosepage2.html", name2=workidofuser, name1=current_user.username)



@app.route("/begintoexersize/<workidofuser>", methods=['GET', 'POST'])  # post隐式提交，get显示提交
def predict(workidofuser):


    print(workidofuser)
    dataset1 = Fileofuser.query.filter_by(workIDofuser=workidofuser).all()
    print(dataset1)
    datasetfromdb = []
    for b in dataset1:
        data = [b.picture_url, b.filename]
        datasetfromdb.append(data)
    print(datasetfromdb)  # ["xx", "xx", "xx", "xx"]
    print(type(datasetfromdb))  # <class 'list'>

    pager_obj = Pagination(request.args.get("page", 1), len(datasetfromdb), request.path, request.args,
                           per_page_count=8)
    print(request.path) #/begintoexersize
    print(request.args)

    indexlist = datasetfromdb[pager_obj.start:pager_obj.end]

    html = pager_obj.page_html()

    widu = workidofuser

    dataset2 = Stateofwork.query.filter_by(workIDofuser=workidofuser).first()
    state = dataset2.state

    return render_template('test3.html', index_list=indexlist, html=html, name=widu, name2=state)







@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    stateofworks = Stateofwork.query.filter_by(userID=current_user.id).all()
    dataset=[]
    for w in stateofworks:
        if w.state==0:
            data = [w.cover, w.workIDofuser]
            dataset.append(data)

    return render_template("userprofile2.html", data=dataset)

@app.route('/chart', methods=['GET', 'POST'])
@login_required
def chart():
    return render_template("chart.html")

@app.route('/setting', methods=['GET', 'POST'])
@login_required
def setting():
    return render_template("setting.html")

@app.route('/record', methods=['GET', 'POST'])
@login_required
def record():
    return render_template("record.html")


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(user)
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)  # 有了这个之后才会变到choosepage 创建用户session
                return redirect(url_for('begin'))  # 这里写的要是函数名

        return '<h1>Invalid username or password</h1>'

    return render_template('login2.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return render_template('warn.html')

    return render_template('signup2.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')



#用户上传标签部分

@app.route('/labelcifar10/<workidofuser>', methods=['GET', 'POST'])
@login_required
def labelcifar10(workidofuser):
    dataset1 = Fileofuser.query.filter_by(workIDofuser=workidofuser).all()
    print(dataset1)
    datasetfromdb = []
    for b in dataset1:
        data = [b.picture_url, b.filename, b.ID]
        datasetfromdb.append(data)
    print(datasetfromdb)  # ["xx", "xx", "xx", "xx"]
    print(type(datasetfromdb))  # <class 'list'>

    pager_obj = Pagination(request.args.get("page", 1), len(datasetfromdb), request.path, request.args,
                           per_page_count=8)
    print(request.path)
    print(request.args)

    indexlist = datasetfromdb[pager_obj.start:pager_obj.end]

    labels = request.form.getlist('label')

    if labels: #这里有bug只能按着顺序标

        print(labels)
        print(indexlist)
        i = 0

        res = Chart.query.filter_by(userID=current_user.id).order_by(Chart.count.desc()).first()

        if res == None:
            count = 0

        else:
            count = res.count

        print("count:{}".format(count))

        for data in indexlist:

            upload_path = os.path.join(basedir, secure_filename(data[1]))

            img_to_save = cv2.imread(upload_path)

            save_path = os.path.join(traindir, labels[i])

            photoname = data[1]

            if os.path.isdir(save_path):
                cv2.imwrite(os.path.join(save_path, photoname), img_to_save)
            else:
                os.makedirs(save_path)
                cv2.imwrite(os.path.join(save_path, photoname), img_to_save)



            datasetfromdb.remove(data)

            delete_data = Fileofuser.query.filter_by(ID=data[2]).one()
            db.session.delete(delete_data)
            db.session.commit()

            logger.info('user:{} labled {} as {} '.format(current_user.username, data[1], labels[i]))
            i = i + 1
            print('i的值为：{}'.format(i))

            count = count + 1
            print('count:{}'.format(count))
            print('lengthlen:{}'.format(len(indexlist)))
            if i == len(indexlist):
                countlist.append(count)
                print(countlist)

                x_train = trainmodel.newx_train(traindir)
                y_train = trainmodel.newy_train(traindir)

                trainmodel.re_train(x_train, y_train, modelcifar10, modelpath)

                #shutil.move(save_path2, olddir)  # 这里有小bug olddir不能事先存在这里应该用个for循环，循环遍历一个文件夹
                move_file(traindir,olddir)

    model2 = load_model("VGG16.h5")

    eval = trainmodel.evaluate(model2, x_test, y_test, y_foracc)  # 返回的顺序是：损失函数有多大，单标签准确度，双标签准确度，三标签准确度

    new_chartdata = Chart(userID=current_user.id, count=count, loss=float(eval[0]), single=float(eval[1]),
                          double=float(eval[2]), three=float(eval[3]))
    db.session.add(new_chartdata)
    db.session.commit()

    pager_obj = Pagination(request.args.get("page", 1), len(datasetfromdb), request.path, request.args,
                           per_page_count=8)
    print(request.path)
    print(request.args)

    indexlist = datasetfromdb[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()
    temp = 0
    if datasetfromdb==[]:
        stateset = Stateofwork.query.filter_by(workIDofuser=workidofuser).first()
        stateset.state = 1
        temp = stateset.state
        db.session.commit()
    print(temp)
    return render_template('test3.html', index_list=indexlist, html=html, eval=eval, name=workidofuser, name2=temp)


@app.route('/data', methods=["GET", "POST"])
def data():
    model2 = load_model("VGG16.h5")



    countlist = []
    losslist = []
    singlelist = []
    doublelist = []
    threelist = []


    data = Chart.query.filter_by(userID=current_user.id).first()
    if data:
        results = Chart.query.filter_by(userID=current_user.id).all()

        for one in results:
            countlist.append(one.count)
            losslist.append(one.loss)
            singlelist.append(one.single)
            doublelist.append(one.double)
            threelist.append(one.three)
    else:
        count = 0
        eval = trainmodel.evaluate(model2, x_test, y_test, y_foracc)  # 返回的顺序是：损失函数有多大，单标签准确度，双标签准确度，三标签准确度
        new_chartdata = Chart(userID=current_user.id, count=count, loss=float(eval[0]), single=float(eval[1]),
                              double=float(eval[2]), three=float(eval[3]))
        db.session.add(new_chartdata)
        db.session.commit()

        countlist = [0]
        losslist = [float(eval[0])]
        singlelist = [float(eval[1])]
        doublelist = [float(eval[2])]
        threelist = [float(eval[3])]

    return jsonify({'count': countlist, 'accuracy': losslist, 'single_lable': singlelist, 'double_lable': doublelist,
                    'three_lable': threelist})



if __name__ == '__main__':
    app.run(debug=True, threaded=False)  # 解决AttributeError: '_thread._local' object has no attribute 'value'
