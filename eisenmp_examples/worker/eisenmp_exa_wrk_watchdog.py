"""Module for investigation of thread activity.
Runs with some examples.

"""
import os
import threading
from time import sleep


class Color:
    PURPLE = '\033[1;35;48m'
    CYAN = '\033[1;36;48m'
    BOLD = '\033[1;37;48m'
    BLUE = '\033[1;34;48m'
    GREEN = '\033[1;32;48m'
    YELLOW = '\033[1;33;48m'
    RED = '\033[1;31;48m'
    BLACK = '\033[1;30;48m'
    UNDERLINE = '\033[4;37;48m'
    END = '\033[1;37;0m'


color = Color()


def mp_start_show_threads(toolbox):
    """"""
    pid = os.getpid()
    threading.Thread(name='Watchdog_' + str(pid),
                     target=mp_show_threads,
                     args=(toolbox,),
                     daemon=True).start()


def mp_show_threads(toolbox):
    """Display running thread names.

    :params: toolbox: queues and vars
    """
    toolbox.mp_print_q.put(f' .. thread display interval {toolbox.sleep_time}s')
    while 1:
        names = [thread.name for thread in threading.enumerate()]
        sorted_ = sorted(names)
        msg = color.CYAN + f'process name: {toolbox.WORKER_NAME} pid {toolbox.WORKER_PID} {sorted_}' + color.END
        toolbox.mp_print_q.put(msg)
        sleep(toolbox.sleep_time)


def show_threads(sleep_time):
    """Display running thread names.

    :params: sleep_time: display interval
    """
    print(f' .. thread display interval {sleep_time}s')
    while 1:
        names = [thread.name for thread in threading.enumerate()]
        sorted_ = sorted(names)
        print(sorted_)
        sleep(sleep_time)
