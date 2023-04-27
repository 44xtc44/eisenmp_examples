"""Green CSV generator / Worker in folder /worker

Download a NZ government report and calculate the average of split lists.
See URL. Try your own URL. They have a lot.
"""

import os
import csv
import time

from io import TextIOWrapper
from zipfile import ZipFile

import eisenmp
import eisenmp.utils.eisenmp_utils as e_utils
try:
    from eisenmp.utils_exa.eisenmp_download import DownLoad
except ImportError:
    from eisenmp_examples.utils_exa.eisenmp_download import DownLoad

dir_name = os.path.dirname(__file__)


class ModuleConfiguration:
    """Fill the existing attributes.
    You can use the class to have your variables available in the module.
    You have full access to all queues and methods. mp = eisenmp.Mp()

    """
    # path to worker module and entry function reference, worker module import in
    # [isolated, dead references to data structures, [list, dict, instance], offset addr. unreachable] process env
    # -------------------- MANDATORY WORKER STRINGS (large worker live in /worker) --------------------
    first_module = {
        'worker_path': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_csv.py'),
        'worker_ref': 'worker_entrance',
    }
    watchdog_module = {
        'WORKER_PATH': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_watchdog.py'),
        'WORKER_REF': 'mp_start_show_threads',
    }
    dl_url = 'https://www.stats.govt.nz/assets/Uploads/International-trade/' \
             'International-trade-December-2022-quarter/Download-data/international-trade-december-2022-quarter.zip'

    def __init__(self):
        # load order list, first module is called in an endless loop, you can append your own loop inside the worker
        self.worker_modules = [
            self.first_module,  # second module must be started by a thread, else we hang
            self.watchdog_module,
        ]

        # Multiprocess vars - override default
        self.PROCS_MAX = 5  # your process count, default is None: one proc/CPU core
        # max generator / ROWS_MAX = number of tickets; 10_000 / 42 = 238.095 -> 238 lists with ticket numbers
        self.ROWS_MAX = 50_000  # workload spread, list (generator items) to calc in one loop, default is None: 1_000
        self.RESULTS_STORE = True  # keep in dictionary, will crash the system if store GB network chunks in mem
        self.RESULTS_PRINT = True  # result rows of output are collected in a list, display if processes are stopped
        self.RESULTS_DICT_PRINT = True  # shows content of results dict with ticket numbers, check tickets
        self.RESULT_LABEL = 'revised.csv, Average calculation'  # pretty print as result header for RESULTS_PRINT
        # self.START_METHOD = 'fork'  # 'spawn' is default if unused; also use 'forkserver' or 'fork' on Unix only

        # CSV part
        self.use_file_system = False  # False: download and unzip in mem; True must exist on fs ------------- SWITCH ---
        self.url = self.dl_url  # False 'use_file_system', URL of csv file
        self.zipped_filename = 'revised.csv'  # name of the uncompressed file in zip archive
        self.csv_col_name = 'value'  # CSV table column header
        self.sleep_time = 45  # watchdog module in 'worker_modules' list


modConf = ModuleConfiguration()  # accessible in module


def generator_calc_csv():
    """
    - Manager -

    Generator part of calc CSV. Worker module in /worker folder.

    :params: result_lbl: find result in a list; sum findings, mandatory
    :params: use_file_system: True 'use_file_system'; False: in mem unzip
    :params: url: dl_url, if not 'use_file_system', URL of csv file
    :params: zipped_filename: 'revised.csv',  name of the uncompressed file in zip archive
    :params: csv_col_name: 'value',  # table column header name, mandatory
    :params: 'ROWS_MAX': num list rows to calc in one loop for each process
    :params: 'num_proc': procs to start, can be more or less than system CPU core count
    """
    emp = eisenmp.Mp()
    emp.start(**modConf.__dict__)  # thread & processes start, attributes avail. for worker and feeder loop
    emp.mp_print_q.put('\tDownload large list')
    emp.mp_print_q.put(modConf.dl_url)

    report_file = os.path.join(dir_name, 'download', 'report.zip')
    downloader = download_report_zip_archive(emp, report_file)  # and prn msg
    generator = g_use_fs_csv(report_file) if modConf.use_file_system else g_in_mem_csv(downloader)  # CSV generator
    emp.run_q_feeder(generator=generator)

    return emp


def g_in_mem_csv(downloader):
    """
    """
    archive = downloader.unzip_mem()
    in_file = archive.open(modConf.zipped_filename, 'r')
    dict_reader = csv.DictReader(TextIOWrapper(in_file, 'utf-8'))
    generator = (column[modConf.csv_col_name] for column in dict_reader)
    return generator


def g_use_fs_csv(report_file):
    """
    """
    file_path = os.path.join(os.path.dirname(report_file), modConf.zipped_filename)
    filename = open(file_path, 'r')
    dict_reader = csv.DictReader(filename)
    generator = (column[modConf.csv_col_name] for column in dict_reader)
    return generator


def unzip_on_file_system(downloader, report_f):
    """
    """
    downloader.save(report_f)
    with ZipFile(report_f, 'r') as un_zip:
        un_zip.extractall(os.path.dirname(report_f))


def download_report_zip_archive(emp, report_file):
    """
    """
    emp.mp_print_q.put(origin_msg_create())
    downloader = DownLoad()
    downloader.url = modConf.url
    downloader.zipped_filename = modConf.zipped_filename
    downloader.load_url()  # now decide to read csv from mem or file
    if modConf.use_file_system:
        unzip_on_file_system(downloader, report_file)  # comment no dl
    return downloader


def origin_msg_create():
    """
    """
    str_fs = 'WRITE_FILE_SYSTEM'
    str_dl = 'LOAD_URL_UNZIP_READ_IN_MEM'
    origin = str_fs if modConf.use_file_system else str_dl
    origin_msg = f'\n\t{origin} [{modConf.zipped_filename}] [{modConf.csv_col_name}]' \
                 f'\n\t~~~~~~~~~~~~~~~~\n'
    return origin_msg


def main():
    """
    """
    start = time.perf_counter()

    emp = generator_calc_csv()
    while 1:
        # running threads, wait
        if emp.begin_proc_shutdown:
            break
        time.sleep(1)

    print(f'Time in sec: {round((time.perf_counter() - start))}')

    msg_result = e_utils.Result.result_dict
    return msg_result


if __name__ == '__main__':
    main()
