import json
import re
from hashlib import md5
from random import random
from time import time
from typing import List, Optional, Union
from webbrowser import open_new

import requests
from lxml import etree
from requests.cookies import CookieConflictError

from api.models import Course, TeachTask, StudentInfo, SelectedTask


class Manager(object):

    def __init__(self):
        self._host = "http://202.115.133.173:805"
        self._login_api = self._host + "/Common/Handler/UserLogin.ashx"
        self._stu_info_api = self._host + "/StudentInfo/StudentsManagement/IdentityCard.aspx"
        self._course_api = self._host + "/SelectCourse/SelectHandler.ashx"
        self._course_table_api = self._host + "/Classroom/ProductionSchedule/StuProductionSchedule.aspx"
        self._selected_task_api = self._host + "/SelectCourse/selectcourse.aspx"
        self._session = requests.Session()
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4223.0 Safari/537.36 Edg/86.0.608.2",
            "Referer": "http://202.115.133.173:805/SelectCourse/Default.aspx"
        }

    def _get(self, url: str, params=None, **kwargs) -> requests.Response:
        try:
            kwargs.setdefault("timeout", 10)
            kwargs.setdefault("headers", self._headers)
            ret = self._session.get(url, params=params, verify=False, **kwargs)
            return ret
        except requests.RequestException:
            return requests.Response()

    def _post(self, url: str, data=None, **kwargs) -> requests.Response:
        try:
            kwargs.setdefault("timeout", 10)
            kwargs.setdefault("headers", self._headers)
            ret = self._session.post(url, data, verify=False, **kwargs)
            return ret
        except requests.RequestException:
            return requests.Response()

    def _xpath(self, html: str, xpath: str) -> Optional[etree.Element]:
        """支持 xpath 方便处理网页"""
        if not html:
            return None
        try:
            return etree.HTML(html).xpath(xpath)
        except etree.XPathError:
            return None

    def login(self, username: str, password: str) -> bool:
        """使用用户名和密码登录"""
        username = username.strip()
        password = password.strip()
        sign = str(int(time() * 1000))
        pass_md5 = md5(password.encode("utf-8")).hexdigest()
        password = md5((username + sign + pass_md5).encode("utf-8")).hexdigest()
        payload = {"Action": "Login", "userName": username, "pwd": password, "sign": sign}
        resp = self._session.post(self._login_api, data=payload)
        if resp.status_code != 200 or resp.text != "0":
            return False
        return True

    def get_cookies(self) -> dict:
        """
        获取用户 cookie
        {"sid": sid, "token": token}
        """
        sid = self._session.cookies.get("ASP.NET_SessionId")
        try:
            token = self._session.cookies.get("UserTokeID")  # token 可能出现多个
        except CookieConflictError:
            token = self._session.cookies.get("UserTokeID", domain="202.115.133.173")
        ret = {"sid": sid, "token": token}
        return ret

    def login_by_cookie(self, sid: str, token: str) -> bool:
        """
        使用 Cookie 登录教务处
        @sid ASP.NET_SessionId 的值
        @token UserTokeID 的值
        """
        user_data = {"ASP.NET_SessionId": sid, "UserTokeID": token}
        self._session.cookies.update(user_data)
        if not self.get_stu_info():
            return False
        return True

    def logout(self):
        """
        登出
        """
        self._session.cookies.clear()

    def show_course_table(self, student_id: str, term_id: int):
        """
        浏览器打开课表
        @student_id 学号
        @term_id 学期号, 如 202101, 202102 表示 2021 年上学期, 下学期
        """
        url = self._course_table_api + f"?termid={term_id}&stuID={student_id}"
        open_new(url)

    def get_stu_info(self) -> StudentInfo:
        """获取学生信息"""
        stu = StudentInfo()
        resp = self._session.get(self._stu_info_api)
        if resp.status_code != 200:
            return stu

        resp.encoding = "utf-8"
        if "重复提交" in resp.text:
            return stu

        table = self._xpath(resp.text, '//table[@class="mb_table01"]')[0]
        stu.name = table.xpath('//span[@id="Content_uName"]/text()')[0]
        stu.sex = table.xpath('//span[@id="Content_Sex"]/text()')[0]
        folk_name = table.xpath('//span[@id="Content_StuFolkName"]/text()')
        stu.folk_name = folk_name[0] if folk_name else "未知"
        address = table.xpath('//span[@id="Content_Addr"]/text()')
        stu.address = address[0] if address else "未知"
        stu.birthday = table.xpath('//span[@id="Content_Birthday"]/text()')[0]
        stu.student_id = table.xpath('//span[@id="Content_StuCode"]/text()')[0]
        stu.depart_name = table.xpath('//span[@id="Content_school"]/text()')[0]
        stu.major_name = table.xpath('//span[@id="Content_major"]/text()')[0]
        years = table.xpath('//span[@id="Content_years"]/text()')
        stu.years = years[0] if years else 0
        stu.enroll_time = table.xpath('//span[@id="Content_ENROLLMENTDATE"]/text()')[0]
        return stu

    def get_teach_tasks(self, is_must=True) -> List[TeachTask]:
        """
        获取本学期教学任务列表

        @is_must 是必修课吗
        """
        task_type = "01" if is_must else "02"
        params = {"Action": "GetTeachTask", "TaskType": task_type, "PageIndex": 0, "PageSize": 300, "rnd": random()}
        resp = self._session.post(self._course_api, data=params)
        if resp.status_code != 200:
            return []

        data = resp.json()
        ret = []
        for task in data["TeachTaskEntities"]:
            t = TeachTask()
            t.choose_flag = task["ChooseFlg"]
            t.choose_status = task["ChooseStatus"]
            t.class_datetime = task["ClassDateTime"]
            t.class_address = task["ClassDress"]
            t.class_names = task["ClassNames"]
            t.course_name = task["CourseName"]
            t.course_show_name = task["CourseShowName"]
            t.credit = float(task["Credit"])
            t.depart_name = task["DepartName"]
            t.task_id = int(task["Id"])
            t.is_must = task["IsMust"]
            t.is_selected = task["IsSelectCourse"]
            t.major_name = task["MajorName"]
            t.max_stu_num = int(task["MaxStuNum"])
            t.cur_stu_num = int(task["StuNum"])
            t.status = task["Status"]
            t.student_grade = task["StuGrade"]
            t.task_type = task["TaskMode"]  # 为了和请求参数一致, 改成 task_type
            t.teachers = task["TeacherName"]
            ret.append(t)
        return ret

    def get_task_courses(self, task: TeachTask) -> List[Course]:
        """
        获取某个教学任务的课程信息(包括理论课/实验课/实训课)
        """
        params = {"Action": "GetTeachTaskClass", "TaskId": task.task_id, "taskType": task.task_type}
        resp = self._get(self._course_api, params=params)
        if resp.status_code != 200:
            return []

        ret = []
        course_info = resp.json().get('data')
        if not course_info:
            return ret

        courses = [
            *course_info.get("01", []),  # 实验课
            *course_info.get("02", []),  # 理论课
            *course_info.get("03", [])  # 实训课
        ]

        for course in courses:
            c = Course()
            c.brief = course["Brief"]
            c.class_datetime = course["ClassDateTime"]
            c.class_address = course["ClassDress"]
            c.course_type = course["ClassMode"]  # 这两个命名很混淆, 改一下
            c.task_type = course["CourseMode"]
            c.hours_total = int(course["HoursTotle"])
            c.task_id = int(course["TaskId"])
            c.course_id = int(course["Id"])
            c.teachers = course["TeachNames"]
            c.term_id = int(course["TermId"])
            c.cur_stu_num = course["CurStuNum"]
            c.max_stu_num = course["MaxStuNum"]
            c.tech_class = course["TeachClass"]
            c.is_selected = course["IsSelected"]
            ret.append(c)
        return ret

    def select_courses(self, courses: List[Course]) -> bool:
        """
        选课操作, 一个 TeachTask 下面可能有多个 Course, 如教学课/实验课/实训课
        通常是单个选项, 只有单独的理论课程
        如果配有实验课, 就需要选择理论课 + 一个实验课(实验课可能分班级上)
        大三的实训课程是多个选项选一个
        """
        c1 = [c.course_id for c in courses if c.course_type == "01"]
        c2 = [c.course_id for c in courses if c.course_type == "02"]
        c3 = [c.course_id for c in courses if c.course_type == "03"]

        for x in (c1, c2, c3):
            if len(x) < 3:
                for _ in range(3 - len(x)):
                    x.append(0)

        params = {"Action": "SelectCourse"}
        payload = {
            "TaskId": courses[0].task_id,
            "TaskType": courses[0].task_type,
            "ClassId": c1[0],  # "01" 实验课 id
            "ClassId2": c1[1],
            "ClassId3": c1[2],
            "SclassId": c2[0],  # "02" 教学课 id
            "SclassId2": c2[1],
            "SclassId3": c2[2],
            "oclassId": 0,  # 不知道是干嘛的
            "oclassId2": 0,
            "oclassId3": 0,
            "jclassId": c3[0],  # "03" 实训课 id
            "jclassId2": c3[1],
            "jclassId3": c3[2],
            "oType": "04"
        }

        resp = self._session.post(self._course_api, params=params, data=payload)
        if resp.status_code != 200:
            return False

        return resp.json().get('result')

    def exit_course(self, course: Union[TeachTask, Course, SelectedTask]) -> bool:
        """
        退课操作
        @course 教学任务或者其中某一个课程
        """
        params = {"Action": "ExitSelectCourse", "TaskType": course.task_type}
        payload = {"TaskId": course.task_id}
        resp = self._session.post(self._course_api, params=params, data=payload)
        if resp.status_code != 200:
            return False

        return resp.json().get('result')

    def get_selected_task(self) -> List[SelectedTask]:
        """
        获取已经选择的教学任务列表
        """
        ret = []
        resp = self._session.get(self._selected_task_api)
        if resp.status_code != 200:
            return ret
        data = re.search(r"selectCourse=(.*?);", resp.text)
        if not data:
            return ret
        data = data.group(1).replace('StuCourse', '"StuCourse"').replace('StuCtCourse', '"StuCtCourse"')
        data = json.loads(data)
        for task in (*data["StuCourse"], *data["StuCtCourse"]):
            t = SelectedTask()
            t.choose_flag = task["ChooseFlg"]
            t.choose_status = task["ChooseStatus"]
            t.course_name = task["CourseName"]
            t.credit = task["Credit"]
            t.task_id = task["TaskId"]
            t.is_must = task["IsMust"]  # 服务器返回点都是 false
            t.is_selected = True  # 不知道为啥服务器返回的是 false
            t.status = task["Status"]
            t.teachers = task["TCalssTeacherName"]
            t.task_type = task["ComeFrom"]
            t.s_class_id = task["SClassId"]
            t.s_class_name = task["SClassName"]
            t.s_class_teachers = task["SClassTeacherName"]
            t.t_class_id = task["TcalssId"]
            t.t_class_name = task["TCalssName"]
            t.t_class_teachers = task["TCalssTeacherName"]
            t.j_class_id = task["JClassId"]
            t.o_class_id = task["OthClassId"]
            # 其它 null 值信息忽略
            ret.append(t)
        return ret
