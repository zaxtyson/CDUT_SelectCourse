class StudentInfo:

    def __init__(self):
        self.name = ""  # 姓名
        self.sex = ""  # 性别
        self.folk_name = ""  # 民族
        self.address = ""  # 籍贯
        self.birthday = ""  # 生日
        self.student_id = ""  # 学号
        self.depart_name = ""  # 院系
        self.major_name = ""  # 专业名
        self.years = ""  # 学制 x 年
        self.enroll_time = ""  # 入学时间

    def __str__(self) -> str:
        return str(self.__dict__)


class TeachTask:

    def __init__(self):
        self.choose_flag = False  # 是否有选课志愿
        self.choose_status = ""  # "01" 正在选课, "02" 选课关闭
        self.class_datetime = ""  # 上课时间
        self.class_address = ""  # 上课地点
        self.class_names = ""  # 开课班号(可能有多个) "2018031001-2 ,2018031005, ..."
        self.course_name = ""  # 课程名
        self.course_show_name = ""  # 教务处网站显示的详细课程名, "L7089-形势与政策（7）-.25-8-8-0-0周"
        self.credit = 0  # 学分
        self.depart_name = ""  # 院系名
        self.task_id = 0  # 教学任务 id
        self.is_must = False  # 是必修课吗
        self.is_selected = ""  # 我选了吗
        self.major_name = ""  # 对这些专业开放选课, "0106测绘工程,0111地理信息科学, ..."
        self.max_stu_num = 0  # 可选学生数量
        self.student_grade = ""  # 学生的年级, "2018,2019,2020"
        self.teachers = ""  # 教课的老师们
        self.task_type = ""  # "01" 计划课, "02" 选修课, "03" 补课, "04/05/06" 跨专业选课, "11" 重修, "12" 刷分
        self.cur_stu_num = 0  # 已选本课的学生人数
        self.status = ""  # "a0" 缴费确认, "a1" 欠费, "n1" 待老师确认, "n2" 缴费确认

    @property
    def choose_status_value(self):
        if self.choose_status == "01":
            return "正在选课"
        if self.choose_status == "02":
            return "选课关闭"
        return "未知状态"

    @property
    def task_type_value(self):
        if self.task_type == "01":
            return "计划课"
        if self.task_type == "02":
            return "选修课"
        if self.task_type == "03":
            return "补课"
        if self.task_type in ["04", "05", "06"]:
            return "跨专业选课"
        if self.task_type == "11":
            return "重修"
        if self.task_type == "12":
            return "刷分"
        return "未知类型"

    @property
    def status_value(self):
        if self.status in ["a0", "n2"]:
            return "缴费确认"
        if self.status == "a1":
            return "欠费"
        if self.status == "n1":
            return "待确认"
        return "正常"

    def __str__(self) -> str:
        return str(self.__dict__)


class SelectedTask(TeachTask):

    def __init__(self):
        super().__init__()

        self.s_class_id = 0  # 实验课 id
        self.s_class_name = ""  # 实验课班号 "R01"
        self.s_class_teachers = ""  # 实验课老师
        self.t_class_id = 0  # 教学课 id
        self.t_class_name = ""  # 教学课班号 "L01"
        self.t_class_teachers = ""  # 实验课老师
        self.j_class_id = 0  # 实训课 id
        self.o_class_id = 0  # 其它课 id

    @property
    def s_class_info(self):
        if self.s_class_id == 0:
            return ""
        return f"实验课程: {self.s_class_name} {self.s_class_teachers}"

    @property
    def t_class_info(self):
        if self.t_class_id == 0:
            return ""
        return f"理论课程: {self.t_class_name} {self.t_class_teachers}"


class Course:

    def __init__(self):
        self.brief = ""  # 备注信息(上课时间/地点/QQ群号一般在这)
        self.class_datetime = ""  # 上课时间
        self.class_address = ""  # 上课地点
        self.course_type = ""  # "01" 表示实验课, "02" 表示教学课, "03" 表示实训课
        self.task_type = ""  # "01" 表示必修课, "02" 表示选修课
        self.cur_stu_num = 0  # 已选本课的学生数
        self.hours_total = 0  # 课时
        self.course_id = 0  # 课程 id
        self.task_id = 0  # 课程所属的教学任务 id
        # self.task_code = 0  # 和 task_id 一样
        self.is_selected = False  # 我选了它吗
        self.max_stu_num = 0  # 最多学生数
        self.teach_emp_id = 0
        self.term_id = 0  # 学期号 202101
        self.teachers = ""  # 老师们的名字
        self.tech_class = ""  # 教学班 "L01"

    @property
    def course_type_value(self):
        if self.course_type == "01":
            return "实验教学"
        if self.course_type == "02":
            return "课堂教学"
        if self.course_type == "03":
            return "实践教学"
        return "其它教学"

    def __str__(self) -> str:
        return str(self.__dict__)


class GpaInfo:

    def __init__(self):
        self.course_num = 0  # 课程数
        self.avg_score = 0  # 平均成绩
        self.total_credit = 0  # 已修学分
        self.gpa = 0  # 平均学分绩点

    def __str__(self) -> str:
        return str(self.__dict__)
