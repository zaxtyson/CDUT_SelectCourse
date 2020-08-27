import os


def error(msg):
    # print(f"\033[1;31mError : {msg}\033[0m")
    print(f"Error : {msg}")


def info(msg):
    # print(f"\033[1;34mInfo : {msg}\033[0m")
    print(f"Info : {msg}")


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


def text_align(text, length) -> str:
    """中英混合字符串对齐"""
    text_len = len(text)
    for char in text:
        if u'\u4e00' <= char <= u'\u9fff':
            text_len += 1
    space = length - text_len
    return text + ' ' * space
