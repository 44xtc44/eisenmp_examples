import unittest
import multiprocessing as mp

import eisenmp_examples.eisenmp_exa_entry as entry
import eisenmp_examples.utils_exa.eisenmp_utils as utils


class TestEntry(unittest.TestCase):
    """
    """
    def test_http_response(self):
        """"""
        proc = mp.Process(target=entry.run_http)
        proc.start()
        response = utils.load_url('http://localhost:12321')
        str_b = response.read()
        assert b'font-family' in str_b
        proc.kill()
