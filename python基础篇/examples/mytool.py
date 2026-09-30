# -*- coding: utf-8 -*-
"""第 14 章「写自己的模块」的配套模块文件。

这个文件本身就是演示品：它是被 ch14_模块与标准库.py 用 `import mytool` 导入的。
单独运行它也能跑——因为末尾有 `if __name__ == "__main__":` 的保护。

用法（在 examples 目录下）：python mytool.py
"""


def greet(name):
    return "你好，" + name + "！"


# 别人 `import mytool` 时，下面这段【不会】执行；
# 只有直接运行 `python mytool.py` 时才执行。
if __name__ == "__main__":
    print("__name__ =", __name__)
    print(greet("mytool"))
