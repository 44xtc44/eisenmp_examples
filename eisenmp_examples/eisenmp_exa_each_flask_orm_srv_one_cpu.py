"""See some examples,
it's always the same process,
you extend or switch off defaults

"""
import os
import time

import eisenmp
from Flask_SQLAlchemy_Project_Template import create_app, setup_database, db_path


class ModuleConfiguration:
    """
    You can use the class to have your variables available in the module.

    """
    dir_name = os.path.dirname(__file__)  # our module path without file name
    # path to worker module and entry function reference, worker module import in [isolated] process environment
    # -------------------- MANDATORY WORKER STRINGS --------------------
    first_module = {
        'WORKER_PATH': os.path.join(dir_name, 'eisenmp_exa_each_flask_orm_srv_one_cpu.py'),
        'WORKER_REF': 'worker',  # Warning: loader runs all f() with a single argument 'toolbox'; pull args from it
    }
    foo = {'WORKER_PATH': 'bar', 'WORKER_REF': 'baz'}

    def __init__(self):
        # load order list, first module is called in an endless loop, you can append your own loop inside the worker
        self.worker_modules = [self.first_module]

        self.num_cores = 6  # number of process we want, default is None: one proc/CPU core
        self.num_rows = 1  # tell iterator to make only one list row, each worker needs only one number

        # worker port groups
        self.blue_lst = [1, 2, 3]  # 3 CPU cores for blue, if worker_id in worker_blue_lst,
        self.red_lst = [4, 5, 6]  # 3 CPU cores for red
        self.port_blue_lst = [100, 102, 104]  # this won't work with pop(), references are dead (and) list not shared
        self.port_red_lst = [200, 203, 206]  # this won't work with pop(), references are dead
        # see manager


modConf = ModuleConfiguration()  # Accessible in the module.


def manager():
    """
    - Manager -

    !!! Database must be [created with one process only], then many procs can read, write !!!


    ORM https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping
    """
    # need a Queue for red and blue and an `existing` Database with numbers or generator range step
    q_name_maxsize = [
        # q_name, q_maxsize;
        ('mp_blue_q', 1),  # tuple, worker: toolbox.mp_blue_q.get()
        ('mp_red_q', 1)
    ]
    # default call
    mP = eisenmp.Mp()

    # custom queues for port groups ---> need a generator for each queue
    mP.queue_cust_dict_std_create(*q_name_maxsize)  # unpack, create Qs in std {default} dict ..['mp_blue_q']=Queue()

    # !!! config write instance dictionary if all args set !!!
    mP.start(**modConf.__dict__)  # feed toolbox, instance attributes available for worker and feeder loop

    mP.run_q_feeder(generator=port_generator_blue(), feeder_input_q=mP.queue_cust_dict_std['mp_blue_q'])

    port_generator_red = (port_number for port_number in range(12_000, 12_006, 2))
    mP.run_q_feeder(generator=port_generator_red, feeder_input_q=mP.queue_cust_dict_std['mp_red_q'])


def port_generator_blue():
    for port_number in range(11_000, 11_006, 2):
        yield port_number


def worker(toolbox):  # name this arg as you like
    """
    - Worker -

    toolbox is the all-in-one box for vars and queues. incl. ModuleConfiguration
    """
    color_dict = {
        'PURPLE': '\033[1;35;48m',
        'CYAN': '\033[1;36;48m',
        'BOLD': '\033[1;37;48m',
        'BLUE': '\033[1;34;48m',
        'GREEN': '\033[1;32;48m',
        'YELLOW': '\033[1;33;48m',
        'RED': '\033[1;31;48m',
        'BLACK': '\033[1;30;48m',
        'UNDERLINE': '\033[4;37;48m',
        'END': '\033[1;37;0m',
    }

    # port group
    port, col = 0, None
    if toolbox.worker_id in toolbox.blue_lst:
        col = color_dict['BLUE']
        port = blue_q_get(toolbox)[1]  # [0] is header row
    if toolbox.worker_id in toolbox.red_lst:
        col = color_dict['RED']
        port = red_q_get(toolbox)[1]

    col_end = color_dict['END']
    col = color_dict['CYAN'] if col is None else col

    msg = col + f'\nWORKER_MSG worker: {toolbox.worker_id} pid: {toolbox.worker_pid} server port: {port}' + col_end
    toolbox.mp_print_q.put(msg)

    # Flask
    app_factory = create_app(port)  # flask, we feed port number to update the route -> Html page with our address
    if not os.path.isfile(db_path):  # do not kill db, if exists; MUST exist if many srv, else create by many srv, crash
        setup_database(app_factory)
    app_factory.run(host="localhost", port=port)


def blue_q_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_blue_q.empty():
            port_lst = toolbox.mp_blue_q.get()  # has header with serial number
            return port_lst


def red_q_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_red_q.empty():
            port_lst = toolbox.mp_red_q.get()  # has header with serial number
            return port_lst


def main():
    """
    """
    start = time.perf_counter()

    manager()

    print(f'\nFlask ORM Time in sec: {round((time.perf_counter() - start))} - main() exit')


if __name__ == '__main__':
    main()
