import os


def color_print(text: str, color: str):
    color_value = 37  # 白色
    if color == "red":
        color_value = 31
    elif color == "green":
        color_value = 32
    elif color == "blue":
        color_value = 34
    print(f"\033[1;{color_value}m{text}\033[0m")


def error(msg):
    color_print("Error : " + msg, "red")


def info(msg):
    color_print("Info : " + msg, "blue")


def set_console_style():
    """设置命令行窗口样式"""
    if os.name != 'nt':
        return None
    os.system(f'title CDUT-选课工具')


def show_welcome():
    text = """
      ___                         ___                 
     /\__\         _____         /\  \                
    /:/  /        /::\  \        \:\  \         ___   
   /:/  /        /:/\:\  \        \:\  \       /\__\  
  /:/  /  ___   /:/  \:\__\   ___  \:\  \     /:/  /  
 /:/__/  /\__\ /:/__/ \:|__| /\  \  \:\__\   /:/__/   
 \:\  \ /:/  / \:\  \ /:/  / \:\  \ /:/  /  /::\  \   
  \:\  /:/  /   \:\  /:/  /   \:\  /:/  /  /:/\:\  \  
   \:\/:/  /     \:\/:/  /     \:\/:/  /   \/__\:\  \ 
    \::/  /       \::/  /       \::/  /         \:\__\ 
     \/__/         \/__/         \/__/           \/__/
  
  GitHub: https://github.com/zaxtyson/CDUT_SelectCourse
    """
    print(text)


def show_help():
    help_text = """
    help          显示本信息
    login         使用 Cookie 登录教务处
    logout        清除本地 Cookie
    bye           退出本程序
    me            显示你的个人信息
    bx            查看必修课
    xx            查看选修课
    kb            查看课表
    kb 学号       查看别人的课表 :)
    """
    print(help_text)


def clear_screen():
    """清屏"""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def text_align(text: str, length: int) -> str:
    """中英混合字符串对齐"""
    text_len = len(text)
    for char in text:
        if u'\u4e00' <= char <= u'\u9fff':
            text_len += 1  # 中文字符宽度算 2

    if text_len <= length:
        space = length - text_len
        text = text + ' ' * space
    else:
        text += '\n' + ' ' * length + '\t'
    return text
