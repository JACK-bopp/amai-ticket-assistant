#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大麦抢票助手 - Android版
主入口文件
"""

import os
import sys

# 确保当前目录在系统路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入应用
from damai_ticket.app import DamaiTicketApp

if __name__ == '__main__':
    app = DamaiTicketApp()
    app.run()