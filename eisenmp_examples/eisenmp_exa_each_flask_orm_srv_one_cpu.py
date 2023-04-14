"""See some examples,
it's always the same process,
you extend or switch off defaults

"""
import os
import time

import eisenmp


class ModuleConfiguration:
    """
    You can use the class to have your variables available in the module.

    """
    dir_name = os.path.dirname(__file__)  # our module path without file name
    # path to worker module and entry function reference, worker module import in [isolated] process environment
    # -------------------- MANDATORY WORKER STRINGS --------------------
    first_module = {
        'WORKER_PATH': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_flask_orm_srv_one_cpu.py'),
        'WORKER_REF': 'worker',  # Warning: loader runs all f() with a single argument 'toolbox'; pull args from it
    }
    foo = {'WORKER_PATH': 'bar', 'WORKER_REF': 'baz'}

    def __init__(self):
        # load order list, first module is called in an endless loop, you can append your own loop inside the worker
        self.worker_modules = [self.first_module]

        # Multiprocess vars - override default
        self.NUM_PROCS = 6  # your process count, default is None: one proc/CPU core
        self.NUM_ROWS = 1  # tell iterator to make only one list row, each worker needs only one number
        self.RESULTS_STORE = True  # keep in dictionary, will crash the system if store GB network chunks in mem
        self.RESULTS_PRINT = True  # result rows of output are collected in a list, display if processes are stopped
        self.RESULT_LABEL = 'No result, server blocks'  # pretty print as result header for RESULTS_PRINT
        self.RESULTS_DICT_PRINT = False  # shows content of results dict with ticket numbers, check tickets
        # self.START_METHOD = 'fork'  # 'spawn' is default if unused; also use 'forkserver' or 'fork' on Unix only


modConf = ModuleConfiguration()  # Accessible in the module.


def manager():
    """
    - Manager -

    !!! Database must be [created with one process only], then many procs can read, write !!!
    """
    # need a Queue for yellow and blue and an `existing` Database with numbers or generator range step
    q_name_maxsize = [
        # q_name, q_maxsize;
        ('mp_blue_q', 1),  # tuple, worker: toolbox.mp_blue_q.get()
        ('mp_yellow_q', 1)
    ]
    # default call
    mP = eisenmp.Mp()

    # custom queues for port groups ---> need a generator for each queue
    mP.queue_cust_dict_std_create(*q_name_maxsize)  # unpack, create Qs in std {default} dict ..['mp_blue_q']=Queue()

    port_blue = (port_number for port_number in range(13_000, 13_006, 2))
    port_yellow = (port_number for port_number in range(14_000, 14_006, 2))

    # !!! config write instance dictionary if all args set !!!
    mP.start(**modConf.__dict__)  # feed toolbox, instance attributes available for worker and feeder loop
    mP.run_q_feeder(generator=port_blue, input_q=mP.queue_cust_dict_std['mp_blue_q'])
    mP.run_q_feeder(generator=port_yellow, input_q=mP.queue_cust_dict_std['mp_yellow_q'])


def main():
    """
    """
    start = time.perf_counter()

    manager()
    msg = f'\nFlask ORM - each one proc, Time in sec: {round((time.perf_counter() - start))} - main() exit'
    print(msg)
    return msg


if __name__ == '__main__':
    main()
