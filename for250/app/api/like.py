#coding:utf-8
from . import api
from app import db
from flask import request,jsonify,Response
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User

import pickle
import json
import redis

#注意docker-compose 中redis不能持久化

@api.route('/like/', methods = ['POST'])
def like():
    if request.method == 'POST':
        myid = request.get_json().get('myid')
        otherid = request.get_json().get('otherid')
        
        #conn1 is for who like who 
        conn1 = redis.StrictRedis(host='redis', port=6380, db=9)
        mylikes = pickle.loads(conn1.get(myid))
        if otherid not in mylikes:
            mylikes.append(otherid)
            #更新mylikes
            conn1.set(myid, pickle.dumps(mylikes))

        otherlikes = pickle.loads(conn1.get(otherid))
        if myid in otherlikes:
            other = User.query.filter_by(id = otherid).first()
            #conn2 is for message 
            conn2 = redis.StrictRedis(host='redis', port=6380, db=10)
            #获取对方消息列表
            messagelist = pickle.loads(conn2.get(otherid))
            flag = 0
            for m in messagelist:
                if m['uid'] == myid:
                    flag = 1
            
            if flag == 0:
                me = User.query.filter_by(id = myid).first()
                dic = {}
                dic['uid'] = me.id
                dic['username'] = me.username
                dic['specialty'] = me.specialty
                dic['qq'] = me.qq
                messagelist.append(dic)
                conn2.set(otherid, pickle.dumps(messagelist))

            return jsonify({
                "message":"ok",
                "qq":other.qq
            }),200

        else:
            return jsonify({
                "message":"fail"
            }),200
