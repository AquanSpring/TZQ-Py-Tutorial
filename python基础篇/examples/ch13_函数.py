# -*- coding: utf-8 -*-
"""第 13 章 函数 —— 章节示例（不含「本章挑战作业」的答案）

把本章正文里出现过的代码按顺序整理在一起，可以直接运行对照。
用法：python ch13_函数.py

说明：正文里故意写错的那行（函数外访问局部变量）用 try/except 接住，
      让你看到真实的 NameError。
"""

# ---------------------------------------------------------------
# 定义与调用
# ---------------------------------------------------------------

def greet():
    print("你好！")
    print("欢迎学习 Python")

greet()     # 调用一次，执行一次
greet()

# pass 什么都不做，专门用来撑住还没写的语法结构
def todo():
    pass          # 还没想好怎么写，先占个位，保证代码能运行


# ---------------------------------------------------------------
# 文档字符串（docstring）
# ---------------------------------------------------------------

def add(a, b):
    """把两个数相加并返回结果。"""
    return a + b

print(add.__doc__)     # 把两个数相加并返回结果。


# ---------------------------------------------------------------
# 参数：给函数传数据
# ---------------------------------------------------------------

def greet(name):
    print("你好，" + name + "！")

greet("小明")     # 你好，小明！
greet("小红")     # 你好，小红！

# 带默认值的参数：不传就用默认，传了就覆盖
def greet(name, greeting="你好"):
    print(greeting + "，" + name + "！")

greet("小明")               # 你好，小明！
greet("小明", "早上好")      # 早上好，小明！

# 关键字参数：指名道姓地传，顺序随意
greet(greeting="早上好", name="小明")    # 早上好，小明！


# ---------------------------------------------------------------
# 一个必须提前知道的坑：默认值别用可变对象
# ---------------------------------------------------------------

# 默认值只在“定义函数时”算一次，之后每次调用共用同一个列表
def add_item(item, box=[]):
    box.append(item)
    return box

print(add_item("a"))    # ['a']
print(add_item("b"))    # ['a', 'b'] —— 上一次的结果还在！

# 正确写法：默认设成 None，进了函数再建
# （正文里这两段是各自独立的代码块、都叫 add_item；放进同一个文件后
#   后一个改名 add_item_ok，免得覆盖前面的定义）
def add_item_ok(item, box=None):
    if box is None:
        box = []
    box.append(item)
    return box

print(add_item_ok("a"))    # ['a']
print(add_item_ok("b"))    # ['b'] —— 互不影响


# ---------------------------------------------------------------
# 选学：接收任意多个参数（*args 和 **kwargs）
# ---------------------------------------------------------------

def total(*nums):
    print(nums)              # (1, 2, 3) —— 收到的是一个元组
    return sum(nums)

print(total(1, 2, 3))        # 6
print(total())               # 0 —— 一个都不传也行

def show(**info):
    print(info)              # {'name': '小明', 'age': 18}
    for key, value in info.items():
        print(key, "=", value)

show(name="小明", age=18)

# 反过来也能用：调用时把列表 / 字典“拆开”当参数传进去
nums = [1, 2, 3]
print(total(*nums))          # 6 —— 等价于 total(1, 2, 3)

info = {"name": "小明", "age": 18}
show(**info)                 # 等价于 show(name="小明", age=18)


# ---------------------------------------------------------------
# 返回值：把结果交回去
# ---------------------------------------------------------------

def add(a, b):
    return a + b

result = add(3, 5)     # 函数算出 8，“交回”给调用处，存进 result
print(result)          # 8

# return 和 print 是两回事 —— 新手最容易混淆的地方
def bad_add(a, b):
    print(a + b)        # 只打印，没有返回

x = bad_add(3, 5)       # 屏幕上显示 8，但 x 是 None！
print(x)                # None

# return 可以一次返回多个值（其实是打包成元组），配合解包接收
def min_max(nums):
    return min(nums), max(nums)

low, high = min_max([3, 1, 4, 1, 5])
print(low, high)        # 1 5


# ---------------------------------------------------------------
# 变量的作用范围
# ---------------------------------------------------------------

def test():
    inner = 42

test()

# ❌ 正文里的反面例子：函数内部定义的变量，外面看不到。
#    用 try/except 接住它，让你看到真实的 NameError：
try:
    print(inner)
except NameError as e:
    print("NameError:", e)


# ---------------------------------------------------------------
# 那想在函数里改外面的变量呢？（global）
# ---------------------------------------------------------------

# 正文这三段也都叫 add_one（各自独立的代码块）；同一个文件里要并存，
# 后两个分别改名 add_one_ok 和 plus_one，其余与正文完全一致。
# ❌ 函数里给外面的变量赋值，Python 会认为你在建一个新的局部变量
count = 0

def add_one():
    count = count + 1      # ❌ UnboundLocalError

try:
    add_one()
except UnboundLocalError as e:
    print("UnboundLocalError:", e)

# 真要改外面那个，得用 global 明确声明
count = 0

def add_one_ok():
    global count           # 声明：我要改的是外面那个 count
    count = count + 1

add_one_ok()
add_one_ok()
print(count)               # 2

# 但更好的做法是让函数把结果返回出来，由调用方决定怎么用
def plus_one(n):
    return n + 1

count = 0
count = plus_one(count)
count = plus_one(count)
print(count)               # 2


# ---------------------------------------------------------------
# 动手：写一个判断偶数的函数
# ---------------------------------------------------------------

def is_even(n):
    return n % 2 == 0

print(is_even(4))     # True
print(is_even(7))     # False

# 返回布尔值的函数常用 is_ 前缀命名，读起来像一句话：“4 是偶数吗？”


# ---------------------------------------------------------------
# 选学：函数调用自己（递归）
# ---------------------------------------------------------------

def factorial(n):
    if n <= 1:                    # 1. 什么时候停（必须有！）
        return 1
    return n * factorial(n - 1)   # 2. 把问题缩小一点，再交给自己

print(factorial(5))     # 120
