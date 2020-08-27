class StudentInfo(object):
    def __init__(self):
        self.name = ""  # 姓名
        self.sex = ""  # 性别
        self.folk_name = ""  # 民族
        self.address = ""  # 籍贯
        self.birthday = ""  # 生日
        self.uid = ""  # 学号
        self.depart_name = ""  # 院系
        self.major_name = ""  # 专业名
        self.years = ""  # 学制 x 年
        self.enroll_time = ""  # 入学时间


class TeachTask(object):
    def __init__(self):
        self.class_name = ""  # 数字编号
        self.course_name = ""  # 课程名
        self.course_show_name = ""  # 详细课程名
        self.depart_name = ""  # 院系名
        self.tid = 0  # 教学任务id
        self.major_name = ""  # 计算机类
        self.is_selected = ""  # 我选了吗
        self.credit = 0  # 学分
        self.teachers = ""  # 教课的老师们
        self.task_mode = ""  # "01" 必修  "02" 选修
        self.cur_stu = 0  # 已选学生人数
        self.max_stu = 0  # 可选学生数量
        self.status = ""


class CourseInfo(object):
    def __init__(self):
        self.name = ""  # 课程名
        self.cid = ""  # 课程 id
        self.teacher = ""  # 老师名
        self.cur_stu = 0  # 当前以选本课的学生数
        self.max_stu = 0  # 最多学生数
        self.tech_cls = ""  # 教学班
        self.is_selected = False  # 我选了它吗
