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
    worker_module = {
        'WORKER_PATH': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_ghettorecorder.py'),
        'WORKER_REF': 'worker_entrance',
    }
    watchdog_module = {
        'WORKER_PATH': os.path.join(os.path.dirname(dir_name), 'worker', 'eisenmp_exa_wrk_watchdog.py'),
        'WORKER_REF': 'mp_start_show_threads',
    }

    def __init__(self, proc_max=3, app_max=3, proc_balance=True):
        self.worker_modules = [
            self.worker_module,  # other modules must start threaded, else we hang
            # self.watchdog_module  # second; thread function call mandatory, last module loaded first
        ]
        self.PROCS_MAX: int = proc_max  # I know it is int. process count, default is None: one proc per CPU core
        self.RESULT_LABEL = 'GhettoRecorder Multiprocessor Example'
        self.sleep_time = 20  # watchdog
        self.finish = False
        self.thread_lst = []
        self.q_dict_key = 'child_qs'
        self.user_dict = {'radios': {},  # dump attributes for JS ajax
                          'radio_proc_num': {},  # {radio name: process num} {'hm': 3,'paloma': 1}
                          'radio_player': '',  # name of current radio feeds audio_out
                          'num_proc': self.PROCS_MAX,
                          'last_proc': self.PROCS_MAX,  # last proc (start_sequence_num) started an app
                          'proc_balance': proc_balance,  # balancer or crowded knows next proc start_sequence_num
                          'app_max': app_max,  # limit num of app in a single proc
                          'input_q': None,  # eisenmp input_q for external command input to make exex tuples
                          'com_in_proc_qs': {},  # each proc get an input q
                          'com_out_shr_q': None,  # all procs share one output q
                          'audio_out_shr_q': None}  # all procs share one audio out q


modConf = ModuleConfiguration()  # Accessible in the module.


def frontend_entry():
    """Return dict for frontend. Connect qs and read content-type."""
    run_ghetto_example()
    return modConf


def manager_entry():
    """Run this module.
    | Must take category for qs. queue_cust_dict_category_create.
    | Access in worker toolbox.ghetto_qs['com_in_1']
    | Note: Can not access in worker toolbox['com_in_1'], only toolbox.com_in_1
    | Run Test on Manager:
    | create_radio = ('create', 'nachtflug', 'http://85.195.88.149:11810', 'home/osboxes/abracadabra')
    | emp.queue_cust_dict_cat['child_qs']['com_in_1'].put(create_radio)
    """
    emp = run_ghetto_example()
    return emp


def run_ghetto_example():
    """"""
    emp = eisenmp.Mp()
    create_parent_qs(emp)
    create_threads(emp)
    emp.start(**modConf.__dict__)  # create processes, load worker mods
    return emp


def create_parent_qs(emp):
    """Create multiple *input* qs, one *output q* and one *audio output q*.

    | Store qs in eisenmp instance to inform worker procs.
    | Store qs in modConf instance user dict to attach user frontend (FE). FE connect qs and pulls info from dict.
    """
    dct_name = modConf.q_dict_key
    q_name_maxsize_lst = [(dct_name, 'com_in_' + str(num), 1) for num in range(modConf.PROCS_MAX)]  # each proc one q
    q_name_maxsize_lst.append((dct_name, 'com_out', modConf.PROCS_MAX * 5))  # all procs one q
    q_name_maxsize_lst.append((dct_name, 'audio_out', 1))  # dito
    # create custom queues, stored in a dictionary for the worker processes
    emp.queue_cust_dict_category_create(*q_name_maxsize_lst)

    child_qs = emp.queue_cust_dict_cat[dct_name]
    modConf.user_dict['input_q'] = emp.mp_input_q
    modConf.user_dict['com_in_proc_qs'] = {q: child_qs[q] for q in child_qs.keys() if q.startswith('com_in')}
    modConf.user_dict['com_out_shr_q'] = child_qs['com_out']
    modConf.user_dict['audio_out_shr_q'] = child_qs['audio_out']


def create_threads(emp):
    """Put commands from frontend in input q.
    Collect output info of all app instances.
    """
    # input_q collect external commands
    t = threading.Thread(name='input_parent_thread',
                         target=input_collector_parent,
                         args=(emp,),
                         daemon=True).start()
    modConf.thread_lst.append(t)
    # collect the information from all com_out queues and update user dict 'radios'
    t = threading.Thread(name='com_out_parent_thread',
                         target=com_out_collector_parent,
                         args=(emp,),
                         daemon=True).start()
    modConf.thread_lst.append(t)


def input_collector_parent(emp):
    """Frontend sends commands to parent process input q.
    Input q forks to *com_in* process queues.

    | Function analyses command tuples.
    | Each app instance is stored with its process number.
    """
    modConf.user_dict['input_q'] = emp.mp_input_q
    a_dct = {
        'input_q': emp.mp_input_q,
        'num_proc': modConf.user_dict['num_proc'],
        'last_proc': modConf.user_dict['last_proc'],
        'app_max': modConf.user_dict['app_max'],
        'radio_player': modConf.user_dict['radio_player']
    }
    while 1:
        if modConf.finish:
            time.sleep(3)
            return
        if not a_dct['input_q'].empty():
            tup = a_dct['input_q'].get()
            if not isinstance(tup, tuple):
                return

            if tup[0].startswith('create') or tup[0].startswith('shutdown_process'):
                input_put_function(emp, tup, q_dict_key=modConf.q_dict_key, a_dct=a_dct)  # throw in q
            else:
                input_put_command(emp, tup, q_dict_key=modConf.q_dict_key)  # analyse further
        time.sleep(0.1)


def input_put_function(emp, tup, q_dict_key, a_dct):
    """Each app instance is stored with its process number.
    User can send commands to correct process, app.

    Balanced means putting next app instance into next process number.
    Else stack until upper limit hits.

    :params: emp: eisenmp instance, controls the process creation and provide default qs
    :params: tup: tuple with arguments for recorder instance creation
    :params: q_dict_key: modConf.q_dict_key[q_dict_key] dictionary, key name to access dict with qs references
    :params: a_dct: custom dict with eisenmp and modConf.user_dict key values, prevent mass variable usage
    """
    if a_dct['last_proc'] > a_dct['num_proc'] - 1:  # start_sequence_num of proc starts with zero
        a_dct['last_proc'] = 0

    if tup[0].startswith('create'):
        input_create_recorder(emp, tup, q_dict_key, a_dct)

    elif tup[0].startswith('shutdown_process'):
        input_shutdown_procs(emp, tup, q_dict_key, a_dct)
    else:
        print('input_put_function(): first arg not valid.')


def input_create_recorder(emp, tup, q_dict_key, a_dct):
    """Request instance creation of recorder.

    :params: emp: eisenmp instance, controls the process creation and provide default qs
    :params: tup: tuple with arguments for recorder instance creation
    :params: q_dict_key: modConf.q_dict_key[q_dict_key] dictionary, key name to access dict with qs references
    :params: a_dct: custom dict with eisenmp and modConf.user_dict key values, prevent mass variable usage
    """
    radio, balanced = tup[1], True
    # app_instance_count = 0  # not balanced, fill proc up to limit then next proc

    try:
        balanced = tup[4]
    except IndexError:
        pass
    radio = tup[1]
    if radio in modConf.user_dict['radio_proc_num'].keys():
        return
    if balanced:
        emp.queue_cust_dict_cat[q_dict_key]['com_in_' + str(a_dct['last_proc'])].put(tup)
        modConf.user_dict['radio_proc_num'][radio] = a_dct['last_proc']
        a_dct['last_proc'] += 1
    else:
        emp.queue_cust_dict_cat[q_dict_key]['com_in_' + str(a_dct['last_proc'])].put(tup)
        modConf.user_dict['radio_proc_num'][radio] = a_dct['last_proc']


def input_shutdown_procs(emp, tup, q_dict_key, a_dct):
    """Shutdown all or requested processes.

    :params: emp: eisenmp instance, controls the process creation and provide default qs
    :params: tup: tuple with arguments for recorder instance creation
    :params: q_dict_key: modConf.q_dict_key[q_dict_key] dictionary, key name to access dict with qs references
    :params: a_dct: custom dict with eisenmp and modConf.user_dict key values, prevent mass variable usage
    """
    if tup[1].startswith('all'):
        for idx in range(0, a_dct['num_proc']):
            # throw in all input qs
            emp.queue_cust_dict_cat[q_dict_key]['com_in_' + str(idx)].put(('shutdown_process', idx, '---'))
            print(f'\tinit shutdown worker START_SEQUENCE_NUM: {idx}')
            modConf.finish = True
    else:
        # put in requested q
        emp.queue_cust_dict_cat[q_dict_key]['com_in_' + str(int(tup[1]))].put(tup)


def input_put_command(emp, tup, q_dict_key):
    """Distribute commands::

        ('nachtflug','exec', 'setattr(self,"runs_listen",True) to process, app.

    :params: emp: eisenmp instance, controls the process creation and provide default qs
    :params: tup: tuple with arguments for recorder instance creation
    :params: q_dict_key: modConf.q_dict_key[q_dict_key] dictionary, key name to access dict with qs references
    """
    radio_num_dct = modConf.user_dict['radio_proc_num']
    cmd_args_idx = 2
    radio_name = tup[0]

    # stop current radio player
    if 'runs_listen' in tup[cmd_args_idx] and 'True' in tup[cmd_args_idx]:
        if not modConf.user_dict['radio_player']:
            modConf.user_dict['radio_player'] = radio_name
        else:
            player = modConf.user_dict['radio_player']
            proc_num = radio_num_dct[player]
            stop_cmd = (player, 'exec', 'setattr(self,"runs_listen", False)')
            emp.queue_cust_dict_cat[q_dict_key]['com_in_' + str(proc_num)].put(stop_cmd)

    if radio_name in radio_num_dct.keys():
        emp.queue_cust_dict_cat[q_dict_key]['com_in_' + str(radio_num_dct[radio_name])].put(tup)
    else:
        print('\n\t input_put_command(): radio name not in dictionary.', radio_name)

    # check instance removal, after command exec
    if 'shutdown' in tup[cmd_args_idx] and 'True' in tup[cmd_args_idx] and radio_name in radio_num_dct.keys():
        del radio_num_dct[radio_name]


def com_out_collector_parent(emp):
    """Analyse tuples and lists.
    (A) Tuple of three is command output strings (radio, command, result).

    (B) Lists have information tuples in it.
    Tuple of two is info dict (radio, dict). Each radio collects header info and status.
    """
    dct_name = modConf.q_dict_key
    q_dct = emp.queue_cust_dict_cat[dct_name]
    garbage_list = []   # eisenmp puts lists with commands for status and shutdown in all qs

    while 1:
        if modConf.finish:
            time.sleep(3)
            return
        tup_lst = []
        while not q_dct['com_out'].empty():
            item = q_dct['com_out'].get()
            if isinstance(item, tuple):
                tup_lst.append(item)
            else:
                garbage_list.append(item)

        for tup in tup_lst:
            radio, info_dct, *rest = tup
            modConf.user_dict['radios'][radio] = info_dct
            emp.kwargs['user_dict']['radios'][radio] = info_dct

        for item in range(0, len(garbage_list)):
            q_dct['com_out'].put(garbage_list.pop())  # return to q, eisenmp can auto shutdown procs

        time.sleep(5)


def main():
    """"""
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
