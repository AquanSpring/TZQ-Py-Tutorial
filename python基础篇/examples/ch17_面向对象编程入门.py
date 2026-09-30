# -*- coding: utf-8 -*-
"""第 17 章 面向对象编程入门 —— 章节示例（不含「本章挑战作业」的答案）

把本章正文里出现过的代码按顺序整理在一起，可以直接运行对照。
用法：python ch17_面向对象编程入门.py
"""

# ---------------------------------------------------------------
# 定义一个类
# ---------------------------------------------------------------

class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        print(self.name + "：汪汪！")

my_dog = Dog("旺财", 3)      # 按图纸造一只狗
print(my_dog.name)           # 旺财
my_dog.bark()                # 旺财：汪汪！


# ---------------------------------------------------------------
# 为什么要这么麻烦
# ---------------------------------------------------------------

dogs = [Dog("旺财", 3), Dog("小黑", 2), Dog("豆豆", 5)]

for dog in dogs:
    dog.bark()


# ---------------------------------------------------------------
# 继承：站在类的肩膀上
# ---------------------------------------------------------------

class Puppy(Dog):          # 幼犬“是一种”狗 —— 继承 Dog
    def roll(self):
        print(self.name + " 打了个滚")

p = Puppy("团子", 1)
p.bark()        # 团子：汪汪！ —— 从 Dog 继承来的
p.roll()        # 团子 打了个滚 —— 自己新增的


# ---------------------------------------------------------------
# 动手：写一个 Student 类
# ---------------------------------------------------------------

class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def introduce(self):
        print(f"我叫 {self.name}，考了 {self.score} 分")

    def is_passed(self):
        return self.score >= 60

stu = Student("小明", 85)
stu.introduce()               # 我叫 小明，考了 85 分
print(stu.is_passed())        # True
