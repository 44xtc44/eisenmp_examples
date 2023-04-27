"""Worker of fake production

Output queue list header must be different for audio and video to save results.
``header_aud`` and ``header_vid`` are pre-defined in ``ModuleConfiguration``
"""
import time


def worker_entrance(toolbox):
    """
    - WORKER - Called in a loop.
    """
    print('Name             |id()           |reference      ')
    print(*toolbox.Q_NAME_ID_LST)

    audio_chunk_lst, video_chunk_lst = None, None
    if not toolbox.WORKER_ID % 2:  # mod is 1 odd
        audio_chunk_lst = batch_1_audio_get(toolbox)
        video_chunk_lst = batch_1_video_get(toolbox)  # batch_1_video_get(toolbox) ['head_1', 'foo', 'bar', 'buz']
    if toolbox.WORKER_ID % 2:  # mod is 0 even
        audio_chunk_lst = batch_7_audio_get(toolbox)
        video_chunk_lst = batch_7_video_get(toolbox)
    print(f'....{toolbox.WORKER_ID} {audio_chunk_lst} {video_chunk_lst}')
    busy = template_worker(toolbox, audio_chunk_lst, video_chunk_lst)  # worker function
    if not busy:
        return False
    return True


def batch_1_video_get(toolbox):
    """"""
    while 1:
        if not toolbox.batch_1['video_in'].empty():
            lst = toolbox.batch_1['video_in'].get()
            toolbox.num_of_lists += 1  # list counter prn screen, ModuleConfiguration self.num_of_lists
            return lst


def batch_1_audio_get(toolbox):
    """"""
    while 1:
        if not toolbox.batch_1['audio_lg'].empty():
            lst = toolbox.batch_1['audio_lg'].get()
            return lst


def batch_7_video_get(toolbox):
    """"""
    while 1:
        if not toolbox.batch_7['video_in'].empty():
            lst = toolbox.batch_7['video_in'].get()
            toolbox.num_of_lists += 1  # list counter prn screen
            return lst


def batch_7_audio_get(toolbox):
    """"""
    while 1:
        if not toolbox.batch_7['audio_lg'].empty():
            lst = toolbox.batch_7['audio_lg'].get()
            return lst


def remove_header(lst):
    """Transport ticket with consecutive number.
    Remove if no recreation of order is necessary.
    Can reuse list for result, if rebuild order.
    """
    del lst[0]  # remove header str


def send_eta_data(toolbox, lst):
    """list of [PERF_HEADER_ETA, PERF_CURRENT_ETA] to ProcInfo, to calc arrival time ETA
    pure option, broken in version 0.4
    """
    toolbox.PERF_CURRENT_ETA = len(lst)
    perf_lst = [toolbox.PERF_HEADER_ETA + toolbox.WORKER_NAME,  # binary head
                toolbox.PERF_CURRENT_ETA]
    # disable info q will block all
    toolbox.mp_info_q.put(perf_lst)  # ProcInfo calc arrival time and % from info_q, of all proc lists


def send_output(toolbox, row_aud, row_vid):
    """Put your findings in the output list.
    Find results in the 'eisenmp_utils.Result.result_dict'

    :params: toolbox: -
    :params: res_lst: list, res_lst = [row_aud, row_aud]
    """
    # header for output result list
    header = toolbox.OUTPUT_HEADER + toolbox.header_aud  # q collector can distinguish qs and store result in dict
    result_lst = [header,
                  row_aud]  # your findings here
    toolbox.mp_output_q.put(result_lst)

    header = toolbox.OUTPUT_HEADER + toolbox.header_vid  # q collector can distinguish qs and store result in dict
    result_lst = [header,
                  row_vid]  # your findings here
    toolbox.mp_output_q.put(result_lst)


def template_worker(toolbox, audio_chunk_lst, video_chunk_lst):
    """
    """
    busy = True
    toolbox.header_aud = audio_chunk_lst[0]
    toolbox.header_vid = video_chunk_lst[0]

    remove_header(audio_chunk_lst)  # remove list header with serial number if no reassembling
    remove_header(video_chunk_lst)

    for idx, row_aud in enumerate(audio_chunk_lst):
        row_aud = row_aud
        row_vid = video_chunk_lst[idx]
        pass
        if toolbox.STOP_MSG in str(row_aud) or toolbox.STOP_MSG in str(row_vid):  # stop is str
            return False
        else:
            msg = f'worker: {toolbox.WORKER_ID} cat: {toolbox.header_aud} {toolbox.header_vid}' \
                  f'audio: {row_aud} vid: {row_vid} list({toolbox.num_of_lists})'
            msg_col = None
            if not toolbox.WORKER_ID % 2:
                msg_col = toolbox.BLUE
            if toolbox.WORKER_ID % 2:
                msg_col = toolbox.RED

            msg_show = msg_col + msg + toolbox.END
            toolbox.mp_print_q.put(msg_show)
            # output result
            send_output(toolbox, row_aud, row_vid)
            time.sleep(.2)

        send_eta_data(toolbox, audio_chunk_lst)
    return busy
