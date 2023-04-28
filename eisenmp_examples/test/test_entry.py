import time
import unittest
import multiprocessing as mp

import eisenmp_examples.eisenmp_exa_entry as entry
import eisenmp_examples.utils_exa.eisenmp_utils as utils


class TestEntry(unittest.TestCase):
    """
    """
    def test_http_response(self):
        """
        """
        com_q = mp.Queue(maxsize=1)
        proc = mp.Process(target=entry.run_http, args=(com_q,))
        proc.start()

        msg = com_q.get()
        if msg == b'ready':
            time.sleep(.2)
            response = utils.load_url('http://localhost:12321')
            str_b = response.read()
            assert b'font-family' in str_b

        proc.kill()
        proc.join()

