# Python 3 server example
# https://pythonbasics.org/webserver/
# mod by 44xtc44

import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import eisenmp

hostName = "localhost"
serverPort = 12_000

radio_url_lst = [
    # just to show server is up, urls for entertainment, no practical use, see template for sqlAlchemy
    ('aac_chill         ', 'http://radio4.vip-radios.fm:8020/stream128k-AAC-Chill_autodj'),
    ('80ies_nl          ', 'http://94.228.133.5:80'),
    ('anime_jp          ', 'http://streamingv2.shoutcast.com/japanimradio-tokyo'),
    ('blues_uk          ', 'http://149.255.59.3:8232/stream'),
    ('classic_ro        ', 'http://37.251.146.169:8000/streamHD'),
    ('goa_psy           ', 'https://amoris.sknt.ru/goa.mp3'),
    ('hirsch_milch      ', 'https://hirschmilch.de:7001/prog-house.mp3'),
    ('nachtflug         ', 'http://85.195.88.149:11810'),
    ('paloma            ', 'https://pool.radiopaloma.de/RADIOPALOMA.mp3'),
    ('reggae            ', 'http://hd.lagrosseradio.info:8000/lagrosseradio-reggae-192.mp3'),
    ('Radio Time Machine', 'http://98.211.68.9:8765/;?icy=https'),
    ('yeah_mon          ', 'http://c3.radioboss.fm:8095/autodj'),
    ('zen_style         ', 'https://radio4.cdm-radio.com:18004/stream-mp3-Zen')
]


class ModuleConfiguration:
    """
    You can use the class to have your variables available in the module.

    'worker_http()' is executed by all processes on a CPU somewhere.
    Each 'worker_http()' gets (one by one) a list chunk from eisenmp.mp_input_q.

    """
    dir_name = os.path.dirname(__file__)  # our module path without file name
    # path to worker module and entry function reference, worker module import in [isolated] process environment
    # -------------------- MANDATORY WORKER STRINGS --------------------
    first_module = {
        'WORKER_PATH': os.path.join(dir_name, 'eisenmp_exa_http.py'),
        'WORKER_REF': 'worker_http',  # Warning: loader runs all f() with a single argument 'toolbox'; pull args from it
    }
    watchdog_module = {
        'WORKER_PATH': os.path.join(dir_name, 'worker', 'eisenmp_watchdog.py'),
        'WORKER_REF': 'mp_start_show_threads',
    }
    foo = {'WORKER_PATH': 'bar', 'WORKER_REF': 'baz'}

    def __init__(self):
        # load order list, first module is called in an endless loop, you can append your own loop inside the worker
        self.worker_modules = [
            self.first_module,  # second module must be threaded, else we hang
            # self.watchdog_module,  # enable for threaded module start live example
        ]
        # not enough work example, useless worker auto shutdown, the modules return False
        self.num_cores = 16  # [option] number of process we want, default is None: one proc/CPU core
        self.num_rows = 1  # micro workload, every process want to get a piece of generator; default None: 10_000 rows
        self.radio_name = None  # define to get it as key in 'modConf' dictionary and worker use 'toolbox.radio_name'
        self.radio_url = None
        self.sleep_time = 60  # if watchdog enabled, toolbox.sleep_time = 60


modConf = ModuleConfiguration()  # Accessible in the module.


def manager_http_srv():
    """
    - Manager -

    """
    # default call feeds all variables of 'ModuleConfiguration' in kwargs -> toolbox of worker
    mP = eisenmp.Mp()
    mP.start(**modConf.__dict__)  # instance attributes available for worker and feeder loop
    # custom, don't need a generator and q feeder to run a server
    generator = (radio_url for radio_url in radio_url_lst)
    mP.run_q_feeder(generator=generator)


def worker_http(toolbox):  # arg for loader, all ModuleConfiguration instance vars can be pulled from toolbox
    """
    - Worker -

    Blocked, no loop here
    toolbox is the all-in-one box for vars and queues. incl. ModuleConfiguration
    We have num_procs, we have ports to add, we need worker in groups to serve ports
    """
    global serverPort

    worker_id = toolbox.worker_id
    serverPort = serverPort + worker_id
    while 1:
        toolbox.next_lst = toolbox.mp_input_q.get()
        break
    if toolbox.stop_msg in toolbox.next_lst[1]:  # eisenmp.iterator_loop() informs (single list) stop, no more lists
        return False  # eisenmp_worker_loader will re-send the shutdown msg to the next worker - generator is empty

    toolbox.radio_name, toolbox.radio_url = toolbox.next_lst[1]  # list of tuples, [0] iterator list header
    MyServer.toolbox = toolbox
    webServer = HTTPServer((hostName, serverPort), MyServer)

    toolbox.mp_print_q.put(f"Server {worker_id} started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")


class MyServer(BaseHTTPRequestHandler):
    toolbox = None

    def do_GET(self):  # no exception handling, else line is over 120, big enough for a basic, OMG an exception! Yep!
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(bytes("<!doctype html>", "utf-8"))
        self.wfile.write(bytes("<html><head>", "utf-8"))
        self.wfile.write(bytes("", "utf-8"))
        self.wfile.write(bytes("<meta charset='utf-8'>", "utf-8"))
        self.wfile.write(bytes("<meta name='viewport' content='width=device-width, ", "utf-8"))
        self.wfile.write(bytes("initial-scale=1, shrink-to-fit=no'/>", "utf-8"))
        self.wfile.write(bytes("<link rel=stylesheet href=https://fonts.googleapis.com/css?family=Roboto/>", "utf-8"))
        self.wfile.write(bytes("<title>https://pythonbasics.org</title>", "utf-8"))
        self.wfile.write(bytes("</head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<h1 style='text-align:center;color:brown;font-family:Roboto;'> Server </h1> ", "utf-8"))
        self.wfile.write(bytes(f"<p style='text-align:center;color:brown;font-family:Roboto;'>", "utf-8"))
        self.wfile.write(bytes("Visit 44xtc44 on PyPi or SnapCraft.io, EisenRadio ,", "utf-8"))
        self.wfile.write(bytes("<a href=https://pypi.org/project/eisenradio/>link</a>", "utf-8"))
        self.wfile.write(bytes(" for a better Show, ", "utf-8"))
        self.wfile.write(bytes("Blacklist, recording and a 'Gain' slider\t", "utf-8"))
        self.wfile.write(bytes(f"\t{self.toolbox.radio_name}\n", "utf-8"))
        self.wfile.write(bytes(f"\t{self.toolbox.radio_url} <a href={self.toolbox.radio_url}>link</a>\n", "utf-8"))
        self.wfile.write(bytes("<hr>", "utf-8"))
        self.wfile.write(bytes("<div class='radio' style='text-align:center;font-family:Roboto;' >'", "utf-8"))
        self.wfile.write(bytes("<audio controls autoplay preload=metadata id='audioR' ", "utf-8"))
        self.wfile.write(bytes(f"src={self.toolbox.radio_url} ></audio> </div>", "utf-8"))
        self.wfile.write(bytes("<script>", "utf-8"))
        self.wfile.write(bytes("(function() {", "utf-8"))
        self.wfile.write(bytes("const audio = document.getElementById('audioR');audio.volume=0.5;", "utf-8"))
        self.wfile.write(bytes("})();", "utf-8"))
        self.wfile.write(bytes("</script>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        self.wfile.write(bytes("", "utf-8"))

        self.toolbox.mp_print_q.put(f'proc name: {self.toolbox.worker_name} pid: {self.toolbox.worker_pid}')


def main():
    """
    """
    start = time.perf_counter()

    manager_http_srv()

    print('Time in sec: ', round((time.perf_counter() - start)))


if __name__ == '__main__':
    main()
