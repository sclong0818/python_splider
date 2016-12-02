# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import os

class File_Tool:
    def createFile(self,save_path,filename):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, filename)
        if not os.path.exists(file_path):
            _file = open(file_path,'a+')
            _file.close()
            return file_path
        else:
            # 已存在同名文件
            return ''

    def saveImg(self,saveroot,subpath,filename,imgurl):
        save_path = os.path.join(saveroot,subpath)
        file_path = self.createFile(save_path,filename)
        if file_path:
            urllib.urlretrieve(imgurl,file_path,None)
