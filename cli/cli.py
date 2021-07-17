from time import sleep
from typing import List, Optional, TypeVar

from api.core import Manager
from api.models import Course, TeachTask
from cli.config import GLOBAL_CONFIG
from cli.utils import text_align, info, error, show_help, color_print


class Commander:
    def __init__(self):
        self._stu_info = None
        self._mgr = Manager()
        self._prompt = "> "

    def login_required(func):
        def inner(self, *args, **kwargs):
            if not self._stu_info:
                error("请先登录!")
                return
            return func(self, *args, **kwargs)

        return inner

    def login(self):
        """登录"""
        sid = GLOBAL_CONFIG.get_user_sid()
        token = GLOBAL_CONFIG.get_user_token()
        # 尝试使用 cookies 登录
        if sid and token and self._mgr.login_by_cookie(sid, token):
            GLOBAL_CONFIG.set_user_sid(sid)
            GLOBAL_CONFIG.set_user_token(token)
            info("使用 Cookie 登录成功!")
            self._stu_info = self._mgr.get_stu_info()
            return

        # cookies 无效, 用户名密码登录
        username = input("输入学号: ")
        password = input("输入密码: ")
        if username and password and self._mgr.login(username, password):
            cookies = self._mgr.get_cookies()
            GLOBAL_CONFIG.set_user_sid(cookies.get("sid"))
            GLOBAL_CONFIG.set_user_token(cookies.get("token"))
            info("登录成功, Cookie 已保存!")
            self._stu_info = self._mgr.get_stu_info()
            return

        error("登录失败!")

    def logout(self):
        """登出, 清除保存的 Cookie"""
        GLOBAL_CONFIG.set_user_sid("")
        GLOBAL_CONFIG.set_user_token("")
        self._stu_info = None
        self._mgr.logout()
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
            self.select_task(False)
        elif cmd == "bx":  # 必修
            self.select_task(True)
        elif cmd == "tk":  # 退课
            self.exit_courses()
        elif cmd == "kb":  # 课表
            self.print_course_table()
        elif cmd == "bye":
            exit()
        else:
            print("输入 help 查看命令帮助")

    def print_course_table(self):
        """浏览器打开课表"""
        student_id = input("输入学号(默认当前登录用户): ") or self._stu_info.student_id
        term_id = input("输入学期号(如 202101/02 表示 2021 年上/下学期): ") or ""
        if not student_id or not term_id.isdigit():
            print(f"输入有误!")
            return
        self._mgr.show_course_table(student_id, int(term_id))

    @login_required
    def print_stu_info(self):
        """打印学生信息"""
        stu_info = self._stu_info
        print("*" * 70)
        print(f"姓名: {stu_info.name}\t\t\t性别: {stu_info.sex}")
        print(f"学号: {stu_info.student_id}\t\t学制: {stu_info.years}")
        print(f"生日: {stu_info.birthday}\t\t入学时间: {stu_info.enroll_time}")
        print(f"学院: {stu_info.depart_name}")
        print(f"专业: {stu_info.major_name}")
        print("*" * 70)

    T = TypeVar("T")

    @staticmethod
    def _ask_for_choice(lst: List[T]) -> Optional[T]:
        try:
            choose = input("\n选择序号: ")
        except KeyboardInterrupt:
            return
        if not choose or not choose.isdigit():
            error("序号有误")
            return
        choose = int(choose) - 1
        if choose < 0 or choose >= len(lst):
            error("序号有误")
            return
        return lst[choose]

    @login_required
    def select_task(self, is_must):
        """打印课程信息列表"""
        tasks = self._mgr.get_teach_tasks(is_must)
        if not tasks:
            error("获取信息失败, 请检查网络连接并重试!")
            return

        for i, task in enumerate(tasks, 1):
            selected = "[√]" if task.is_selected else "[  ]"
            max_stu = task.max_stu_num if task.max_stu_num > 0 else "∞"
            text = f"[{i}]\t{text_align(task.course_name, 28)}\t学分: {task.credit:<8}{task.cur_stu_num:>4}/{max_stu:<4} {task.task_type_value}  {task.choose_status_value}  已选: {selected}"
            if task.is_selected:
                color_print(text, "green")
            else:
                print(text)

        task = self._ask_for_choice(tasks)
        if not task:
            return
        courses_list = self.print_task_courses(task)
        if not courses_list:
            return

        task_nums = input("\n选择课程编号(多个编号用空格分开): ") or ""
        if not task_nums:
            info("放弃选课")
            return
        task_nums = [int(n) - 1 for n in task_nums.split()]
        for n in task_nums:
            if n < 0 or n >= len(courses_list):
                error("包含无效课程编号, 请检查")
                return
        courses = [courses_list[n] for n in task_nums]
        if self._mgr.select_courses(courses):
            info("选课成功!")
            return

        error("选课失败!")
        choose = input("是否需要挂机抢课(y/n): ") or "n"
        if choose.lower() == "y":
            interval = float(input("挂机抢课时间间隔(秒): ") or "3")
            self.auto_select_course(courses, interval)

    def print_task_courses(self, task: TeachTask) -> Optional[List[Course]]:
        course_list = self._mgr.get_task_courses(task)
        if not course_list:
            error("获取课程信息失败")
            return None

        for i, course in enumerate(course_list, 1):
            selected = "[√]" if course.is_selected else "[  ]"
            max_stu = course.max_stu_num if course.max_stu_num > 0 else "∞"
            remains = course.max_stu_num - course.cur_stu_num
            text = f"[{i}] {course.course_type_value}\t{course.tech_class:<4} {course.cur_stu_num:>4}/{max_stu:<4}\t剩余: {remains:>4}\t已选: {selected}\t{course.teachers}\t备注: {course.brief}"
            if course.is_selected:
                color_print(text, "green")
            else:
                print(text)
        return course_list

    @login_required
    def exit_courses(self):
        """
        退课操作
        """
        selected_tasks = self._mgr.get_selected_task()
        for i, task in enumerate(selected_tasks, 1):
            text = f"[{i}] {text_align(task.course_name, 28)}\t{task.task_type_value}\t学分: {task.credit:<3}\t{task.choose_status_value}\t{task.status_value}"
            color_print(text, "green")
            print(f"\t{task.t_class_info} \t {task.s_class_info}\n")

        task = self._ask_for_choice(selected_tasks)
        if not task:
            return
        if self._mgr.exit_course(task):
            info(f"{task.course_name}: 退课成功!")
        else:
            error(f"{task.course_name}: 退课失败，该课程选课已关闭或已结束")

    def auto_select_course(self, courses: List[Course], interval: float):
        """一直选课, 直到成功"""
        if interval < 1:
            info("太快了, 慢点啊兄弟! 时间间隔不能小于 1s")
        count = 1
        try:
            while True:
                if self._mgr.select_courses(courses):
                    info("选课成功!")
                    break
                error(f"{count} 选课失败, {interval}s 后重试...")
                count += 1
                sleep(interval)
        except KeyboardInterrupt:
            pass
