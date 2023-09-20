import eisenmp_examples.eisenmp_exa_ghettorecorder as gr


class Helper:
    create_lst = [
        # (create instance, name, url, record dir, distribute over procs (default option))
        ('create', 'nachtflug', 'http://85.195.88.149:11810', 'recorder', True),
        ('create', 'hirschmilch', 'https://hirschmilch.de:7001/prog-house.mp3', 'recorder'),
        ('create', 'zenstyle', 'https://radio4.cdm-radio.com:18004/stream-mp3-Zen', 'recorder'),
        ('create', 'classic_ro', 'http://37.251.146.169:8000/streamHD', 'recorder', True),
        ('create', 'yeahmon', 'http://c3.radioboss.fm:8095/autodj', 'recorder', True),
        ('create', 'aacchill', 'http://radio4.vip-radios.fm:8020/stream128k-AAC-Chill_autodj', 'recorder'),
        ('create', 'playurban', 'http://live.playradio.org:9090/UrbanHD', 'recorder')
    ]
    cmd_lst = [
        ('nachtflug', 'exec', 'setattr(self,"runs_listen", True)')   # enable audio out
    ]

    def __init__(self):
        self.module_conf = None


helper = Helper()


def start_recorder():
    """"""
    input_q = helper.module_conf.user_dict['input_q']
    [input_q.put(radio) for radio in Helper.create_lst]
    [input_q.put(command) for command in Helper.cmd_lst]


def stop_recorder():
    """"""
    input_q = helper.module_conf.user_dict['input_q']
    [input_q.put((radio[1], 'exec', 'setattr(self,"shutdown", True)')) for radio in Helper.create_lst]


def kill_all_processes():
    """shutdown_process"""
    input_q = helper.module_conf.user_dict['input_q']
    # ('shutdown_process', '1', 'force');  'all' or num, force: no radio shutdown with delay
    input_q.put(('shutdown_process', 'all', '---'))


def main():
    """Frontend sends commands as tuple to input q.
    Input q distributes to processes worker, worker distributes to radio instance.
    Frontend connects to audio q.
    """
    module_conf = gr.frontend_entry()
    helper.module_conf = module_conf
    return module_conf


if __name__ == "__main__":
    main()
