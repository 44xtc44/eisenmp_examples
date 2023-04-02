"""

"""
import time


def worker_entrance(toolbox):
    """
    - WORKER - Called in a loop.
    """
    # we ignore toolbox.next_lst
    audio_chunk_lst = batch_1_audio_get(toolbox)
    video_chunk_lst = batch_1_video_get(toolbox)

    busy = template_worker(toolbox, audio_chunk_lst, video_chunk_lst)  # worker function
    if not busy:
        return False
    return True


def batch_1_video_get(toolbox):
    """"""
    while 1:
        if not toolbox.batch_1['video_in'].empty():
            lst = toolbox.batch_1['video_in'].get()
            toolbox.num_of_lists += 1  # list counter prn screen
            return lst


def batch_1_audio_get(toolbox):
    """"""
    while 1:
        if not toolbox.batch_1['audio_lg'].empty():
            lst = toolbox.batch_1['audio_lg'].get()
            return lst


def remove_header(lst):
    """Transport ticket with consecutive number.
    Remove if no recreation of order is necessary.
    Can reuse list for result, if rebuild order.

    Use self.header_msg attribute to overwrite default header string
    """
    del lst[0]  # remove header str


def send_eta_data(toolbox, lst):
    """list of [perf_header_eta, perf_current_eta] to ProcInfo, to calc arrival time ETA
    """
    toolbox.perf_current_eta = len(lst)
    perf_lst = [toolbox.perf_header_eta + toolbox.worker_name,  # binary head
                toolbox.perf_current_eta]
    toolbox.mp_info_q.put(perf_lst)  # ProcInfo calc arrival time and % from mp_info_q, of all proc lists


def send_result_msg(toolbox, *res_lst):
    """"""
    for msg in res_lst:
        result_lst = [toolbox.result_header_proc,  # result list, stored in 'eisenmp.output_q_box' dictionary
                      msg]  # will crash the system mem, binaries
        toolbox.mp_output_q.put(result_lst)


def template_worker(toolbox, audio_chunk_lst, video_chunk_lst):
    """
    """
    busy = True
    header_msg = audio_chunk_lst[0]

    remove_header(audio_chunk_lst)  # remove list header with serial number if no reassembling
    remove_header(video_chunk_lst)

    for idx, row_aud in enumerate(audio_chunk_lst):
        row_aud = row_aud
        row_vid = video_chunk_lst[idx]
        pass
        if toolbox.stop_msg in str(row_aud) or toolbox.stop_msg in str(row_vid):  # stop is str
            return False
        else:

            msg = f'worker: {toolbox.worker_id} cat: {header_msg} ' \
                  f'audio: {row_aud} vid: {row_vid} list({toolbox.num_of_lists})'
            toolbox.mp_print_q.put(msg)
            # output result
            res_lst = [row_aud, row_aud]
            send_result_msg(toolbox, *res_lst)
            time.sleep(.2)

        send_eta_data(toolbox, audio_chunk_lst)
    return busy
