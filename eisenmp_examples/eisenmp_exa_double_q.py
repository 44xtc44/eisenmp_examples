"""Template for Manager

- Watchdog Thread included, shows pid of its proc
- double feeder
- custom queues and queues in category

"""
import os
import time

import eisenmp

dir_name = os.path.dirname(__file__)


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
        super().__init__()
        self.worker_modules = [  # in-bld-res
            self.template_module,  # other modules must start threaded, else we hang
            self.watchdog_module,  # second; thread function call mandatory, last module loaded first
        ]
        # system
        self.num_cores = 2  # in-bld-res, number of processes we want, default is None: one proc/CPU core
        self.num_rows = 3  # in-bld-res, workload; can script (cores, rows count, q_max, get time) find system balance
        self.store_result = True  # keep in dictionary, can crash the system mem if working with network chunks

        # work to do
        self.range_num = 10 ** 3  # number of work units in generator
        self.info_td_max = self.range_num  # in-bld-res, target value for info thread to calculate % and ETA
        self.sleep_time = 20  # watchdog
        self.num_of_lists = 0  # worker lists done counter
        self.result_lbl = 'Template results'  # in-bld-res, custom result print headline
        self.header_msg = 'TEMPLATE'  # # in-bld-res, for debug or custom internal identity


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
        ('batch_7', 'audio_lg', 3),  # queues for batch_7, created but not used so far, can play with
        ('batch_7', 'video_in', 1),
    ]
    mP = eisenmp.Mp()
    mP.queue_cust_dict_category_create(*q_cat_name_maxsize)  # create queues, store in {custom} {category} dict

    generator_aud = audio_generator()
    generator_vid = video_generator()
    audio_q_b1 = mP.queue_cust_dict_cat['batch_1']['audio_lg']  # USE Queue
    video_q_b1 = mP.queue_cust_dict_cat['batch_1']['video_in']  # toolbox.batch_1['video_in'].get()
    mP.start(**modConf.__dict__)  # create processes, load worker mods, start threads (output_p coll, info)
    mP.run_q_feeder(generator=generator_aud, feeder_input_q=audio_q_b1, header_msg='BATCH_1_A')  # custom head
    mP.run_q_feeder(generator=generator_vid, feeder_input_q=video_q_b1, header_msg='BATCH_1_V')


def audio_generator():
    """"""
    for _ in chunks_0:
        yield _


def video_generator():
    """"""
    for _ in chunks_1:
        yield _


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


def main():
    """
    """
    start = time.perf_counter()

    manager_entry()

    print(f'Time in sec: {round((time.perf_counter() - start))}')


if __name__ == '__main__':
    main()
