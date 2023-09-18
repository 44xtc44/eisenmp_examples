"""GhettoRecorder command line app instances are distributed
over two processes. See the documentation images.

| The parent process is controlling the instances via a child process thread manager.
| Three queues are assigned to each child process. In, out, audio Queue.

A Watchdog Thread is included, it shows the pid of its proc.
"""
import os
import time
import threading
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

    def __init__(self, proc_max=3, app_max=3, proc_balance=True):
        self.worker_modules = [  # in-bld-res
            self.template_module,  # other modules must start threaded, else we hang
            self.watchdog_module  # second; thread function call mandatory, last module loaded first
        ]
        self.PROCS_MAX: int = proc_max  # I know it is int. process count, default is None: one proc per CPU core
        self.sleep_time = 20  # watchdog
        self.thread_lst = []
        self.user_dict = {'input_q': None,  # eisenmp input_q for external command input to make exex tuples
                          'audio_q': None,  # eisenmp output_q to bring audio to extern (audio endpoint)
                          'radios': {},  # dump attributes for JS ajax
                          'radio_proc_num': {},  # radio process num {'hm', 3}
                          'radio_player': '',  # name of current radio feeds audio_out
                          'num_proc': self.PROCS_MAX,  # to load balance procs or next proc if crowded
                          'proc_balance': proc_balance,
                          'last_proc': self.PROCS_MAX,  # balancer or crowded knows next proc start_sequence_num
                          'app_max': app_max,
                          'com_in_qs': {},
                          'com_out_qs': {},
                          'audio_out_qs': {}}


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
    emp = eisenmp.Mp()
    create_parent_qs(emp)
    create_threads(emp)
    emp.start(**modConf.__dict__)  # create processes, load worker mods

    time.sleep(3)
    emp.mp_input_q.put(('create', 'nachtflug', 'http://85.195.88.149:11810', 'home/osboxes/abracadabra', True))
    emp.mp_input_q.put(('create', 'hirschmilch', 'https://hirschmilch.de:7001/prog-house.mp3',
                        'home/osboxes/abracadabra'))

    'classic_ro = http://37.251.146.169:8000/streamHD'
    time.sleep(6)
    emp.mp_input_q.put(('nachtflug','exec', 'setattr(self,"runs_listen",True)'))

    return emp


def create_parent_qs(emp):
    """"""
    # list of q_category, q_name, q_maxsize tuples
    q_name_maxsize_lst = []
    for num in range(modConf.PROCS_MAX):
        q_name_maxsize_lst.append(('child_qs', 'com_in_' + str(num), 1))
    q_name_maxsize_lst.append(('child_qs', 'com_out', 500))
    q_name_maxsize_lst.append(('child_qs', 'audio_out', 1))

    # create custom queues without category, stored in a dictionary for the worker processes
    emp.queue_cust_dict_category_create(*q_name_maxsize_lst)

    child_qs = emp.queue_cust_dict_cat['child_qs']
    for q in child_qs.keys():
        if q.startswith('com_in'):
            modConf.user_dict['com_in_qs'][q] = child_qs[q]
        if q.startswith('com_out'):
            modConf.user_dict['com_out_qs'][q] = child_qs[q]
        if q.startswith('audio_out'):
            modConf.user_dict['audio_out_qs'][q] = child_qs[q]


def create_threads(emp):
    """"""
    # input_q collect external commands and adapt
    t = threading.Thread(name='input_parent_thread',
                         target=input_collector_parent,
                         args=(emp,),
                         daemon=True).start()
    modConf.thread_lst.append(t)
    # create a thread loop to collect the information from all com_out queues and update user dict 'radios'
    t = threading.Thread(name='com_out_parent_thread',
                         target=com_out_collector_parent,
                         args=(emp,),
                         daemon=True).start()
    modConf.thread_lst.append(t)
    #
    t = threading.Thread(name='audio_out_parent_thread',
                         target=audio_out_collector_parent,
                         args=(emp,),
                         daemon=True).start()
    modConf.thread_lst.append(t)


def input_collector_parent(emp):
    """"""
    input_q = modConf.user_dict['input_q'] = emp.mp_input_q
    num_proc = modConf.user_dict['num_proc']
    last_proc = modConf.user_dict['last_proc']
    app_max = modConf.user_dict['app_max']
    radio_player = modConf.user_dict['radio_player']
    tup = None
    while 1:

        if not input_q.empty():
            tup = input_q.get()

            if not tup[0].startswith('create'):
                radio_num_dct = modConf.user_dict['radio_proc_num']
                radio = tup[0]
                if radio in radio_num_dct.keys():
                    emp.queue_cust_dict_cat['child_qs']['com_in_' + str(radio_num_dct[radio])].put(tup)
                    # ('nachtflug','exec', 'setattr(self,"runs_listen",True)

            if tup[0].startswith('create'):
                if last_proc > num_proc - 1:  # start_sequence_num of proc starts with zero
                    last_proc = 0
                radio, url, base_dir, balanced = tup[1], tup[2], tup[3], True
                try:
                    balanced = tup[4]
                except IndexError:
                    pass
                if balanced:
                    emp.queue_cust_dict_cat['child_qs']['com_in_' + str(last_proc)].put(tup)
                    modConf.user_dict['radio_proc_num'][radio] = last_proc
                    last_proc += 1
                else:
                    emp.queue_cust_dict_cat['child_qs']['com_in_' + str(last_proc)].put(tup)
                    modConf.user_dict['radio_proc_num'][radio] = last_proc

                # create_radio = ('create', 'nachtflug', 'http://85.195.88.149:11810', 'home/osboxes/abracadabra', True)

        time.sleep(0.1)


def com_out_collector_parent(emp):
    """Analyse tuples and lists.
    (A) Tuple of three is command output strings (radio, command, result).

    (B) Lists have information tuples in it.
    Tuple of two is info dict (radio, dict).
    """
    dct = emp.queue_cust_dict_cat['child_qs']
    com_out_q_lst = [dct[key] for key in dct.keys() if key.startswith('com_out')]
    while 1:
        out_lst = [q.get() for q in com_out_q_lst if not q.empty()]  # can contain lists and tuples

        for item in out_lst:
            if isinstance(item, list):
                tup_lst = item
                for tup in tup_lst:
                    radio, info_dct = tup
                    modConf.user_dict['radios'][radio] = info_dct
                    emp.kwargs['user_dict']['radios'][radio] = info_dct

            else:
                print(f'is_command_output {item}')

        time.sleep(2)


def audio_out_collector_parent(emp):
    """"""
    audio_ext_q = modConf.user_dict['audio_q'] = emp.mp_output_q  # external interface q
    audio_ch_dct = modConf.user_dict['audio_out_qs']  # child qs dict
    chunk = b''
    while 1:
        q_lst = [audio_ch_dct[q_name] for q_name in audio_ch_dct.keys()]
        for q in q_lst:
            if not q.empty():
                chunk = q.get()
            if not audio_ext_q.full():
                audio_ext_q.put(chunk)
                # print(chunk)
        time.sleep(0.1)


def main():
    """
    """
    import multiprocessing as mp

    mp.set_start_method('spawn', force=True)
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
