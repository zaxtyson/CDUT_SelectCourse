from random import random
from typing import List, Optional
from webbrowser import open_new

import requests
from lxml import etree

from api.models import CourseInfo, TeachTask, StudentInfo


class Manager(object):
    """课程捡漏"""

    def __init__(self):
        self._host = "http://202.115.133.173:805"
        self._stu_info_api = self._host + "/StudentInfo/StudentsManagement/IdentityCard.aspx"
        self._course_api = self._host + "/SelectCourse/SelectHandler.ashx"
        self._course_table_api = self._host + "/Classroom/ProductionSchedule/StuProductionSchedule.aspx"
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

    def login(self, sid: str, token: str) -> bool:
        """使用 Cookie 登录教务处
        @sid ASP.NET_SessionId 的值
        @token UserTokeID 的值
        """
        user_data = {"ASP.NET_SessionId": sid, "UserTokeID": token}
        self._session.cookies.update(user_data)
        if self.get_stu_info().uid:
            return True
        return False

    def show_course_table(self, uid: int):
        """浏览器打开课表
        @uid 学号
        """
        url = self._course_table_api + f"?termid=202001&stuID={uid}"
        open_new(url)

    def get_stu_info(self) -> Optional[StudentInfo]:
        """获取学生信息"""
        resp = self._session.get(self._stu_info_api)
        if resp.status_code != 200:
            print(f"Error, status code: {resp.status_code}")
            return None

        stu = StudentInfo()
        table = self._xpath(resp.text, '//table[@class="mb_table01"]')[0]
        stu.name = table.xpath('.//span[@id="Content_uName"]/text()')[0]
        stu.sex = table.xpath('.//span[@id="Content_Sex"]/text()')[0]
        stu.folk_name = table.xpath('.//span[@id="Content_StuFolkName"]/text()')
        stu.folk_name = stu.folk_name[0] if stu.folk_name else ""
        stu.address = table.xpath('.//span[@id="Content_Addr"]/text()')
        stu.address = stu.address[0] if stu.address else ""
        stu.birthday = table.xpath('.//span[@id="Content_Birthday"]/text()')[0]
        stu.uid = table.xpath('.//span[@id="Content_StuCode"]/text()')[0]
        stu.depart_name = table.xpath('.//span[@id="Content_school"]/text()')[0]
        stu.major_name = table.xpath('.//span[@id="Content_major"]/text()')[0]
        stu.years = table.xpath('.//span[@id="Content_years"]/text()')[0]
        stu.enroll_time = table.xpath('.//span[@id="Content_ENROLLMENTDATE"]/text()')[0]
        return stu

    def get_teach_task_list(self, is_must=True) -> List[TeachTask]:
        """获取本学期教学任务
        @is_must 是必修课吗
        """
        task_type = "01" if is_must else "02"
        params = {"Action": "GetTeachTask", "TaskType": task_type, "PageIndex": 0, "PageSize": 300, "rnd": random()}
        resp = self._session.post(self._course_api, data=params)
        if resp.status_code != 200:
            print(f"{resp.status_code}, Failed to get teach tasks")
            return []
        data = resp.json()
        ret = []
        for task in data["TeachTaskEntities"]:
            t = TeachTask()
            t.class_name = task["ClassNames"]
            t.course_name = task["CourseName"]
            t.course_show_name = task["CourseShowName"]
            t.credit = float(task["Credit"])
            t.depart_name = task["DepartName"]
            t.tid = int(task["Id"])
            t.is_selected = task["IsSelectCourse"]
            t.major_name = task["MajorName"]
            t.status = task["Status"]
            t.task_mode = task["TaskMode"]
            t.teachers = task["TeacherName"]
            t.cur_stu = int(task["StuNum"])
            t.max_stu = int(task["MaxStuNum"])
            ret.append(t)
        return ret

    def get_course_list(self, tid: int, is_must: bool) -> List[CourseInfo]:
        """获取某个课程的选课信息
        @tid 教学任务id
        @is_must 是必修课吗
        """
        task_type = "01" if is_must else "02"
        params = {"Action": "GetTeachTaskClass", "TaskId": tid, "taskType": task_type}
        resp = self._get(self._course_api, params=params)
        if resp.status_code != 200:
            print(f"Error, status {resp.status_code}")
            return []

        ret = []
        course_info = resp.json().get('data')
        if not course_info:
            print(f"Error, no course information")
            return ret

        course_info = course_info.get('02') or course_info.get('01') or course_info.get('03')
        for course in course_info:
            c = CourseInfo()
            c.name = course["Brief"]
            c.teacher = course["TeachNames"]
            c.cid = course["Id"]
            c.cur_stu = course["CurStuNum"]
            c.max_stu = course["MaxStuNum"]
            c.tech_cls = course["TeachClass"]
            c.is_selected = course["IsSelected"]
            ret.append(c)
        return ret

    def select_course(self, tid: int, cid: int, is_must: bool):
        """选课操作
        @tid 教学任务id
        @cid 具体的课程id
        @is_must 是必修课吗
        """
        if is_must:  # 必修课
            task_type = "01"
            class_id = cid
            s_class_id = 0
        else:  # 选修有第123志愿
            task_type = "02"
            class_id = 0
            s_class_id = cid
        params = {"Action": "SelectCourse"}
        payload = {"TaskId": tid, "TaskType": task_type,
                   "ClassId": class_id, "ClassId2": 0, "ClassId3": 0,
                   "SclassId": s_class_id, "SclassId2": s_class_id, "SclassId3": s_class_id,
                   "oclassId": 0, "oclassId2": 0, "oclassId3": 0,
                   "jclassId": 0, "jclassId2": 0, "jclassId3": 0,
                   "oType": "04"}

        resp = self._session.post(self._course_api, params=params, data=payload)
        if resp.status_code != 200:
            print(f"Error, status: {resp.status_code}")
            return False

        return resp.json().get('result')

    def exit_course(self, tid: int, is_must: bool) -> bool:
        """退课操作
        @tid 教学任务id
        @is_must 是必修课吗
        """
        task_type = "01" if is_must else "02"
        params = {"Action": "ExitSelectCourse", "TaskType": task_type}
        payload = {"TaskId": tid}
        resp = self._session.post(self._course_api, params=params, data=payload)
        if resp.status_code != 200:
            print(f"Error, status: {resp.status_code}")
            return False

        return resp.json().get('result')
