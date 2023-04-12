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
        'RED': '\033[1;31;48m',
        'BLACK': '\033[1;30;48m',
        'UNDERLINE': '\033[4;37;48m',
        'END': '\033[1;37;0m',
    }

    # port group
    port, col = 0, None
    if toolbox.worker_id in toolbox.blue_lst:
        col = color_dict['BLUE']
        port = blue_q_get(toolbox)[1]  # [0] is header row
    if toolbox.worker_id in toolbox.red_lst:
        col = color_dict['RED']
        port = red_q_get(toolbox)[1]

    col_end = color_dict['END']
    col = color_dict['CYAN'] if col is None else col

    msg = col + f'\nWORKER_MSG worker: {toolbox.worker_id} pid: {toolbox.worker_pid} server port: {port}' + col_end
    toolbox.mp_print_q.put(msg)

    # Flask
    app_factory = create_app(port)  # flask, we feed port number to update the route -> Html page with our address
    if not os.path.isfile(db_path):  # do not kill db, if exists; MUST exist if many srv, else create by many srv, crash
        setup_database(app_factory)
    app_factory.run(host="localhost", port=port)


def blue_q_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_blue_q.empty():
            port_lst = toolbox.mp_blue_q.get()  # has header with serial number
            return port_lst


def red_q_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_red_q.empty():
            port_lst = toolbox.mp_red_q.get()  # has header with serial number
            return port_lst


