from typing import List, Optional

from api.core import Manager
from api.models import CourseInfo, TeachTask
from cli.config import GLOBAL_CONFIG
from cli.utils import text_align, info, error, show_help


class Commander(object):
    def __init__(self):
        self._mgr = Manager()
        self._prompt = "> "

    def login(self):
        sid = GLOBAL_CONFIG.get_user_sid()
        token = GLOBAL_CONFIG.get_user_token()
        if not sid or not token:
            sid = input("输入你的 SID: ")
            token = input("输入 Token: ")
        if self._mgr.login(sid, token):
            GLOBAL_CONFIG.set_user_sid(sid)
            GLOBAL_CONFIG.set_user_token(token)
            info("登录成功!")
        else:
            error("登录失败!")

    def logout(self):
        """登出, 清除保存的 Cookie"""
        GLOBAL_CONFIG.set_user_sid("")
        GLOBAL_CONFIG.set_user_token("")
        info("已清除本地 Cookie")

    def run(self):
        """处理一条命令"""
        try:
            inputs = input(self._prompt).split()
            if len(inputs) == 0:
                return None
        except KeyboardInterrupt:
            print("")
            info("退出本程序请输入 bye")
            return None

        cmd, arg = (inputs[0], "") if len(inputs) == 1 else (inputs[0], inputs[1])

        if cmd == "login":
            self.login()
        elif cmd == "logout":
            self.logout()
        elif cmd == "help":
            show_help()
        elif cmd == "me":
            self.print_stu_info()
        elif cmd == "xx":  # 选修
            self.start_select_course(False)
        elif cmd == "bx":  # 必修
            self.start_select_course(True)
        elif cmd == "kb":  # 课表
            self.print_course_table(arg)
        elif cmd == "bye":
            exit()

    def print_course_table(self, uid_str: str):
        """浏览器打开课表"""
        uid = self._mgr.get_stu_info().uid if not uid_str else int(uid_str)
        self._mgr.show_course_table(uid)

    def print_stu_info(self):
        """打印学生信息"""
        stu = self._mgr.get_stu_info()
        print("*" * 70)
        print(f"姓名: {stu.name}\t\t性别: {stu.sex}")
        print(f"学号: {stu.uid}\t学制: {stu.years}")
        print(f"生日: {stu.birthday}\t入学时间: {stu.enroll_time}")
        print(f"学院: {stu.depart_name}")
        print(f"专业: {stu.major_name}")
        print("*" * 70)

    def start_select_course(self, is_must=True):
        """打印课程信息列表"""
        task_list = self._mgr.get_teach_task_list(is_must)
        if not task_list:
            error("获取信息失败, 请重试!")
            return None

        for i, task in enumerate(task_list, 1):
            selected = "[√]" if task.is_selected else "[  ]"
            is_must = "[√]" if task.task_mode == "01" else "[  ]"
            max_stu = task.max_stu if task.max_stu > 0 else "∞"
            print(
                f"[{i}]\t{text_align(task.course_name, 25)}\t学分:{task.credit:<8}{task.cur_stu:>4}/{max_stu:<4}\t必修: {is_must}  已选: {selected}  TID: {task.tid}")

        choose = input("\n[选课按1 | 退课按2]: ") or "1"
        num = int(input("输入课程编号: ") or "0") - 1
        if num < 0 or num >= len(task_list):
            error("编号无效")
            return
        task = task_list[num]
        if choose == "2":
            self.exit_courses(task)
        elif choose == "1":
            courses_list = self.print_course_list(task)
            if not courses_list:
                return
            num = int(input("输入课程编号: ") or "0") - 1
            if num < 0 or num >= len(courses_list):
                error("编号无效")
                return
            course = courses_list[num]
            self.select_course(task, course)
        else:
            error("输入有误!")

    def print_course_list(self, task: TeachTask) -> Optional[List[CourseInfo]]:
        is_must = True if task.task_mode == "01" else False
        course_list = self._mgr.get_course_list(task.tid, is_must)
        if not course_list:
            error("获取课程信息失败")
            return None

        for i, course in enumerate(course_list, 1):
            selected = "[√]" if course.is_selected else "[  ]"
            max_stu = course.max_stu if course.max_stu > 0 else "∞"
            remains = course.max_stu - course.cur_stu
            print(
                f"[{i}]\t{text_align(course.name, 25)}\t{course.teacher:4}\t{course.tech_cls:<4} {course.cur_stu:>4}/{max_stu:<4}\t剩余: {remains:<4} 已选: {selected}  CID: {course.cid}")
        return course_list

    def exit_courses(self, task: TeachTask):
        is_must = True if task.task_mode == "01" else False
        if self._mgr.exit_course(task.tid, is_must):
            info(f"退课成功: {task.course_name}")
        else:
            error(f"退课失败: {task.course_name}")

    def select_course(self, task: TeachTask, course: CourseInfo):
        is_must = True if task.task_mode == "01" else False
        if self._mgr.select_course(task.tid, course.cid, is_must):
            info(f"选课成功: {course.name} {course.teacher}")
        else:
            error(f"选课失败: {course.name} {course.teacher}")
