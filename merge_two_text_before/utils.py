import os

# importing shutil module
import shutil

def move_file(orgin_path, moved_path):
   dir_files = os.listdir(orgin_path)  # 得到该文件夹下所有的文件
   for file in dir_files:
       file_path = os.path.join(orgin_path, file)  # 路径拼接成绝对路径
       if os.path.isfile(file_path):  # 如果是文件，就打印这个文件路径
           # if file.endswith(".txt"):
               if os.path.exists(os.path.join(moved_path, file)):
                   print("有重复文件！！覆盖！！！")

                   os.remove(os.path.join(moved_path, file))

               shutil.move(file_path, moved_path)
       if os.path.isdir(file_path):  # 如果目录，就递归子目录
           move_file(file_path, moved_path)
   print("移动文件成功！")
