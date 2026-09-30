# -*- coding: utf-8 -*-
"""第 15 章 异常处理 —— 章节示例（不含「本章挑战作业」的答案）

把本章正文里出现过的代码按顺序整理在一起，可以直接运行对照。
用法：python ch15_异常处理.py

说明：正文的这些例子都靠 input() 手动输入来制造错误。这里把输入换成
      了几组固定值，把“成功 / 失败”两条路各走一遍给你看，
      这样文件能自己跑完，不用你盯着屏幕敲。
"""

# ---------------------------------------------------------------
# try / except：尝试与兜底
# ---------------------------------------------------------------

# 正文的交互版是：age = int(input("请输入年龄："))
for raw in ["18", "abc"]:
    try:
        age = int(raw)                       # 这行可能报错
        print(f"输入 {raw} → 明年你就 {age + 1} 岁")
    except ValueError:
        print(f"输入 {raw} → 输入的不是数字，请重试！")

print("程序继续运行")                         # 两种情况都会走到这里


# ---------------------------------------------------------------
# 一个 try 可以接多种异常
# ---------------------------------------------------------------

for a_raw, b_raw in [("10", "2"), ("10", "0"), ("abc", "2")]:
    try:
        a = int(a_raw)
        b = int(b_raw)
        print(f"{a_raw} ÷ {b_raw} = {a / b}")
    except ValueError:
        print(f"{a_raw} ÷ {b_raw} → 请输入数字")
    except ZeroDivisionError:
        print(f"{a_raw} ÷ {b_raw} → 除数不能为 0")


# ---------------------------------------------------------------
# 动手：给 BMI 计算器加保护
# ---------------------------------------------------------------

for height_raw, weight_raw in [("1.75", "65"), ("abc", "65"), ("0", "65")]:
    try:
        height = float(height_raw)
        weight = float(weight_raw)
        bmi = weight / height ** 2
        print(f"身高 {height_raw}、体重 {weight_raw} → BMI {bmi:.2f}")
    except ValueError:
        print(f"身高 {height_raw}、体重 {weight_raw} → 请输入合法的数字！")
    except ZeroDivisionError:
        print(f"身高 {height_raw}、体重 {weight_raw} → 身高不能为 0！")


# ---------------------------------------------------------------
# 选学：从“读报错”到“调试”
# ---------------------------------------------------------------

# 正文这段例子用到了 scores，这里把它的定义补上
scores = [90, 85, 77, 100, 66]

total = 0
for s in scores:
    total += s
    print(f"加上 {s} 后，total = {total}")     # 每一步都摊开看


# ---------------------------------------------------------------
# 附：正文「常见异常速查表」里的异常，各演示一次
# ---------------------------------------------------------------

print("--- 常见异常演示 ---")

try:
    print(undefined_name)                # NameError：使用了未定义的变量
except NameError as e:
    print("NameError:", e)

try:
    print("5" + 5)                       # TypeError：类型不匹配
except TypeError as e:
    print("TypeError:", e)

try:
    print(int("abc"))                    # ValueError：类型对但值不合适
except ValueError as e:
    print("ValueError:", e)

try:
    print([1, 2, 3][10])                 # IndexError：列表索引越界
except IndexError as e:
    print("IndexError:", e)

try:
    print({"a": 1}["b"])                 # KeyError：字典键不存在
except KeyError as e:
    print("KeyError:", e)

try:
    print(1 / 0)                         # ZeroDivisionError：除数为 0
except ZeroDivisionError as e:
    print("ZeroDivisionError:", e)

try:
    open("不存在的文件.txt", "r", encoding="utf-8")    # FileNotFoundError
except FileNotFoundError as e:
    print("FileNotFoundError:", e)


# ---------------------------------------------------------------
# 还有 finally 和 assert
# ---------------------------------------------------------------

# finally：无论成功还是失败都会执行的收尾代码
try:
    f = open("不存在的文件.txt", "r", encoding="utf-8")   # 这里一定失败
    print(f.read())
except FileNotFoundError:
    print("文件不存在")
finally:
    print("无论成功还是失败，这句都会执行")

# assert：给“我认为这里一定是这样”加一道自动检查（适合调试和自测，不适合挡用户输入）
age = 18
assert age >= 18, "年龄必须满 18"    # 不成立就报错，并带上这句说明
print("断言通过")
