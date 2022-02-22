import matplotlib.pyplot as plt
import cv2
import random
import os
from page_utils import Pagination

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from werkzeug.utils import secure_filename
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from keras_preprocessing.image import load_img, img_to_array
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, flash ,g
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

app = Flask(__name__)

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

basedir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\testpicture")  # 用户上传的图片都会先存进去
savedir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\savepicture")  # 预测结果大于80%的存进去

savedir2 = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\train2")  # 自己标的数据+原来的

label_dict = {0: 'airplane', 1: 'automobile', 2: 'bird', 3: 'cat', 4: 'deer', 5: 'dog', 6: 'frog', 7: 'horse',
              8: 'ship', 9: 'truck'}

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///F:\\1\\dachuang\\merge_two_text_before\\database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

traindir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\newlable")  # 用来训练的数据
testdir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\test")  # 用来测试的数据
olddir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\old-labled")

x_test = trainmodel.getx_test(testdir)  # x,y都是测试集来自F:\mini_cifar10\test
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

#文件上传数据库

class Files(db.Model):
    filenumber = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    userid = db.Column(db.Integer)
    picture_url = db.Column(db.String(100),unique=True)#先试试string类型能不能

   # return jsonify({'count': countlist, 'accuracy': losslist, 'single_lable': singlelist, 'double_lable': doublelist,
     #               'three_lable': threelist})

class Chart(db.Model):
    datanumber = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer)
    count = db.Column(db.Integer)
    loss = db.Column(db.Float)
    single = db.Column(db.Float)
    double = db.Column(db.Float)
    three = db.Column(db.Float)



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


# 选择哪个模型部分
@app.route('/choosepage')
@login_required
def choosepage():
    return render_template("choosepage.html", name=current_user.id)

@app.route('/start', methods=['GET', 'POST'])
def begin():
    return render_template("start.html")

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template("userprofile.html")




@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(user)
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)  # 有了这个之后才会变到choosepage 创建用户session
                return redirect(url_for('choosepage'))

        return '<h1>Invalid username or password</h1>'
        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

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


@app.route("/cifar10model", methods=["POST"])
@login_required
def begincifar10():
    return render_template("cifar10begin.html")


# cifar10模型部分
@app.route("/uploadcifar10picture", methods=['GET', 'POST'])
@login_required
def uploadcifar10():

    files = request.files.getlist('file')  # 这里面是可以随便写吗

    for file in files:
        filename = file.filename



        upload_path = os.path.join(basedir, secure_filename(filename))
        file.save(upload_path)  # 存testpicture

        img = load_img(upload_path, grayscale=False)
        img = np.array(img).reshape((1, 32, 32, 3))
        img = img.astype('float32') / 255

        predict = modelcifar10.predict(img)
        probablity = np.max(predict)

        predict = np.argmax(predict)
        result = format(label_dict[predict])

        if probablity >= 0.80:
            img_to_save = cv2.imread(upload_path)
            resultstr = str(result)
            save_path = os.path.join(savedir, resultstr)

            if os.path.isdir(save_path):

                cv2.imwrite(os.path.join(save_path, secure_filename(filename)), img_to_save)

            else:
                os.mkdir(save_path)
                cv2.imwrite(os.path.join(save_path, secure_filename(filename)), img_to_save)
        else:

            url = url_for("static", filename="images/testpicture/" + filename)

            print(url)

            print(probablity)
            ######################
            new_file = Files(userid=current_user.id, picture_url=url, filename=filename)
            db.session.add(new_file)
            db.session.commit()

            data = [url, result, probablity, filename]

            print(data)

            dataset.append(data)

    return render_template('cifar10begin.html', msg='图片上传成功')


@app.route("/begintoexersize", methods=['GET', 'POST'])  # post隐式提交，get显示提交
def predict():

    dataset1 = Files.query.filter_by(userid=current_user.id).all()
    print(dataset1)
    datasetfromdb = []
    for b in dataset1:
        data = [b.picture_url,b.filename]
        datasetfromdb.append(data)
    print(datasetfromdb)  # ["xx", "xx", "xx", "xx"]
    print(type(datasetfromdb))  # <class 'list'>


    pager_obj = Pagination(request.args.get("page", 1), len(datasetfromdb), request.path, request.args, per_page_count=8)
    print(request.path)
    print(request.args)


    indexlist = datasetfromdb[pager_obj.start:pager_obj.end]

    html = pager_obj.page_html()

    return render_template('test3.html', index_list=indexlist, html=html)


@app.route('/labelcifar10', methods=['GET', 'POST'])
@login_required
def labelcifar10():

    dataset1 = Files.query.filter_by(userid=current_user.id).all()
    print(dataset1)
    datasetfromdb = []
    for b in dataset1:
        data = [b.picture_url,b.filename,b.filenumber]
        datasetfromdb.append(data)
    print(datasetfromdb)  # ["xx", "xx", "xx", "xx"]
    print(type(datasetfromdb))  # <class 'list'>


    pager_obj = Pagination(request.args.get("page", 1), len(datasetfromdb), request.path, request.args, per_page_count=8)
    print(request.path)
    print(request.args)

    indexlist = datasetfromdb[pager_obj.start:pager_obj.end]

    labels = request.form.getlist('label')

    if labels:

        print(labels)
        print(indexlist)
        i = 0



        res = Chart.query.filter_by(userID=current_user.id).order_by(Chart.count.desc()).first()

        if res==None:
            count=0

        else:
            count=res.count

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

            save_path2 = os.path.join(save_path, photoname)
            datasetfromdb.remove(data)

            delete_data = Files.query.filter_by(filenumber=data[2]).one()
            db.session.delete(delete_data)
            db.session.commit()

            logger.info('user:{} labled {} as {} '.format(current_user.username, data[1], labels[i]))
            i=i+1
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

                shutil.move(save_path2, olddir)  # 这里有小bug olddir不能事先存在这里应该用个for循环，循环遍历一个文件夹


    model2 = load_model("VGG16.h5")

    eval = trainmodel.evaluate(model2, x_test, y_test, y_foracc)  # 返回的顺序是：损失函数有多大，单标签准确度，双标签准确度，三标签准确度


    new_chartdata = Chart(userID=current_user.id, count=count, loss=float(eval[0]),single=float(eval[1]),double=float(eval[2]),three=float(eval[3]))
    db.session.add(new_chartdata)
    db.session.commit()

    pager_obj = Pagination(request.args.get("page", 1), len(datasetfromdb), request.path, request.args, per_page_count=8)
    print(request.path)
    print(request.args)

    indexlist = datasetfromdb[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()

    return render_template('test3.html', index_list=indexlist, html=html, eval=eval)


@app.route('/data', methods=["GET", "POST"])
def data():
    model2 = load_model("VGG16.h5")

    eval = trainmodel.evaluate(model2, x_test, y_test, y_foracc)  # 返回的顺序是：损失函数有多大，单标签准确度，双标签准确度，三标签准确度

   #这里有小bug每次都加载最新的
    countlist = [0]
    losslist = [float(eval[0])]
    singlelist = [float(eval[1])]
    doublelist = [float(eval[2])]
    threelist = [float(eval[3])]

    data = Chart.query.filter_by(userID=current_user.id).first()
    if data:
        results = Chart.query.filter_by(userID=current_user.id).all()


        for one in results:
            countlist.append(one.count)
            losslist.append(one.loss)
            singlelist.append(one.single)
            doublelist.append(one.double)
            threelist.append(one.three)



    return jsonify({'count': countlist, 'accuracy': losslist, 'single_lable': singlelist, 'double_lable': doublelist,
                    'three_lable': threelist})


@app.route("/changelabelcifar10", methods=["POST"])
@login_required
def changelabelcifar10():
    return render_template("cifar10predictensure.html", name="wrong", name1="whatever")


if __name__ == '__main__':
    app.run(debug=True, threaded=False)  # 解决AttributeError: '_thread._local' object has no attribute 'value'
