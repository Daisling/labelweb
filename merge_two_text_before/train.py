
import trainmodel
import os
from tensorflow.keras.models import load_model
import os, shutil
modelcifar10 = load_model('VGG16.h5')
modelpath = "VGG.h5"
traindir = os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\train2")  # 用来训练的数据
olddir=os.path.abspath(r"F:\1\dachuang\merge_two_text_before\static\images\old-labled")
x_train = trainmodel.newx_train(traindir)
y_train = trainmodel.newy_train(traindir)

trainmodel.re_train(x_train, y_train, modelcifar10, modelpath)
shutil.move(traindir, olddir)