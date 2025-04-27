#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大麦抢票助手 - Android版
主入口文件
"""

from damai_ticket.app import DamaiTicketApp

if __name__ == '__main__':
    app = DamaiTicketApp()
    app.run()