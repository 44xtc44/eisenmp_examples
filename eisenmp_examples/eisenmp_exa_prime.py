"""Multiprocessor Prime number finder (worker) and number Generator.

Example for a ``two in one module``. Generator and worker. 'generator_prime'/'worker_prime'
"""
import os
import time
from math import isqrt

import eisenmp
dir_name = os.path.dirname(__file__)


class ModuleConfiguration:
    """
    You can use the class to have your variables available in the module.

    'worker_prime()' is executed by all processes on a CPU somewhere.
    Each 'worker_prime()' gets (one by one) a list chunk from eisenmp.mp_input_q.
    You have full access to all queues and methods, GhettoBoss has. eisenmp = eisenmp.GhettoBoss()
    """
    # path to worker module and entry function reference, worker module import in [isolated] process environment
    # -------------------- MANDATORY WORKER STRINGS --------------------
    first_module = {
        'WORKER_PATH': os.path.join(dir_name, 'eisenmp_exa_prime.py'),
        'WORKER_REF': 'worker_prime',  # Warning: loader runs all f(toolbox) as single argument; pull args from toolbox
    }
    foo = {'WORKER_PATH': 'bar', 'WORKER_REF': 'baz'}

    def __init__(self):
        # load order list, first module is called in an endless loop, you can append your own loop inside the worker
        self.worker_modules = [
            self.first_module,   # second module must be threaded, else we hang
            # foo
        ]
        # manager
        self.num_cores = 6  # number of process we want, default is None: one proc/CPU core
        self.num_rows = 42  # spread workload, list rows to calc in one loop, default is None: 10_000
        self.store_result = True  # keep in dictionary, can crash the system if working with network chunks

        # custom part, write your own Attributes
        self.range_num = 1_000  # we got a target/max value and num_rows for each proc, can calc ETA est. time arrival
        self.info_td_max = self.range_num  # target value for info thread to calculate % and ETA
        self.n = 10 ** 7  # 10_000_000_000_000_000 .....
        self.result_lbl = 'Large PRIME numbers '
        self.say_hello = 'Hello'  # just to show that worker can [read] all attributes of instance, in 'worker_prime()'


modConf = ModuleConfiguration()  # Accessible in the module.


def generator_prime():
    """Manager

    - Generator - One time execution.
    """
    # auto
    mP = eisenmp.Mp()

    generator = number_generator()
    mP.start(**modConf.__dict__)  # instance attributes available for worker and feeder loop
    mP.run_q_feeder(generator=generator)  # also 'header_msg' modConf   header_msg='MAXIMUS_PRIME'


def number_generator():
    """Generates numbers from start count.
    Has an end value, range.
    """
    range_num = modConf.range_num
    n = modConf.n  # start with a large number to see some work in progress
    for _ in range(range_num):
        yield n
        n += 1


def worker_prime(toolbox):
    """
    - WORKER -      Called in a loop until returns False.

    Start, Entry, Exit of this 'single' process worker.
    We return True to get next list chunk, whatever object is in the rows.
    Fed from mp_input_q to our toolbox. toolbox is our work instance with queues,
    messages, list chunk, and work tools like language dictionary or hash list.

    toolbox.foo, gives also access to all attributes and values
    of the 'modConf.foo' instance, you have created
    """
    # toolbox.mp_print_q.put(toolbox.say_hello)
    busy = workload_get(toolbox)
    calc_prime(toolbox)  # start worker function
    if not busy:
        return False
    send_eta_data(toolbox)  # send data list, first row is header, info thread can find it in eisenmp.output_q_box
    return True


def workload_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_input_q.empty():
            toolbox.next_lst = toolbox.mp_input_q.get()
            break
    if toolbox.stop_msg in toolbox.next_lst:  # eisenmp.iterator_loop() informs stop, no more lists
        return False  # loop worker sends shutdown msg to next worker - generator is empty
    return True


def calc_prime(toolbox):
    """Calc prime num.
    """
    remove_header(toolbox)

    # calc
    lst = toolbox.next_lst  # next_lst is default var for the new list in mp_input_q
    stop_msg = toolbox.stop_msg  # string 'STOP'
    prime_lst = [str(num) for num in lst if num is not stop_msg and type(num) is int and is_prime(num)]

    # output result
    result_lst = [toolbox.result_header_proc,  # result list, stored in 'eisenmp.output_q_box' dictionary
                  prime_lst]
    toolbox.mp_output_q.put(result_lst)  # result thread reads the header, if ok store result in a list

    # print message
    primes = ''.join(str(prime_lst)) if len(prime_lst) else ''
    output_msg = f' ... Result {toolbox.worker_name} ... Prime {primes}'
    toolbox.mp_print_q.put(output_msg) if len(prime_lst) else None  # blocks the whole mp


def is_prime(n: int) -> bool:
    """https://en.wikipedia.org/wiki/Primality_test
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    limit = isqrt(n)
    for i in range(5, limit + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True


def send_eta_data(toolbox):
    """list of [perf_header_eta, perf_current_eta] to ProcInfo, to calc arrival time ETA
    """
    toolbox.perf_current_eta = len(toolbox.next_lst)
    perf_lst = [toolbox.perf_header_eta + toolbox.worker_name,  # binary head
                toolbox.perf_current_eta]
    # disable info q will block all
    toolbox.mp_info_q.put(perf_lst)  # ProcInfo calc arrival time and % from info_q, of all proc lists


def remove_header(toolbox):
    """Transport ticket with consecutive number.
    Remove if no recreation of order is necessary.
    Can reuse list for result, if rebuild order.

    Use self.header_msg attribute to overwrite default header string
    """
    # toolbox.mp_print_q.put(toolbox.next_lst[0])
    del toolbox.next_lst[0]  # remove header str


def main():
    """
    """
    start = time.perf_counter()

    generator_prime()

    print('Time in sec: ', round((time.perf_counter() - start)))


if __name__ == '__main__':
    main()
