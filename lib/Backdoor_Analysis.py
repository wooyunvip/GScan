# coding:utf-8
from __future__ import print_function
import os, time, sys, json, re
from lib.common import *
from lib.ip.ip import *


# 作者：咚咚呛
# 常规类后门检测
# 1、LD_PRELOAD后门检测
# 2、LD_AOUT_PRELOAD后门检测
# 3、LD_ELF_PRELOAD后门检测
# 4、LD_LIBRARY_PATH后门检测
# 5、ld.so.preload后门检测
# 6、PROMPT_COMMAND后门检测
# 7、crontab后门检测
# 8、alias后门
# 9、ssh后门 ln -sf /usr/sbin/sshd /tmp/su; /tmp/su -oPort=5555;
# 10、SSH Server wrapper 后门，替换/user/sbin/sshd 为脚本文件
# 11、/etc/inetd.conf 后门
# 12、/etc/xinetd.conf/后门
# 13、系统启动项后门检测


class Backdoor_Analysis:
    def __init__(self):
        # 异常后门列表
        self.backdoor = []
        # 恶意特征列表
        self.malware_infos = []
        # 获取恶意特征信息
        self.get_malware_info()

        self.ip_http = r'(htt|ft)p(|s)://(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
        self.ip_re = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
        self.lan_ip = r'(127\.0\.0\.1)|(localhost)|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(172\.((1[6-9])|(2\d)|(3[01]))\.\d{1,3}\.\d{1,3})|(192\.168\.\d{1,3}\.\d{1,3})'

    # LD_PRELOAD后门检测
    def check_LD_PRELOAD(self):
        suspicious, malice = False, False
        try:
            infos = os.popen("echo $LD_PRELOAD").read().splitlines()
            for info in infos:
                if not len(info) > 3: continue
                self.backdoor.append(
                    {u'异常类型': u'LD_PRELOAD 后门', u'异常信息': info, u'手工确认': u'[1]echo $LD_PRELOAD [2]unset LD_PRELOAD'})
                malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # LD_AOUT_PRELOAD后门检测
    def check_LD_AOUT_PRELOAD(self):
        suspicious, malice = False, False
        try:
            infos = os.popen("echo $LD_AOUT_PRELOAD").read().splitlines()
            for info in infos:
                if not len(info) > 3: continue
                self.backdoor.append(
                    {u'异常类型': u'LD_AOUT_PRELOAD 后门', u'异常信息': info,
                     u'手工确认': u'[1]echo $LD_AOUT_PRELOAD [2]unset LD_AOUT_PRELOAD'})
                malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # LD_ELF_PRELOAD后门检测
    def check_LD_ELF_PRELOAD(self):
        suspicious, malice = False, False
        try:
            infos = os.popen("echo $LD_ELF_PRELOAD").read().splitlines()
            for info in infos:
                if not len(info) > 3: continue
                self.backdoor.append(
                    {u'异常类型': u'LD_ELF_PRELOAD 后门', u'异常信息': info,
                     u'手工确认': u'[1]echo $LD_ELF_PRELOAD [2]unset LD_ELF_PRELOAD'})
                malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # LD_LIBRARY_PATH后门检测
    def check_LD_LIBRARY_PATH(self):
        suspicious, malice = False, False
        try:
            infos = os.popen("echo $LD_LIBRARY_PATH").read().splitlines()
            for info in infos:
                if not len(info) > 3: continue
                self.backdoor.append(
                    {u'异常类型': u'LD_LIBRARY_PATH 后门', u'异常信息': info,
                     u'手工确认': u'[1]echo $LD_LIBRARY_PATH [2]unset LD_LIBRARY_PATH'})
                malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # ld.so.preload后门检测
    def check_ld_so_preload(self):
        suspicious, malice = False, False
        try:
            if not os.path.exists('/etc/ld.so.preload'): return suspicious, malice
            with open('/etc/ld.so.preload') as f:
                for line in f:
                    if not len(line) > 3: continue
                    if line[0] != '#':
                        self.backdoor.append({u'异常类型': u'ld.so.preload 后门', u'异常信息': line.replace("\n", ""),
                                              u'文件': u'/etc/ld.so.preload', u'手工确认': u'[1]cat /etc/ld.so.preload'})
                        malice = True
                        break
            return suspicious, malice
        except:
            return suspicious, malice

    # PROMPT_COMMAND后门检测
    def check_PROMPT_COMMAND(self):
        suspicious, malice = False, False
        try:
            infos = os.popen("echo $PROMPT_COMMAND").read().splitlines()
            for info in infos:
                suspicious2, malice2 = self.analysis_strings('PROMPT_COMMAND backdoor', 'ROMPT_COMMAND', info,
                                                             '[1]echo $PROMPT_COMMAND')
                if suspicious2: suspicious = True
                if malice2: malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 分析cron定时任务后门
    def check_cron(self):
        suspicious, malice = False, False
        try:
            cron_dir_list = ['/var/spool/cron/', '/etc/cron.d/', '/etc/cron.daily/', '/etc/cron.weekly/',
                             '/etc/cron.hourly/', '/etc/cron.monthly/']
            for cron in cron_dir_list:
                files = [os.path.join(cron, i) for i in os.listdir(cron) if (not os.path.isdir(os.path.join(cron, i)))]
                for file in files:
                    for i in open(file, 'r'):
                        suspicious2, malice2 = self.analysis_strings('crontab backdoor', file, i, '[1]cat %s' % file)
                        if suspicious2: suspicious = True
                        if malice2: malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 分析alias后门
    def check_alias(self):
        suspicious, malice = False, False
        try:
            infos = os.popen("alias").read().splitlines()
            for info in infos:
                suspicious2, malice2 = self.analysis_strings('alias backdoor', "", info, '[1]alias')
                if suspicious2: suspicious = True
                if malice2: malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 分析SSH后门
    def check_SSH(self):
        suspicious, malice = False, False
        try:
            infos = os.popen("netstat -ntpl |grep -v ':22 '| awk '{if (NR>2){print $7}}'").read().splitlines()
            for info in infos:
                pid = info.split("/")[0]
                if os.path.exists('/proc/%s/exe' % pid):
                    if 'sshd' in os.readlink('/proc/%s/exe' % pid):
                        self.backdoor.append(
                            {u'异常类型': u'SSH 后门', u'异常信息': u'/porc/%s/exe' % pid, u'异常文件': u'/proc/%s/exe' % pid,
                             u'手工确认': u'[1]ls -l /porc/%s [2]ps -ef|grep %s|grep -v grep' % (pid, pid)})
                        malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 分析SSH Server wrapper 后门
    def check_SSHwrapper(self):
        suspicious, malice = False, False
        try:
            infos = os.popen("file /usr/sbin/sshd").read().splitlines()
            if 'ELF' not in infos[0]:
                self.backdoor.append(
                    {u'异常类型': u'SSHwrapper 后门', u'异常信息': infos[0], u'文件': u'/usr/sbin/sshd',
                     u'手工确认': u'[1]file /usr/sbin/sshd [2]cat /usr/sbin/sshd'})
                malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 分析inetd后门
    def check_inetd(self):
        suspicious, malice = False, False
        try:
            if not os.path.exists('/etc/inetd.conf'): return suspicious, malice
            with open('/etc/inetd.conf') as f:
                for line in f:
                    if '/bin/bash' in line:
                        self.backdoor.append(
                            {u'异常类型': u'inetd.conf 后门', u'异常信息': line, u'文件': u'/etc/inetd.conf',
                             u'手工确认': u'[1]cat /etc/inetd.conf'})
                        malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 分析xinetd后门
    def check_xinetd(self):
        suspicious, malice = False, False
        try:
            if not os.path.exists('/etc/xinetd.conf/'): return suspicious, malice
            for file in os.listdir('/etc/xinetd.conf/'):
                with open(os.path.join('%s%s' % ('/etc/xinetd.conf/', file))) as f:
                    for line in f:
                        if '/bin/bash' in line:
                            fpath = os.path.join('%s%s' % ('/etc/xinetd.conf/', file))
                            self.backdoor.append(
                                {u'异常类型': u'xinetd.conf 后门', u'异常信息': line, u'文件': u'/etc/xinetd.conf/%s' % file,
                                 u'手工确认': u'[1]cat /etc/xinetd.conf/%s' % file})
                            malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 系统启动项检测
    def check_startup(self):
        suspicious, malice = False, False
        try:
            init_path = ['/etc/init.d/', '/etc/rc.d/', '/etc/rc.local', '/usr/local/etc/rc.d',
                         '/usr/local/etc/rc.local', '/etc/conf.d/local.start', '/etc/inittab', '/etc/systemd/system']
            for path in init_path:
                if not os.path.exists(path): continue
                if os.path.isfile(path):
                    malware = self.analysis_file(path)
                    if malware:
                        self.backdoor.append(
                            {u'异常类型': u'系统启动项后门', u'文件': path, u'异常信息': malware,
                             u'手工确认': u'[1]cat %s' % path})
                        malice = True
                    continue
                for file in gci(path):
                    malware = self.analysis_file(file)
                    if malware:
                        self.backdoor.append(
                            {u'异常类型': u'系统启动项后门', u'文件': path, u'异常信息': malware,
                             u'手工确认': u'[1]cat %s' % file})
                        malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 获取配置文件的恶意域名等信息
    def get_malware_info(self):
        try:
            malware_path = sys.path[0] + '/lib/malware/'
            if not os.path.exists(malware_path): return
            for file in os.listdir(malware_path):
                time.sleep(0.001)  # 防止cpu占用过大
                with open(malware_path + file) as f:
                    for line in f:
                        if len(line) > 3:
                            if line[0] != '#': self.malware_infos.append(line.strip().replace("\n", ""))
        except:
            return

    # 分析文件是否包含恶意特征或者反弹shell问题
    def analysis_file(self, file):
        try:
            if not os.path.exists(file): return ""
            if os.path.isdir(file): return ""
            if os.path.islink(file): return ""
            if " " in file: return ""
            if 'GScan' in file: return ""
            if (os.path.getsize(file) == 0) or (round(os.path.getsize(file) / float(1024 * 1024)) > 10): return ""
            strings = os.popen("strings %s" % file).readlines()
            for str in strings:
                mal = check_shell(str)
                if mal: return mal
                for malware in self.malware_infos:
                    if malware in str: return malware
                if self.check_contents_ip(str): return str

            return ""
        except:
            return ""

    # 分析字符串是否包含境外IP
    def check_contents_ip(self, contents):
        try:
            if not re.search(self.ip_http, contents): return False
            if re.search(self.lan_ip, contents): return False
            for ip in re.findall(self.ip_re, contents):
                if (find(ip)[0:2] != u'中国') and (find(ip)[0:3] != u'局域网') and (find(ip)[0:4] != u'共享地址'):
                    return True
            return False
        except:
            return False

    # 分析一串字符串是否包含反弹shell或者存在的文件路径
    def analysis_strings(self, name, file, contents, solve):
        suspicious, malice = False, False
        try:
            content = contents.replace('\n', '')
            if check_shell(content):
                self.backdoor.append(
                    {u'异常类型': name, u'文件': file, u'异常信息': content, u'类型特征': u'反弹shell类', u'手工确认': solve})
                malice = True
            elif self.check_contents_ip(content):
                self.backdoor.append(
                    {u'异常类型': name, u'文件': file, u'异常信息': content, u'类型特征': u'境外IP信息', u'手工确认': solve})
                malice = True
            else:
                for file in content.split(' '):
                    if not os.path.exists(file): continue
                    malware = self.analysis_file(file)
                    if malware:
                        self.backdoor.append(
                            {u'异常类型': name, u'文件': file, u'异常信息': content, u'类型特征': malware, u'手工确认': solve})
                        malice = True
            return suspicious, malice
        except:
            return suspicious, malice

    def run(self):
        print(u'\n开始恶意后门类安全扫描')
        print(align(u' [1]LD_PRELOAD 后门检测', 30) + u'[ ', end='')
        file_write(u'\n开始后门类安全扫描\n')
        file_write(align(u' [1]LD_PRELOAD 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_LD_PRELOAD()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [2]LD_AOUT_PRELOAD 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [2]LD_AOUT_PRELOAD 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_LD_AOUT_PRELOAD()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [3]LD_ELF_PRELOAD 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [3]LD_ELF_PRELOAD 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_LD_ELF_PRELOAD()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [4]LD_LIBRARY_PATH 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [4]LD_LIBRARY_PATH 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_LD_LIBRARY_PATH()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [5]ld.so.preload 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [5]ld.so.preload 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_ld_so_preload()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [6]PROMPT_COMMAND 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [6]PROMPT_COMMAND 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_PROMPT_COMMAND()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [7]crontab 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [7]crontab 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_cron()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [8]alias 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [8]alias 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_SSH()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [9]ssh 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [9]ssh 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_SSH()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [10]SSH wrapper 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [10]SSH wrapper 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_SSHwrapper()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [11]inetd.conf 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [11]inetd.conf 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_inetd()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [12]xinetd.conf 后门检测', 30) + u'[ ', end='')
        file_write(align(u' [12]xinetd.conf 后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_xinetd()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        print(align(u' [13]系统启动项后门检测', 30) + u'[ ', end='')
        file_write(align(u' [13]系统启动项后门检测', 30) + u'[ ')
        sys.stdout.flush()
        suspicious, malice = self.check_startup()
        if malice:
            pringf(u'存在风险', malice=True)
        elif suspicious and (not malice):
            pringf(u'警告', suspicious=True)
        else:
            pringf(u'OK', security=True)

        if len(self.backdoor) > 0:
            file_write('-' * 30 + '\n')
            file_write(u'后门检查异常如下：\n')
            for info in self.backdoor:
                file_write(json.dumps(info, ensure_ascii=False) + '\n')
            file_write('-' * 30 + '\n')


if __name__ == '__main__':
    infos = Backdoor_Analysis()
    infos.run()
    print(u"后门检查异常如下：")
    for info in infos.backdoor:
        print(info)
