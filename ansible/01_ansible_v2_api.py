#!/usr/bin/env python  
# -*- coding: UTF-8 -*-


import json
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import ansible.constants as C

class ResultCallback(CallbackBase):
 
    def v2_runner_on_ok(self, result, **kwargs):
 
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

# 初始化需要的对象
Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])
options = Options(connection='smart', module_path=['/data/py3/lib/python3.7/site-packages/ansible/modules'], forks=10, become=None, become_method='sudo', become_user='root', check=False, diff=False)

# initialize needed objects
loader = DataLoader()
# passwords = dict(vault_pass='abcd-1234')
passwords = {}

# 实例化ResultCallback
results_callback = ResultCallback()

# 创建inventory并传递给var_manager
inventory = InventoryManager(loader=loader, sources='/data/devops/ansible/nginx_hosts')
variable_manager = VariableManager(loader=loader, inventory=inventory)

# create datastructure that represents our play, including tasks, this is basically what our YAML loader does internally.
play_source =  dict(
        name = "Ansible Play",
        hosts = 'nginx-uat',
        gather_facts = 'no',
        tasks = [
            #dict(action=dict(module='shell', args='/bin/sh /usr/local/nginx/conf/script/get_servername.sh'), register='shell_out'),
            dict(action=dict(module='shell', args='ls /data/'), register='shell_out'),
            #dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
         ]
    )

# 
play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

# 
tqm = None
try:
    tqm = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
              #stdout_callback=results_callback,  # 回调函数
              stdout_callback='default',
          )
    result = tqm.run(play) # 执行
finally:
    # 清理子进程
    if tqm is not None:
        tqm.cleanup()

    # Remove ansible tmpdir
    shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

