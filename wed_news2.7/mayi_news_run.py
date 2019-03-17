# coding:utf-8
from mayi_news_bp import news_run
from flask import Flask
from flask_apscheduler import APScheduler  # 引入APScheduler
from mayi_news_bp.news_spider import spider_run


class Config(object):  # 创建配置，用类
	JOBS = [
		{
			'id': 'job1',
			'func': '__main__:spider_run',
			'args': None,
			'trigger': 'interval',
			'minutes': 30,
		}
	]


# 任务字典
# 其中id是一个标识，func指定定时执行的函数，args指定输入参数列表，trigger指定任务类型，如interval表示时间间隔。seconds表示时间周期，单位是秒。

app = Flask(__name__)
app.register_blueprint(news_run.bp)  # 注册蓝图

app.config.from_object(Config())  # 为实例化的flask引入配置

app.secret_key = 'abcdef123456'

if __name__ == '__main__':
	scheduler = APScheduler()  # 实例化APScheduler
	scheduler.init_app(app)  # 把任务列表放进flask
	scheduler.start()  # 启动任务列表
	app.run(host='0.0.0.0', port=10000, debug=True)
