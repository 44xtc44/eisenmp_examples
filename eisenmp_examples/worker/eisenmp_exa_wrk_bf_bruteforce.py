"""Example 1 brute force
Example 1 owns also a necessary string list reducer module.
Ghetto Dev 16 core is too slow at 12!.
eisenmp uses a list reducer module.
Generated list rows search in language dict.

Vars and Queues stored in the toolbox instance.
See documentation for a quick overview, please.

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
    if toolbox.multi_tool_get:
        tool_get(toolbox)  # dict mp_tools_q
    workload_get(toolbox)
    busy = brute_force(toolbox)  # worker function
    if not busy:
        return False
    send_eta_data(toolbox)
    return True


def tool_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_tools_q.empty():
            toolbox.multi_tool = toolbox.mp_tools_q.get()
            toolbox.multi_tool_get = False  # can be set in modConf
            break


def workload_get(toolbox):
    """"""
    while 1:
        if not toolbox.mp_input_q.empty():
            toolbox.next_lst = toolbox.mp_input_q.get()
            toolbox.num_lists += 1
            break


def remove_header(toolbox):
    """Transport ticket with consecutive number.
    Remove if no recreation of order is necessary.
    Can reuse list for result, if rebuild order.

    Use self.header_msg attribute to overwrite default header string
    """
    # toolbox.mp_print_q.put(toolbox.next_lst[0])
    del toolbox.next_lst[0]  # remove header str


def send_eta_data(toolbox):
    """list of [perf_header_eta, perf_current_eta] to ProcInfo, to calc arrival time ETA
    """
    toolbox.perf_current_eta = len(toolbox.next_lst)
    perf_lst = [toolbox.perf_header_eta + toolbox.worker_name,  # binary head
                toolbox.perf_current_eta]
    toolbox.mp_info_q.put(perf_lst)  # ProcInfo calc arrival time and % from mp_info_q, of all proc lists


def brute_force(toolbox):
    """List -> dict str compare until stop order in last list, generator empty.

    :params: worker_msg: test for a valid string
    """
    busy = True
    if toolbox.stop_msg in toolbox.next_lst:  # eisenmp.iterator_loop() informs stop, no more lists
        busy = False  # loop worker sends shutdown msg to next worker - generator is empty
    remove_header(toolbox)  # remove if no reassembling

    for str_permutation in toolbox.next_lst:  # 'iiattbz' string permutation in the row
        search_str(str_permutation, toolbox)
    return busy


def search_str(s_str, toolbox):
    """Write to result Q if str matched.

    :params: s_str: current generated string to test
    :params: multi_tool: here the words dict
    """
    if s_str in toolbox.multi_tool:  # match dict
        result_lst = [toolbox.result_header_proc,
                      f'... proc {toolbox.worker_name} ... {s_str}']

        toolbox.mp_output_q.put(result_lst)  # a result_q result list has a mandatory header, like input_q lists

        toolbox.mp_print_q.put(f'... proc {toolbox.worker_name} ... {s_str}')
