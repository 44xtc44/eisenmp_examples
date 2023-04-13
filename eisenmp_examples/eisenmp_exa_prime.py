"""Multiprocessor Prime number finder (worker) and number Generator.

Example for a ``two in one module``. Manager and worker.

This is NOT ADVISABLE and only to show the mechanics.
Use a separate worker module to not import your 'Generator' imports twice.
That is what the loader is for.
"""
import os
import time
import math
import platform

import eisenmp
import eisenmp.utils.eisenmp_utils as e_utils

dir_name = os.path.dirname(__file__)


class ModuleConfiguration:
    """
    You can use the class to have your variables available in the module.

    'worker_prime()' is executed by all processes on a CPU somewhere.
    Each 'worker_prime()' gets (one by one) a list chunk from eisenmp.mp_input_q.
    You have full access to all queues and methods. mp = eisenmp.Mp()
    """
    # path to worker module and entry function reference, worker module import in [isolated] process environment
    # -------------------- MANDATORY WORKER STRINGS --------------------
    first_module = {
        'WORKER_PATH': os.path.join(dir_name, 'eisenmp_exa_prime.py'),
        'WORKER_REF': 'worker_prime',  # loader runs worker_prime(toolbox) to provide all args from toolbox (kwargs)
    }
    foo = {'WORKER_PATH': 'bar', 'WORKER_REF': 'baz'}

    def __init__(self):
        # load order list, first module is called in an endless loop
        self.worker_modules = [
            self.first_module,   # second module must be threaded, else we hang
            # foo
        ]

        # Multiprocess vars - override default
        self.NUM_PROCS = 5  # your process count, default is None: one proc/CPU core
        # max generator / NUM_ROWS = number of tickets, 10_000 / 42 = 238.095 -> 238 lists with ticket numbers
        self.NUM_ROWS = 42  # your workload spread, list (generator items) to calc in one loop, default is None: 1_000
        self.RESULTS_STORE = True  # keep in dictionary, will crash the system if store GB network chunks in mem
        self.RESULTS_PRINT = True  # result rows of output are collected in a list, display if processes are stopped
        self.RESULTS_DICT_PRINT = True  # shows content of results dict with ticket numbers, check tickets
        if platform.system() == 'Linux':
            self.START_METHOD = 'fork'  # 'spawn' is default if unused; also use 'forkserver' or 'fork' on Unix only

        # custom part, write your own Attributes
        self.range_num = 10 ** 4  # got a target/max value and NUM_ROWS for each proc, can calc ETA est. time arrival
        self.INFO_THREAD_MAX = self.range_num  # target value for info thread to calculate % and ETA
        # self.INFO_ENABLE = True  # [baustelle]
        self.n = 10 ** 12  # ten with zero count, 10_000_000_000_000_000
        self.say_hello = 'Hello'  # just to show that worker can [read] all attributes of instance, in 'worker_prime()'


modConf = ModuleConfiguration()  # Accessible in the module.


def generator_prime():
    """Manager - One time execution.
    Exits if generator is empty.
    """
    # auto
    mP = eisenmp.Mp()

    mP.start(**modConf.__dict__)  # instance attributes available for worker and feeder loop
    generator = number_generator()
    mP.run_q_feeder(generator=generator, input_q=mP.mp_input_q)  # here default mp_input_q, use if only one q needed

    return mP


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
    - WORKER - Called with a single arg (name it xyz) in a loop until returns False.

    Start, Entry, Exit of this 'single' process worker.
    We return True to get next list chunk, whatever object is in the rows.
    Fed from mp_input_q to our toolbox. toolbox is your work instance with queues,
    messages, list chunk, and work tools like language dictionary or hash list.

    toolbox.foo, gives also access to all attributes and values
    of the 'modConf.foo' instance, you have created
    """
    # toolbox.mp_print_q.put(toolbox.say_hello)
    busy = workload_get(toolbox)
    calc_prime(toolbox)  # start worker function, exit afterwards if stop received
    if not busy:
        return False
    send_eta_data(toolbox)  # send data list, first row is header, info thread can find it in eisenmp.output_q_box
    return True


def workload_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_input_q.empty():
            toolbox.NEXT_LIST = toolbox.mp_input_q.get()  # NEXT_LIST is pre-defined, you can declare your own var
            break
    if toolbox.STOP_MSG in toolbox.NEXT_LIST:  # eisenmp.iterator_loop() informs stop, no more lists
        return False  # loader sends shutdown msg to next worker - generator is empty
    return True


def calc_prime(toolbox):
    """Calc prime num.

    The stop message is detected in 'workload_get', in this example.
    """
    remove_header(toolbox)

    # calc
    lst = toolbox.NEXT_LIST  # NEXT_LIST is default var for the new list in mp_input_q
    stop_msg = toolbox.STOP_MSG  # string 'STOP'
    prime_lst = [str(num) for num in lst if num is not stop_msg and type(num) is int and is_prime(num)]

    send_output(toolbox, prime_lst)

    # print message
    primes = ''.join(str(prime_lst)) if len(prime_lst) else ''
    output_msg = f' ... Result {toolbox.WORKER_NAME} ... Prime {primes}'
    toolbox.mp_print_q.put(output_msg) if len(prime_lst) else None  # blocks the whole mp


def is_prime(n: int) -> bool:
    """https://en.wikipedia.org/wiki/Primality_test

    mod by 44xtc44, limit = int(math.sqrt(n)) , isqrt(n) is Python 3.8, package shall run 3.7
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    limit = int(math.sqrt(n))  # python 3.8 isqrt(n) humbug
    for i in range(5, limit + 1, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True


def send_output(toolbox, prime_lst):
    """Put your findings in the output list.
    Find results in the 'eisenmp_utils.Result.result_dict'

    :params: toolbox: -
    :params: prime_lst: findings of prime num calc
    """
    # OUTPUT_HEADER - mandatory, INPUT_HEADER - q collector distinguish queues, write own strings if multiple queues
    header = toolbox.OUTPUT_HEADER + toolbox.INPUT_HEADER  # INPUT_HEADER pre-defined, or write your own to find result
    result_lst = [header,
                  prime_lst]  # your findings here
    toolbox.mp_output_q.put(result_lst)


def send_eta_data(toolbox):
    """list of [PERF_HEADER_ETA, PERF_CURRENT_ETA] to ProcInfo, to calc arrival time ETA
    """
    toolbox.PERF_CURRENT_ETA = len(toolbox.NEXT_LIST)
    perf_lst = [toolbox.PERF_HEADER_ETA + toolbox.WORKER_NAME,  # binary head
                toolbox.PERF_CURRENT_ETA]
    # disable info q collector will block all
    toolbox.mp_info_q.put(perf_lst)  # ProcInfo calc arrival time and % from info_q, of all proc lists


def remove_header(toolbox):
    """Transport ticket with consecutive number.
    Remove if no recreation of order is necessary.
    """
    # toolbox.mp_print_q.put(toolbox.NEXT_LIST[0])
    toolbox.INPUT_HEADER = toolbox.NEXT_LIST[0]  # header with name of input Queue and serial number, for output Queue
    del toolbox.NEXT_LIST[0]  # remove header str from list, which you get from input Q


def main():
    """
    """
    start = time.perf_counter()

    mP = generator_prime()
    while 1:
        # running threads, wait
        if mP.begin_proc_shutdown:
            break
        time.sleep(1)

    msg_time = 'Example Prime numbers, Time in sec: ', round((time.perf_counter() - start))
    print(msg_time)
    msg_result = e_utils.Result.result_dict

    return msg_result


if __name__ == '__main__':
    main()
