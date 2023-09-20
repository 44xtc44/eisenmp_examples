"""Worker of ghettorecorder. See the documentation images to get a clue.

"""
import time
import threading
import multiprocessing as mp
from ghettorecorder import GhettoRecorder

proc_exit = False


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


def worker_entrance(toolbox):
    """
    --- WORKER ----

    Called in a loop by the loader module to offer new chunks of iterables.
    But this time we stay fixed and loop only over the queues to start instances
    and forward commands of the parent process.

    Create a dict to store the ghetto instances to loop over their exposed attributes, interfaces.
    Create a thread loop to check com_in q and transfer commands to the ghetto instance.
    """
    toolbox.ghetto_inst_dct = {}
    com_in_thread_start(toolbox)
    com_out_thread_start(toolbox)
    message_thread_start(toolbox)

    while 1:
        if proc_exit:  # ('shutdown_process', '1', 'force');  'all' or num, force: no radio shutdown with delay
            break
        time.sleep(1)


def com_in_thread_start(toolbox):
    """Interface *com_in* of radio recorder is connected to a command q.
    """
    threading.Thread(name='com_in_thread_' + str(toolbox.START_SEQUENCE_NUM),
                     target=com_in_get_loop,
                     args=(toolbox,),
                     daemon=True).start()


def com_out_thread_start(toolbox):
    """com_out interface of radio recorder is connected to a collector q."""
    threading.Thread(name='com_out_thread_' + str(toolbox.START_SEQUENCE_NUM),
                     target=com_out_info_get_loop,
                     args=(toolbox,),
                     daemon=True).start()


def message_thread_start(toolbox):
    """Print active recorder names in a multiprocessing, blocking q to get formatted messages."""
    threading.Thread(name='message_thread_' + str(toolbox.START_SEQUENCE_NUM),
                     target=message_loop,
                     args=(toolbox,),
                     daemon=True).start()


def com_in_get_loop(toolbox):
    """All command tuples for ghetto instances come via com_in proc num."""
    while 1:
        if proc_exit:
            return
        com_in_instance_exec(toolbox)
        time.sleep(.2)


def com_out_info_get_loop(toolbox):
    """tuples with *info_dump_dct* attribute dict from all radios.

    com_out will also hold some tuples with return messages of com_in exec orders.
    Com_out needs a higher maxsize value by default?
    A list counts one, regardless of size. All processes throw their lists into their own q.
    """
    timeout_com_out = 5
    start = time.perf_counter()
    com_out_all = toolbox.child_qs['com_out']
    ghetto_dct = toolbox.ghetto_inst_dct

    while 1:
        if proc_exit:
            return
        end = time.perf_counter()
        if (end - start) > timeout_com_out:
            start = time.perf_counter()

            for radio in ghetto_dct.keys():
                if not com_out_all.full():
                    com_out_all.put((radio, ghetto_dct[radio].info_dump_dct))
                else:
                    print(f"Q full {com_out_all}")


def message_loop(toolbox):
    """Print blocking, formatted in a default eisenmp multiprocess q."""
    print_q = toolbox.mp_print_q
    timeout_message = 15
    start = time.perf_counter()
    while 1:
        if proc_exit:
            return
        dct_cp = toolbox.ghetto_inst_dct.copy()
        lst = [radio for radio in dct_cp.keys()]
        msg = color.CYAN + f'{toolbox.WORKER_NAME} pid {toolbox.WORKER_PID} {lst}' + color.END

        end = time.perf_counter()
        if (end - start) > timeout_message:
            start = time.perf_counter()
            print_q.put(msg)


def com_in_instance_exec(toolbox):
    """Create instance or put cmd tuple in proc internal instance queue to run cmd on instance::

        ('create', 'nachtflug', 'http://85.195.88.149:11810', 'home/osboxes/abracadabra', True)
        ('nachtflug', 'exec', 'setattr(self,"runs_listen",True)')
    """
    global proc_exit
    com_in_all = toolbox.child_qs['com_in_' + str(toolbox.START_SEQUENCE_NUM)]
    if not com_in_all.empty():
        tup = com_in_all.get()
        if not isinstance(tup, tuple):
            return

        if tup[0].startswith('create'):
            radio_create(toolbox, tup)  # create
        elif tup[0].startswith('shutdown_process'):
            proc_exit = True
            time.sleep(3)
        else:
            cmd_args_idx = 2
            radio: str = tup[0]   # command exec
            toolbox.ghetto_inst_dct[radio].com_in.put(tup)

            # check instance removal
            if 'shutdown' in tup[cmd_args_idx] and 'True' in tup[cmd_args_idx]:
                del toolbox.ghetto_inst_dct[radio]


def radio_create(toolbox, tup):
    """Create a Ghetto Recorder instance and start recording.
    *runs_listen* attribute is set by caller to enable audio_out, fill audio_out q.
    """
    radio, url, base_dir = tup[1], tup[2], tup[3]
    dct = toolbox.ghetto_inst_dct

    dct[radio] = GhettoRecorder(radio, url)
    dct[radio].radio_base_dir = base_dir
    dct[radio].runs_meta = True
    dct[radio].runs_record = True
    dct[radio].runs_listen = False
    dct[radio].info_dump_dct = {}
    dct[radio].com_in = mp.Queue(maxsize=1)  # THIS worker process internal q to push commands
    dct[radio].com_out = toolbox.child_qs['com_out']
    dct[radio].audio_out = toolbox.child_qs['audio_out']  # radios must share one q
    dct[radio].start()
