import unittest
from unittest import mock
import multiprocessing as mp

import eisenmp_examples.eisenmp_exa_entry as entry
import eisenmp_examples.utils_exa.eisenmp_utils as utils


class TestEntry(unittest.TestCase):
    """
    """

    def _setUp(self):
        """ 49152 to 65535 free
        """
        self.http_port = entry.serverPort
        self.mock_http_port = mock.patch.object(
            entry, 'serverPort', return_value=50_001
        )

    def test_http_response(self):
        """
        """
        com_q = mp.Queue(maxsize=1)
        proc = mp.Process(target=entry.run_http, args=(com_q,))
        proc.start()

        msg = com_q.get()
        if msg == b'ready':
            # with self.mock_http_port:
            response = utils.load_url('http://localhost:12321')
            str_b = response.read()
            assert b'font-family' in str_b
        proc.terminate()
        proc.kill()
        proc.join()

    def _tearDown(self):
        """ org. port set back, for whatever reason
        """
        entry.serverPort = self.http_port
