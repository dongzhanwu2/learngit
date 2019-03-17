# coding:utf-8
import datetime
import re
import database, random
from flask import render_template, redirect, request, session, Blueprint
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

db = database.Mysql('127.0.0.1', 'root', 'Mroot@123', 3306, 'mayi_news', 'utf8')[0]

bp = Blueprint('mayi_news',__name__,static_folder='static_folder',template_folder='templates')

@bp.route('/')
def news_page1():
    sql = "select e_name,c_name from classes_tb "
    classes_result = db.select_data(sql)
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    sq_t = "(select * from news_tb where create_time like '%s%%')" % date
    sql = "select A.id,A.title,B.e_name from %s A,classes_tb B where A.classes=B.id order by rand() limit 10" % sq_t
    data2 = db.select_data(sql)
    sql = "select A.id,A.title,B.e_name from news_tb A,classes_tb B where A.classes=B.id order by order_id DESC limit 10"
    data1 = db.select_data(sql)
    grade = session.get('grade')
    user_name = session.get('username')
    return render_template('news_page1.html', data=classes_result, data1=data1, data2=data2, grade=grade,
                           username=user_name)


@bp.route('/seek', methods=['POST', 'GET'])
def search_page():
    search_data = ''
    c = 0
    if request.method == 'POST':
        sousuo = request.form.get('sousuo')
        if sousuo.strip():
            sql = "select A.id,A.title,B.e_name from news_tb A,classes_tb B where A.classes=B.id and A.title like '%{}%'".format(
                sousuo)
            search_data = db.select_data(sql)
            c = len(search_data)
        else:
            return redirect('/')
    grade = session.get('grade')
    user_name = session.get('username')
    return render_template('news_page4.html', data=search_data, c=c, grade=grade, username=user_name)



@bp.route('/<classes>/<int:page>')
def my_column(classes,page):
    sql="select A.title,B.id,A.classes,B.e_name,A.id from news_tb A,classes_tb B where A.classes=B.id and B.e_name='%s'order by create_time desc"%(classes)
    data=db.select_data(sql)
    total=len(data)     #总数据量
    if total%20==0:
        total_page=total/20
    else:
        total_page=total/20+1       #总页码数
    page_data=data[20*(page-1):20*page]     #取出对应页码数据
    data1=page_data[0:10]
    data2=page_data[10:20]
    grade = session.get('grade')
    user_name = session.get('username')
    return render_template('news_page2.html',data1=data1,data2=data2,classes=classes,page=page,total_page=total_page,grade=grade, username=user_name)



@bp.route('/<classes>/page/<int:id>')
def news_page3(classes,id):
    sql = "update news_tb set order_id = order_id+1 where id=%s"
    db.change_data(sql, id)
    sql = "select title,content,img,create_time from news_tb where id=%s"
    res = db.select_data(sql,id)
    content = res[0][1].split('\n')
    img = res[0][2]
    if img:
        img = img.split()
    grade = session.get('grade')
    user_name = session.get('username')
    return render_template('news_page3.html', title=res[0][0], content=content, img=img, date=res[0][3],grade=grade, username=user_name)


@bp.route('/data')
def data_list():
    data = ''
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    sq_t = "(select * from news_tb where create_time like '%s%%')" % date
    sql = "select A.id,A.title,B.e_name from %s A,classes_tb B where A.classes=B.id order by rand() limit 10" % sq_t
    res = db.select_data(sql)
    for i in res:
        data += '<ul><li><a href="/%s/%s" style = "text-decoration:none;">%s</a></li></ul>' % (i[2], i[0], i[1][0:23])
    return data


@bp.route('/test')
def test():
    list1 = [1, 2, 3]
    random_list = random.sample(list1, 1)
    photo_str = '''<br><br><a href="https://www.4008823823.com.cn/kfcios/Html/index.html" target="_blank">
            <img src="/static_folder/image/news_ad_kdj%s.gif" style="height:200px;width:200px"/></a><br><br>
        <img src="/static_folder/image/ad1_page3.png" style="height:200px;width:200px"/>
        ''' % random_list[0]
    return photo_str


@bp.route('/test1')
def test1():
    list2 = [1, 2, 3]
    random_list = random.sample(list2, 2)
    photo_str = '''<br><br><a href="http://lpl.qq.com/es/rr/2018/?ADTAG=media.buy.baidu_shxbrand.fenlei_rukou1" target="_blank">
            <img src="/static_folder/image/news_ad_yxlm%s.gif" style="height:200px;width:200px"/></a><br><br>
        <a href="http://app.tanwan.com/htmlcode/17443.html" target="_blank">
        <img src="/static_folder/image/news_ad_twly%s.gif" style="height:200px;width:200px"/></a>
        ''' % (random_list[0], random_list[1])
    return photo_str


@bp.route('/login', methods=['POST', 'GET'])
def land():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        passwd = request.form.get('password')
        sql = "select username from user_tb where username=%s"
        res = db.select_data(sql, username)
        msg = '用户名不存在'
        if res:
            sql = "select password from user_tb where username=%s and password=%s"
            res = db.select_data(sql, (username, passwd))
            if res:
                sql = "select grade from user_tb where username=%s"
                res = db.select_data(sql, username)
                session['username'] = '%s' % username
                session['grade'] = res[0][0]
                return redirect('/')
            msg = '密码错误'
        return render_template('login.html', errors=msg)


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form.get('username')
        passwd = request.form.get('password')
        passwd1 = request.form.get('password1')
        phonenum = request.form.get('phone')
        sql = "select username from user_tb where username=%s"
        res = db.select_data(sql, username)
        msg = '用户名已存在'
        if not res:
            if passwd == passwd1:
                if len(phonenum) == 11 and (re.findall('1[0-9]{10}', phonenum)) != []:
                    sql = "insert into user_tb(username,password,phone) values(%s,%s,%s)"
                    db.change_data(sql, (username, passwd, phonenum))
                    pops = '注册成功! 用户名:%s，密码:%s，手机号:%s。' % (username, passwd, phonenum)
                    return render_template('login.html', pop=pops)
                msg = '手机号不合法'
            else:
                msg = '两次密码不一致'
        return render_template('register.html', errors=msg)


@bp.route('/revise', methods=['POST', 'GET'])
def revise():
    if request.method == 'GET':
        return render_template('revise.html')
    username = request.form.get('username')
    password = request.form.get('password')
    password1 = request.form.get('password1')
    sql = "select username from user_tb where username=%s"
    res = db.select_data(sql, username)
    msg = '用户名不存在'
    if res:
        sql = "select password from user_tb where username=%s and password=%s"
        res = db.select_data(sql, (username, password))
        if res:
            if password != password1:
                sql = "update user_tb set password=%s where username=%s"
                db.change_data(sql, (password1, username))
                pops = '密码修改成功! 新密码:%s。' % password1
                return render_template('login.html', pop=pops)
            msg = '新密码不能与旧密码相同'
        else:
            msg = '密码错误'
    return render_template('revise.html', errors=msg)


@bp.route('/forget', methods=['POST', 'GET'])
def forget():
    if request.method == 'GET':
        return render_template('forget.html')
    username = request.form.get('username')
    password = request.form.get('password')
    phone = request.form.get('phone')
    sql = "select username from user_tb where username=%s"
    res = db.select_data(sql, username)
    msg = '用户名不存在'
    if res:
        sql = "select phone from user_tb where username=%s and phone=%s"
        res = db.select_data(sql, (username, phone))
        if res:
            sql = "update user_tb set password=%s"
            db.change_data(sql, password)
            pops = '密码重置成功! 新密码为：%s。' % password
            return render_template('login.html', pop=pops)
        msg = '手机号码不匹配'
    return render_template('forget.html', errors=msg)


@bp.route('/recharge', methods=['POST', 'GET'])
def recharge():
    if request.method == 'GET':
        return render_template('recharge.html')
    username = request.form.get('username')
    password = request.form.get('password')
    money = request.form.get('money')
    sql = "select username from user_tb where username=%s"
    res = db.select_data(sql, username)
    msg = '用户名不存在'
    if res:
        sql = "select password from user_tb where username=%s and password=%s"
        res = db.select_data(sql, (username, password))
        if res:
            if int(money) >= 30:
                sql = "update user_tb set grade=%s where username=%s"
                db.change_data(sql, (1, username))
                pops = '充值成功，您已成为尊贵的VIP！'
                return render_template('login.html', pop=pops)  # 有问题，路由没变化
            msg = '每次充值不得少于30元'
        else:
            msg = '密码错误'
    return render_template('recharge.html', errors=msg)

