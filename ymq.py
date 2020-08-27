""""
一个简单的例子, 如果羽毛球有剩余就退掉已经选择的课改选羽毛球
"""

import time
from random import randrange

from api.core import Manager

mgr = Manager()
mgr.login("xxx", "xxx")
tid = 123345  # 体育课
cid_wq = 182035  # 网球
cid_ymq = 182121  # 羽毛球

while True:
    c_list = mgr.get_course_list(tid, True)
    course_ymq = [c for c in c_list if c.cid == cid_ymq][0]
    remains = course_ymq.max_stu - course_ymq.cur_stu
    if remains > 0:
        print("有机可乘!")
        mgr.exit_course(tid, is_must=True)  # 退体育课
        mgr.select_course(tid, cid_ymq, is_must=True)  # 选羽毛球
    print("正在蹲羽毛球...")

    t = time.strptime("2020-08-27 05:00:00", "%Y-%m-%d %H:%M:%S")
    now = time.struct_time(time.localtime())
    if t > now:  # 没到早上
        time.sleep(60 * 10)  # 10 分钟看一下
    else:
        time.sleep(randrange(5, 10))  # 5-10秒看一下
