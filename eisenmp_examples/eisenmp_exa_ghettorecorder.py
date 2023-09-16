"""GhettoRecorder command line app instances are distributed
over two processes. See the documentation images.

| The parent process is controlling the instances via a child process thread manager.
| Three queues are assigned to each child process. In, out, audio Queue.

A Watchdog Thread is included, it shows the pid of its proc.
"""
import os
import threading
import time
import eisenmp
import eisenmp.utils.eisenmp_utils as e_utils

dir_name = os.path.dirname(__file__)


class ModuleConfiguration:  # name your own class and feed eisenmp with the dict
    """More advanced template. Multiprocess 'spawn' in 'ProcEnv' to work with all OS.
    - toolbox.kwargs shows all avail. vars and dead references of dicts, lists, instances, read only
    """
    template_module = {
        'WORKER_PATH': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_ghettorecorder.py'),
        'WORKER_REF': 'worker_entrance',
    }
    watchdog_module = {
        'WORKER_PATH': os.path.join(os.path.dirname(dir_name), 'worker', 'eisenmp_exa_wrk_watchdog.py'),
        'WORKER_REF': 'mp_start_show_threads',
    }

    def __init__(self, proc_max=3):

        self.worker_modules = [  # in-bld-res
            self.template_module,  # other modules must start threaded, else we hang
            self.watchdog_module  # second; thread function call mandatory, last module loaded first
        ]
        self.PROCS_MAX: int = proc_max  # I know it is int. process count, default is None: one proc per CPU core
        self.sleep_time = 20  # watchdog


modConf = ModuleConfiguration()  # Accessible in the module.


def manager_entry():
    """
    | Must take category for qs. queue_cust_dict_category_create.
    | Access in worker toolbox.ghetto_qs['com_in_1']
    | Note: Can not access in worker toolbox['com_in_1'], only toolbox.com_in_1
    | Run Test on Manager:
    | create_radio = ('create', 'nachtflug', 'http://85.195.88.149:11810', 'home/osboxes/abracadabra')
    | emp.queue_cust_dict_cat['child_qs']['com_in_1'].put(create_radio)
    """
    # list of q_category, q_name, q_maxsize tuples
    q_name_maxsize_lst = []
    for num in range(modConf.PROCS_MAX):
        q_name_maxsize_lst.append(('child_qs', 'com_in_' + str(num), 1))
        q_name_maxsize_lst.append(('child_qs', 'com_out_' + str(num), 5))
        q_name_maxsize_lst.append(('child_qs', 'audio_out_' + str(num), 1))

    emp = eisenmp.Mp()
    # create custom queues without category, stored in a dictionary for the worker processes
    emp.queue_cust_dict_category_create(*q_name_maxsize_lst)

    emp.start(**modConf.__dict__)  # create processes, load worker mods
    pass
    while 1:
        time.sleep(3)
        create_radio = ('create', 'nachtflug', 'http://85.195.88.149:11810', 'home/osboxes/abracadabra')
        emp.queue_cust_dict_cat['child_qs']['com_in_1'].put(create_radio)
        return emp


def main():
    """
    """
    start = time.perf_counter()

    emp_ret = manager_entry()
    while 1:
        # running threads, wait
        if emp_ret.begin_proc_shutdown:
            break
        time.sleep(1)

    msg_time = 'GhettoRecorder instances, Time in sec: ', round((time.perf_counter() - start))
    print(msg_time)
    msg_result = e_utils.Result.result_dict

    names_list = [thread.name for thread in threading.enumerate()]
    print(names_list)
    return msg_result


if __name__ == '__main__':
    main()
