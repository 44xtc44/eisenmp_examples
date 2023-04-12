"""See some examples,
it's always the same process,
you extend or switch off defaults


Multiple server on each CPU core, if server has that many cores.
needs Flask_SQLAlchemy_Project_Template >=1.3
"""
import os
import time

import eisenmp


class ModuleConfiguration:
    """
    You can use the class to have your variables available in the module.

    """
    dir_name = os.path.dirname(__file__)  # our module path without file name
    # path to worker module and entry function reference, worker module import in process environment
    # -------------------- MANDATORY WORKER STRINGS --------------------
    first_module = {
        'WORKER_PATH': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_multi_srv_each_cpu.py'),
        'WORKER_REF': 'worker',  # Note: loader calls all f() with a single argument 'toolbox'; worker(toolbox)
    }
    foo = {'WORKER_PATH': 'bar', 'WORKER_REF': 'baz'}

    def __init__(self):
        # load order list, first module is called in an endless loop if it is not a thread
        self.worker_modules = [  # multi server on one CPU core
            self.first_module,
            self.first_module,
            self.first_module,  # each module_loader in the process loads this list
            self.first_module,
            self.first_module,
            self.first_module,  # just demo, same can be achieved if server called in a worker loop
        ]

        # Multiprocess vars - override default
        self.NUM_PROCS = 3  # your process count, default is None: one proc/CPU core
        self.NUM_ROWS = 1  # tell iterator to make only one list row, each worker needs only one number
        self.RESULTS_STORE = True  # keep in dictionary, will crash the system if store GB network chunks in mem
        self.RESULTS_PRINT = True  # result rows of output are collected in a list, display if processes are stopped
        self.RESULTS_DICT_PRINT = False  # shows content of results dict with ticket numbers, check tickets
        # self.START_METHOD = 'fork'  # 'spawn' is default if unused; also use 'forkserver' or 'fork' on Unix only

        self.STOP_MSG_disable = True  # module_loader leaves worker loop and waits for stop msg in mp_process_q

        # worker port groups, nailed on one cpu
        self.blue_lst = [0]  # one CPU core for blue list, if toolbox.kwargs['START_SEQUENCE_NUM'] in worker_blue_lst,
        self.yellow_lst = [1]  # one CPU core for yellow, process spawn num 1; (class ProcEnv 'run_proc -> core')
        self.green_lst = [2]


modConf = ModuleConfiguration()  # Accessible in the module.


def manager():
    """
    - Manager -

    !!! Database must be [created with one process only], then many procs can read, write !!!


    ORM https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping
    """
    # need a Queue for yellow and blue and an `existing` Database with numbers or generator range step
    q_name_maxsize = [
        # q_name, q_maxsize;
        ('mp_blue_q', 1),  # tuple, worker: toolbox.mp_blue_q.get()
        ('mp_yellow_q', 1),
        ('mp_green_q', 1)
    ]
    # default call
    mP = eisenmp.Mp()

    # custom queues for port groups ---> need a generator for each queue
    mP.queue_cust_dict_std_create(*q_name_maxsize)  # unpack, create Qs in std {default} dict ..['mp_blue_q']=Queue()

    # !!! config write instance dictionary if all args set !!!
    mP.start(**modConf.__dict__)  # feed toolbox, instance attributes available for worker and feeder loop

    port_generator_blue = (port_number for port_number in range(11_000, 11_006, 1))
    port_generator_yellow = (port_number for port_number in range(14_000, 14_006, 1))
    port_generator_green = (port_number for port_number in range(15_000, 15_006, 1))
    mP.run_q_feeder(generator=port_generator_blue, input_q=mP.queue_cust_dict_std['mp_blue_q'])
    mP.run_q_feeder(generator=port_generator_yellow, input_q=mP.queue_cust_dict_std['mp_yellow_q'])
    mP.run_q_feeder(generator=port_generator_green, input_q=mP.queue_cust_dict_std['mp_green_q'])


def main():
    """
    """
    start = time.perf_counter()

    manager()

    msg_time = f'\nMulti loader Time in sec: {round((time.perf_counter() - start))} - main() exits'
    print(msg_time)
    return msg_time


if __name__ == '__main__':
    main()
