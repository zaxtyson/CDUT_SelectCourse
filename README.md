# CDUT 教务处选课

选没到羽毛球, 太伤心了, 于是连夜加急写了这个玩意, 主要是选体育课用

貌似教务处有 BUG, 可以无视选课人数上限 100% 选中(震惊滑稽.jpg)  


## CLI

![](https://s1.ax1x.com/2020/08/28/do1moF.png)

## 食用方法

- 请安装 Python3

- 安装依赖
 ```python
pip install requests lxml
 ```

- 运行
```python
python3 main.py
```


## 命令帮助

```bash
help          显示本信息
login         使用 Cookie 登录教务处
logout        清除本地 Cookie
bye           退出本程序
me            显示你的个人信息
bx            查看必修课
xx            查看选修课
kb            查看课表
kb 学号       查看别人的课表 :)
```

## 声明

本项目仅供学习交流使用, 由此导致的一切问题由用户自行承担

## 更新

### 2020/12/31  

- 改用用户名+密码方式登录, 登录成功自动保存 Cookie 
- 命令行加了点颜色, 排版稍微好看点了
