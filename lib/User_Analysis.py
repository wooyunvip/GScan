# coding:utf-8
import os, optparse, time, sys
from common import *


# 账户类安全排查
# 1、查看root权限账户，排除root本身
# 2、查看系统中是否存在空口令账户
# 3、查看sudoers文件权限，是否存在可直接sudo获取root的账户
# 4、查看各账户下登录公钥

class User_Analysis:
    def __init__(self):
        self.user_malware = []

    # 检测root权限用户
    def check_user(self):
        suspicious, malice = False, False
        shell_process = os.popen("awk -F: '$3==0 {print $1}' /etc/passwd").readlines()
        for user in shell_process:
            if user.replace("\n", "") != 'root':
                self.user_malware.append(
                    {'user': user.replace("\n", ""), 'description': 'root power', 'authorized_keys_user': ''})
                suspicious = False
        return suspicious, malice

    # 检测空口令账户
    def check_empty(self):
        suspicious, malice = False, False
        shell_process2 = os.popen("awk -F: 'length($2)==0 {print $1}' /etc/shadow").readlines()
        for user in shell_process2:
            self.user_malware.append(
                {'user': user.replace("\n", ""), 'description': 'user empty password', 'authorized_keys': ''})
            malice = True
        return suspicious, malice

    # 检测sudo权限异常账户
    def check_sudo(self):
        suspicious, malice = False, False
        shell_process3 = os.popen("cat /etc/sudoers|grep -v '#'|grep 'ALL=(ALL)'|awk '{print $1}'").readlines()
        for user in shell_process3:
            if user.replace("\n", "") != 'root':
                self.user_malware.append(
                    {'user': user.replace("\n", ""), 'description': 'sudo get root power', 'authorized_keys_user': ''})
                suspicious = True
        return suspicious, malice

    # 获取用户免密登录的公钥
    def check_authorized_keys(self):
        suspicious, malice = False, False
        for dir in os.listdir('/home/'):
            suspicious2, malice2 = self.file_analysis(os.path.join('%s%s%s' % ('/home/', dir, '/.ssh/authorized_keys')),
                                                      dir)
            if suspicious2: suspicious = True
            if malice2: malice = True
        suspicious2, malice2 = self.file_analysis('/root/.ssh/authorized_keys', 'root')
        if suspicious2: suspicious = True
        if malice2: malice = True
        return suspicious, malice

    # 分析authorized_keys文件
    def file_analysis(self, file, user):
        suspicious, malice = False, False
        if os.path.exists(file):
            shell_process = os.popen("cat " + file + "|awk '{print $3}'").readlines()
            authorized_key = ' & '.join(shell_process).replace("\n", "")
            self.user_malware.append({'user': user.replace("\n", ""), 'description': 'login certificate settings',
                                      'authorized_keys_user': authorized_key})
            suspicious = True
        return suspicious, malice

    def run(self):
        print(u'\n开始账户类安全扫描')
        print align(u' [1]root权限账户安全扫描', 30) + u'[ ',
        file_write(u'\n开始账户类安全扫描')
        file_write(align(u' [1]root权限账户安全扫描', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_user()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print align(u' [2]空口令账户安全扫描', 30) + u'[ ',
        file_write(align(u' [2]空口令账户安全扫描', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_empty()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print align(u' [3]sudoers文件权限账户安全扫描', 30) + u'[ ',
        file_write(align(u' [3]sudoers文件权限账户安全扫描', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_sudo()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print align(u' [4]账户免密码证书安全扫描', 30) + u'[ ',
        file_write(align(u' [4]账户免密码证书安全扫描', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_authorized_keys()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        if len(self.user_malware) > 0:
            file_write(u'可疑账户如下：\n')
            for info in self.user_malware:
                file_write(str(info) + '\n')

if __name__ == '__main__':
    infos = User_Analysis()
    infos.run()
    print u"可疑账户如下："
    for info in infos.user_malware:
        print info