# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import pymysql

dict1={}
def singleton(func):
	def inner(*args,**kwargs):
		temp = dict1.setdefault(func,[])
		if len(temp) < 2:
			temp.append(func(*args,**kwargs))
		# if func not in dict1:
		# 	dict1[func] = func(*args,**kwargs)
		return dict1[func]
	return inner

@singleton
class Mysql(object):
	def __init__(self,host,user,passwd,port,db,charset):
		self.connect = pymysql.Connect(host=host,user=user,passwd=passwd,port=port,db=db,charset=charset)
		self.cursor = self.connect.cursor()
		
	def change_data(self,*args):
		self.cursor.execute(*args)
		self.connect.commit()
	
	def select_data(self,*args):
		# type: (object) -> object
		self.cursor.execute(*args)
		return self.cursor.fetchall()
	
	def close(self):
		self.cursor.close()
		self.connect.close()
	