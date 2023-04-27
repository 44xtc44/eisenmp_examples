"""Template for Manager

- Watchdog Thread included, shows pid of its proc
- double feeder
- custom queues and queues in category
- fake production of audio and video coding, is loop through to result dict
- two processors work on different streams, batches, (src is same here, so what)

"""
import os
import threading
import time
import eisenmp
import eisenmp.utils.eisenmp_utils as e_utils

dir_name = os.path.dirname(__file__)


chunks_0 = [
    # some 'binaries'
    b'\x94\x80\x12\'',
    bytes("<html><head>", "utf-8"),
    bytes(5),
    b'\x8e|\x1e\x95\'',
    b'\xbe\xb0-\xeex\'',
    b'\xf5\x98\x16$\'',
    b'\x13\xb7\x12XB\'',
    b'\x16\xbb\xe5MX\'',
    b'\x94\x80\x12\'',
    bytes("<html><head>", "utf-8"),
    bytes(5),
    b'\x8e|\x1e\x95\'',
    b'\xbe\xb0-\xeex\'',
    b'\xf5\x98\x16$\'',
    b'\x13\xb7\x12XB\'',
    b'\x16\xbb\xe5MX\'',
    b'\x94\x80\x12\'',
]

chunks_1 = [
    # some 'binaries'
    b'\x94\x80\x12\'',
    bytes("<html><head>", "utf-8"),
    b'\x13\xb7\x12XB\'',
    b'\x16\xbb\xe5MX\'',
    b'\x94\x80\x12\'',
    bytes(5),
    b'\x8e|\x1e\x95\'',
    b'\xbe\xb0-\xeex\'',
    b'\xf5\x98\x16$\'',
    b'\x13\xb7\x12XB\'',
    b'\x16\xbb\xe5MX\'',
    b'\x94\x80\x12\'',
    bytes("<html><head>", "utf-8"),
    b'\x13\xb7\x12XB\'',
    b'\x16\xbb\xe5MX\'',
    b'\x94\x80\x12\'',
    bytes(5),
    b'\x8e|\x1e\x95\'',
    b'\xbe\xb0-\xeex\'',
    b'\xf5\x98\x16$\'',
]


class ModuleConfiguration:  # name your own class and feed eisenmp with the dict
    """More advanced template. Multiprocess 'spawn' in 'ProcEnv' to work with all OS.
    - toolbox.kwargs shows all avail. vars and dead references of dicts, lists, instances, read only

    """
    template_module = {
        'WORKER_PATH': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_double.py'),
        'WORKER_REF': 'worker_entrance',
    }
    watchdog_module = {
        'WORKER_PATH': os.path.join(os.path.dirname(dir_name), 'worker', 'eisenmp_exa_wrk_watchdog.py'),
        'WORKER_REF': 'mp_start_show_threads',
    }

    def __init__(self):

        self.worker_modules = [  # in-bld-res
            self.template_module,  # other modules must start threaded, else we hang
            # self.watchdog_module  # second; thread function call mandatory, last module loaded first
        ]

        # Multiprocess vars - override default
        self.PROCS_MAX = 2  # your process count, each 'batch' on one CPU core, default is None: one proc/CPU core
        self.ROWS_MAX = 3  # arbitrary num here
        self.RESULTS_STORE = True  # keep in dictionary, will crash the system if store GB network chunks in mem
        self.RESULTS_PRINT = True  # result rows of output are collected in a list, display if processes are stopped
        self.RESULT_LABEL = 'fake production of audio and video for WHO studios'  # RESULT_LABEL for RESULTS_PRINT
        self.RESULTS_DICT_PRINT = True  # shows content of results dict with ticket numbers, check tickets
        # self.START_METHOD = 'fork'  # 'spawn' is default if unused; also use 'forkserver' or 'fork' on Unix only

        # work to do
        self.sleep_time = 20  # watchdog
        self.num_of_lists = 0  # worker lists done counter

        # vars lived before in worker module classes
        self.header_aud = None  # pre-defined, use in whole worker mod, save input list header to mark output header
        self.header_vid = None  # output from multiple queues must be divided, default is only one output queue for all
        self.BLUE = '\033[1;34;48m'
        self.RED = '\033[1;31;48m'
        self.END = '\033[1;37;0m'


modConf = ModuleConfiguration()  # Accessible in the module.


def manager_entry():
    """
    - Generator - One time execution.

    Divide workload between processes / CPU
    -
    """
    q_cat_name_maxsize = [
        # q_category, q_name, q_maxsize; find your 100 Queues in the debugger, toolbox
        ('batch_1', 'audio_lg', 5),  # queues for batch_1
        ('batch_1', 'video_in', 1),  # dict avail. in worker module: toolbox.batch_1['video_in'].get()
        ('batch_7', 'audio_lg', 3),  # queues for batch_7
        ('batch_7', 'video_in', 1)
    ]
    emp = eisenmp.Mp()

    # create custom queues with category and name
    emp.queue_cust_dict_category_create(*q_cat_name_maxsize)  # create queues, store in {custom} {category} dict

    audio_q_b1 = emp.queue_cust_dict_cat['batch_1']['audio_lg']  # USE Queue:
    video_q_b1 = emp.queue_cust_dict_cat['batch_1']['video_in']  # worker module: toolbox.batch_1['video_in'].get()
    audio_q_b7 = emp.queue_cust_dict_cat['batch_7']['audio_lg']
    video_q_b7 = emp.queue_cust_dict_cat['batch_7']['video_in']  # toolbox.batch_7['video_in'].get()

    emp.start(**modConf.__dict__)  # create processes, load worker mods, start threads (output_p coll, info)
    emp.run_q_feeder(generator=audio_generator_batch_1(), input_q=audio_q_b1)
    emp.run_q_feeder(generator=video_generator_batch_1(), input_q=video_q_b1)
    emp.run_q_feeder(generator=audio_generator_batch_7(), input_q=audio_q_b7)
    emp.run_q_feeder(generator=video_generator_batch_7(), input_q=video_q_b7)

    return emp


def audio_generator_batch_1():
    """"""
    for _ in chunks_0:
        yield _


def video_generator_batch_1():
    """"""
    for _ in chunks_1:
        yield _


def audio_generator_batch_7():
    """"""
    for _ in chunks_0:
        yield _


def video_generator_batch_7():
    """"""
    for _ in chunks_1:
        yield _


def main():
    """
    """
    start = time.perf_counter()

    emp = manager_entry()
    while 1:
        # running threads, wait
        if emp.begin_proc_shutdown:
            break
        time.sleep(1)

    msg_time = 'Fake production, Time in sec: ', round((time.perf_counter() - start))
    print(msg_time)
    msg_result = e_utils.Result.result_dict

    names_list = [thread.name for thread in threading.enumerate()]
    print(names_list)
    return msg_result


if __name__ == '__main__':
    main()
