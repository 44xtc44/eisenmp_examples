import os
import threading
from Flask_SQLAlchemy_Project_Template import create_app, setup_database, db_path

color_dict = {
    'PURPLE': '\033[1;35;48m',
    'CYAN': '\033[1;36;48m',
    'BOLD': '\033[1;37;48m',
    'BLUE': '\033[1;34;48m',
    'GREEN': '\033[1;32;48m',
    'YELLOW': '\033[1;33;48m',
    'yellow': '\033[1;31;48m',
    'BLACK': '\033[1;30;48m',
    'UNDERLINE': '\033[4;37;48m',
    'END': '\033[1;37;0m',
}

network = "localhost"


def worker(toolbox):
    """
    - Worker -

    """
    # port group
    proc_start_num = toolbox.kwargs['START_SEQUENCE_NUM']

    port, col = 0, None
    if proc_start_num in toolbox.blue_lst:
        col = color_dict['BLUE']
        port = blue_q_get(toolbox)[1]  # [0] is header row
    if proc_start_num in toolbox.yellow_lst:
        col = color_dict['YELLOW']
        port = yellow_q_get(toolbox)[1]
    if proc_start_num in toolbox.green_lst:
        col = color_dict['GREEN']
        port = green_q_get(toolbox)[1]

    col_end = color_dict['END']

    # Flask
    app_factory = create_app(port)  # flask, we feed port number to update the route -> Html page with our address
    if not os.path.isfile(db_path):  # do not kill db, if exists; MUST exist if many srv, else create by many srv, crash
        setup_database(app_factory)
    # app_factory.run(host="localhost", port=port)
    threading.Thread(
        target=lambda: app_factory.run(host="localhost", port=port)).start()

    msg = col + f'\nWORKER_MSG worker: {toolbox.WORKER_ID} pid: {toolbox.WORKER_PID} server port: {port}\n' \
                f'SERVER: http://{network}:{port}' + col_end
    toolbox.mp_print_q.put(msg)

    # end, return None (Nothing is None), loader leaves worker loop and waits for stop msg in mp_process_q


def blue_q_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_blue_q.empty():
            port_lst = toolbox.mp_blue_q.get()  # has header with serial number
            return port_lst


def yellow_q_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_yellow_q.empty():
            port_lst = toolbox.mp_yellow_q.get()
            return port_lst


def green_q_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_green_q.empty():
            port_lst = toolbox.mp_green_q.get()
            return port_lst
