import os
from Flask_SQLAlchemy_Project_Template import create_app, setup_database, db_path


def worker(toolbox):  # name this arg as you like
    """
    - Worker -  eisenmp_exa_wrk_flask_orm_srv_one_cpu

    toolbox is the all-in-one box for vars and queues. incl. ModuleConfiguration
    """
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

    port, col = 0, None
    if not toolbox.WORKER_ID % 2:   # mod is 1 odd
        col = color_dict['BLUE']
        port = blue_q_get(toolbox)[1]  # [0] is header row
    if toolbox.WORKER_ID % 2:
        col = color_dict['YELLOW']
        port = yellow_q_get(toolbox)[1]

    col_end = color_dict['END']

    msg = col + f'\nWORKER_MSG worker: {toolbox.WORKER_ID} pid: {toolbox.WORKER_PID} server port: {port}' + col_end
    toolbox.mp_print_q.put(msg)

    # Flask - app_factory, start Flask via function call
    app_factory = create_app(port)  # flask, we feed port number to update the route -> Html page with our address
    if not os.path.isfile(db_path):  # do not kill db, if exists; MUST exist if many srv, else create by many srv, crash
        setup_database(app_factory)
    app_factory.run(host="localhost", port=port)


def blue_q_get(toolbox):
    """Receive port numbers from queue.
    Same as list.pop()
    """
    while 1:
        if not toolbox.mp_blue_q.empty():
            port_lst = toolbox.mp_blue_q.get()  # has header with serial number
            return port_lst


def yellow_q_get(toolbox):
    """Receive port numbers from queue."""
    while 1:
        if not toolbox.mp_yellow_q.empty():
            port_lst = toolbox.mp_yellow_q.get()  # has header with serial number
            return port_lst
