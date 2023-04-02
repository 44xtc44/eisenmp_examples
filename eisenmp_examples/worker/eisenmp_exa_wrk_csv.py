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
            toolbox.next_lst = toolbox.mp_input_q.get()
            break
    if toolbox.stop_msg in toolbox.next_lst:  # eisenmp.iterator_loop() informs stop, no more lists
        return False  # loop worker sends shutdown msg to next worker - generator is empty
    return True


def remove_header(toolbox):
    """Transport ticket with consecutive number.
    Remove if no recreation of order is necessary.
    Can reuse list for result, if rebuild order.

    Use self.header_msg attribute to overwrite default header string
    """
    # toolbox.mp_print_q.put(toolbox.next_lst[0])
    del toolbox.next_lst[0]  # remove header str


def calc_average(toolbox):
    """Calc average from strings.
    Pandas can make float, but we use raw Python csv import.
    Table column has 'nan' and empty cells we can not read.
    """
    busy = True
    if toolbox.stop_msg in toolbox.next_lst:  # inform we want exit
        busy = False
    remove_header(toolbox)

    lst = toolbox.next_lst
    stop_msg = toolbox.stop_msg
    # kick out 'nan' string and binary stop message from list, stop message is appended on GhettoBoss iterator loop end
    tbl_flt = [float(num) for num in lst if str(num) and 'nan' not in str(num) and num != stop_msg]

    average = 0
    if len(tbl_flt):  # calc with float type to get comma values
        average = sum([num for num in tbl_flt]) / len(tbl_flt)
    average = average if average else 0

    result_lst = [toolbox.result_header_proc,  # result list for mp_output_q, collected in mp_output_q_box dictionary
                  average]
    toolbox.mp_output_q.put(result_lst)

    output_msg = f' ... {toolbox.worker_name} ... [ average |{average}| ] of {len(toolbox.next_lst)} rows'
    toolbox.mp_print_q.put(output_msg)

    return busy


def send_eta_data(toolbox):
    """list of [perf_header_eta, perf_current_eta] to ProcInfo, to calc arrival time ETA
    """
    toolbox.perf_current_eta = len(toolbox.next_lst)
    perf_lst = [toolbox.perf_header_eta + toolbox.worker_name,  # binary head
                toolbox.perf_current_eta]
    toolbox.mp_info_q.put(perf_lst)  # ProcInfo calc arrival time and % from mp_info_q, of all proc lists
