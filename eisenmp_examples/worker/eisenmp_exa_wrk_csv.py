"""Economy Example CSV column calculation.

"""


def worker_entrance(toolbox):
    """
    - WORKER - Called in a loop.

    Start, Entry, Exit of this single process worker.
    We return True to get next list chunk, whatever object is in the rows.
    Fed from mp_input_q to our toolbox. toolbox is our work instance with queues,
    messages, list chunk, and work tools like language dictionary or hash list.

    toolbox.foo, gives also access to all attributes and values
    of the 'modConf.foo' instance, you have created
    """
    # toolbox.mp_print_q.put(toolbox.say_hello)
    busy = workload_get(toolbox)
    calc_average(toolbox)  # start worker function
    if not busy:
        return False
    send_eta_data(toolbox)  # send data list, first row is header, info thread can find it in eisenmp.output_q_box
    return True


def workload_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_input_q.empty():
            toolbox.NEXT_LIST = toolbox.mp_input_q.get()
            break
    if toolbox.STOP_MSG in toolbox.NEXT_LIST:  # eisenmp.iterator_loop() informs stop, no more lists
        return False  # loop worker sends shutdown msg to next worker - generator is empty
    return True


def remove_header(toolbox):
    """Transport ticket with consecutive number.
    Remove if no recreation of order is necessary.
    Can reuse list for result, if rebuild order.

    Use self.header_msg attribute to overwrite default header string
    """
    # toolbox.mp_print_q.put(toolbox.NEXT_LIST[0])
    toolbox.INPUT_HEADER = toolbox.NEXT_LIST[0]
    del toolbox.NEXT_LIST[0]  # remove header str


def calc_average(toolbox):
    """Calc average from strings.
    Pandas can make float, but we use raw Python csv import.
    Table column has 'nan' and empty cells we can not read.
    """
    busy = True
    if toolbox.STOP_MSG in toolbox.NEXT_LIST:  # inform we want exit
        busy = False
    remove_header(toolbox)

    lst = toolbox.NEXT_LIST
    STOP_MSG = toolbox.STOP_MSG
    # kick out 'nan' string and binary stop message from list, stop message is appended on GhettoBoss iterator loop end
    tbl_flt = [float(num) for num in lst if str(num) and 'nan' not in str(num) and num != STOP_MSG]

    average = 0
    if len(tbl_flt):  # calc with float type to get comma values
        average = sum([num for num in tbl_flt]) / len(tbl_flt)
    average = average if average else 0

    send_output(toolbox, average)

    output_msg = f' ... {toolbox.WORKER_NAME} ... [ average |{average}| ] of {len(toolbox.NEXT_LIST)} rows'
    toolbox.mp_print_q.put(output_msg)

    return busy


def send_output(toolbox, average):
    """Put your findings in the output list.
    Find results in the 'eisenmp_utils.Result.result_dict'

    :params: toolbox: -
    :params: average: average of the (chunk of) column
    """
    # header for output result list
    header = toolbox.OUTPUT_HEADER + toolbox.INPUT_HEADER  # q collector can distinguish queues and store result in dict
    result_lst = [header,
                  average]  # your findings here
    toolbox.mp_output_q.put(result_lst)


def send_eta_data(toolbox):
    """list of [PERF_HEADER_ETA, PERF_CURRENT_ETA] to ProcInfo, to calc arrival time ETA
    """
    toolbox.PERF_CURRENT_ETA = len(toolbox.NEXT_LIST)
    perf_lst = [toolbox.PERF_HEADER_ETA + toolbox.WORKER_NAME,  # binary head
                toolbox.PERF_CURRENT_ETA]
    toolbox.mp_info_q.put(perf_lst)  # ProcInfo calc arrival time and % from mp_info_q, of all proc lists
