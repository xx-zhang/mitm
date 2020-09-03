import os

LINUX_LOG_DIR = "/opt/log/"
PRO_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
WIN_LOG_DIR = os.path.join(PRO_DIR, 'logs')

if not os.path.exists(LINUX_LOG_DIR):
    os.makedirs(LINUX_LOG_DIR)

if not os.path.exists(WIN_LOG_DIR):
    os.makedirs(WIN_LOG_DIR)

