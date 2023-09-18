"""Worker of ghettorecorder. See the documentation images to get a clue.

"""
import time
import threading
import multiprocessing as mp
from ghettorecorder import GhettoRecorder

done = False


def worker_entrance(toolbox):
    """
    - WORKER -
    Called in a loop by the loader module to offer new chunks of iterables.
    But this time we stay fixed and loop only over the queues to start instances
    and forward commands of the parent process.

    Create a dict to store the ghetto instances to loop over their exposed attributes, interfaces.
    Create a thread loop to check com_in q and transfer commands to the ghetto instance.
    """
    toolbox.ghetto_inst_dct = {}
    com_in_thread_start(toolbox)
    com_out_thread_start(toolbox)

    while 1:
        if not done:
            time.sleep(42)


def com_in_thread_start(toolbox):
    threading.Thread(name='com_in_thread_' + str(toolbox.START_SEQUENCE_NUM),
                     target=com_in_get_loop,
                     args=(toolbox,),
                     daemon=True).start()


def com_out_thread_start(toolbox):
    threading.Thread(name='com_out_thread_' + str(toolbox.START_SEQUENCE_NUM),
                     target=com_out_info_get_loop,
                     args=(toolbox,),
                     daemon=True).start()


def com_in_get_loop(toolbox):
    """All command tuples for ghetto instances come via com_in_ proc num."""
    while 1:
        com_in_instance_exec(toolbox)
        time.sleep(.1)


def com_out_info_get_loop(toolbox):
    """Create a list of tuples with *info_dump_dct* attribute dict content of all radios.
    Taken from toolbox.ghetto_inst_dct.

    com_out will also hold some tuples with return messages of com_in exec orders.
    Com_out needs a higher maxsize value by default?
    A list counts one, regardless of size. All processes throw their lists into their own q.
    """
    timeout = 5
    start = time.perf_counter()
    com_out_all = toolbox.child_qs['com_out']
    ghetto_dct = toolbox.ghetto_inst_dct
    while 1:
        end = time.perf_counter()
        if (end - start) > timeout:
            start = time.perf_counter()
            for radio in ghetto_dct.keys():
                print(f'radio name - {radio}')
                try:
                    print(ghetto_dct[radio].info_dump_dct)
                except Exception as e:
                    print(e)

            # info_lst = [(radio, ghetto_dct[radio].info_dump_dct) for radio in ghetto_dct.keys()]
            # com_out_all.put(info_lst) if not com_out_all.full() else print(f"Q full {com_out_all}")
            # print(info_lst)


def com_in_instance_exec(toolbox):
    """Create instance or put cmd tuple in proc internal instance queue to run cmd on instance."""
    com_in_all = toolbox.child_qs['com_in_' + str(toolbox.START_SEQUENCE_NUM)]
    if not com_in_all.empty():
        tup = com_in_all.get()
        if tup[0].startswith('create'):
            radio_create(toolbox, tup)
        else:
            radio: str = tup[0]
            toolbox.ghetto_inst_dct[radio].com_in.put(tup)

    # ('create', 'nachtflug', 'http://85.195.88.149:11810', 'home/osboxes/abracadabra', True)
    # ('nachtflug', 'exec', 'setattr(self,"runs_listen",True)')


def radio_create(toolbox, tup):
    """Create a Ghetto Recorder instance and start recording.
    *runs_listen* attribute is set by caller to enable audio_out, fill audio_out q.
    """
    create_str, radio, url, base_dir = tup[0], tup[1], tup[2], tup[3]
    dct = toolbox.ghetto_inst_dct

    dct[radio] = GhettoRecorder(radio, url)
    dct[radio].radio_base_dir = base_dir
    dct[radio].runs_meta = True
    dct[radio].runs_record = True
    dct[radio].runs_listen = False
    dct[radio].info_dump_dct = {}
    dct[radio].com_in = mp.Queue(maxsize=1)  # internal q to push commands
    dct[radio].com_out = toolbox.child_qs['com_out']
    dct[radio].audio_out = toolbox.child_qs['audio_out']  # radios must share one q
    dct[radio].start()
