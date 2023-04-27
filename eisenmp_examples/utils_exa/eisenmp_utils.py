import os
import ssl
import time
import random
import urllib
import sqlite3
import certifi
import threading
from hashlib import sha256
from zipfile import ZipFile
from urllib.request import urlopen, Request
from collections import defaultdict


os.environ['SSL_CERT_FILE'] = certifi.where()
context_ssl = ssl.create_default_context(cafile=certifi.where())
dir_name = os.path.dirname(__file__)  # absolute dir path

agent_list = [   # agent orange or agent white
    'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) '
    'Version/8.0 Mobile/12H321 Safari/600.1.4',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/45.0.2454.85 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/45.0.2454.85 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
]


class Result:
    """Finest results only here.
    Can save number stuff, not response chunks, or we crash

    """

    def __init__(self):
        self._result_dict = defaultdict(list)  # threads can read/write dict

    @property
    def result_dict(self):
        return self._result_dict

    @result_dict.setter
    def result_dict(self, update):
        self._result_dict = update

    @result_dict.deleter
    def result_dict(self):
        del self._result_dict

    def result_dict_update(self, key, value):
        self._result_dict[key].append(value)


def consecutive_number():
    """Want a stamp on each list header.
    Used for Queue messages get() and put in box_dict[num] = msg
    Can rebuild original order if worker puts result in a list
    with same num as order list.
    """
    idx = 0
    while 1:
        yield idx
        idx += 1


def load_url(url, user_agent=None):
    """Get server response.

    :params: url: url
    :params: user_agent: override python ua of urllib (we are a browser)
    :exception: Timeout recursive call
    :return: http server response
    :rtype: http response
    """
    if not user_agent:
        user_agent = agent_list[random.randint(0, len(agent_list) - 1)]
    try:
        request = Request(url)
        opener = urllib.request.build_opener()
        if user_agent:
            opener.addheaders = [('User-agent', user_agent)]
        urllib.request.install_opener(opener)
        response = urlopen(request, timeout=15, context=context_ssl)
        return response

    except TimeoutError:
        print('TimeoutError in load_url().')
        return False
    except Exception as error:
        print(f'unknown error in load_url() {error}')
        return False


def thread_shutdown_wait(*threads):
    """We return if none of the thread names are listed anymore.
    Blocks!

    :params: *threads: arbitrary list of thread names
    """
    busy = True
    while busy:
        names_list = [thread.name for thread in threading.enumerate()]
        busy = True if any([True for thread in threads if thread in names_list]) else False
        time.sleep(.1)


def condense_list_from_fs(search_str, words_dict):
    """
    """
    short_list = [word for word in words_dict.keys() if str_with_len_get(word, search_str)]
    return short_list


def str_with_len_get(word, str_to_comp):
    if len(word) == len(str_to_comp):

        return word
    return False


def split_list(lst, chunk_size):
    """Needs a companion loop.
    for chunk in split_list(word_list, chunk_size): print(chunk)

    :params: lst: the list to split
    :params: chunk_size: row count of lst for one consumer
    """
    for i in range(0, len(lst), int(chunk_size)):
        yield lst[i: i + int(chunk_size)]


def merge_list(*list_paths, lowercase=True):
    """WORD LISTS.
    We create a dict with word as key or hash digest, for speed.

    :params: args: tuple of OS paths word list(s)
    :params: lower: True is all lowercase
    """
    word_list = []
    for arg in list(*list_paths):
        print(f' .. read wordlist {arg}')
        with open(arg, 'r', encoding="UTF-8") as reader:
            if lowercase:
                stripped = [line.lower().rstrip() for line in reader.readlines()]  # remove \n
                pass
            else:
                stripped = [line.rstrip() for line in reader.readlines()]
            word_list.extend(stripped)
    return word_list


def unzip(file_path):
    """Extractor.

    :params: file_path: to zipped file
    """
    with ZipFile(file_path, 'r') as un_zip:
        un_zip.extractall(os.path.dirname(file_path))


def create_hash(word):
    """Inputs a string and returns the sha256 digest

    :params: word: to hash
    """
    w_bytes = word.encode('utf-8')
    w_hash = sha256(w_bytes)
    digest = w_hash.hexdigest()
    return digest


def replace_special_char(word):
    """German so far.

    :params: word: string to check
    """
    if 'ã¤' in word:
        word = word.replace('ã¤', 'ae')
    elif 'ã¼' in word:
        word = word.replace('ã¼', 'ue')
    elif 'ä¶' in word:
        word = word.replace('ä¶', 'oe')
    elif 'ã¶' in word:
        word = word.replace('ã¶', 'oe')
    elif 'ãÿ' in word:
        word = word.replace('ãÿ', 'ss')
    elif 'Ã„' in word:
        word = word.replace('Ã„', 'AE')
    elif 'Ãœ' in word:
        word = word.replace('Ãœ', 'UE')
    elif 'Ã–' in word:
        word = word.replace('Ã–', 'OE')
    elif 'ä' in word:
        word = word.replace('ä', 'ae')
    elif 'Ä' in word:
        word = word.replace('Ä', 'AE')
    elif 'ü' in word:
        word = word.replace('ü', 'ue')
    elif 'Ü' in word:
        word = word.replace('Ü', 'UE')
    elif 'ö' in word:
        word = word.replace('ö', 'oe')
    elif 'Ö' in word:
        word = word.replace('Ö', 'OE')
    elif "'" in word:
        word = word.replace("'", '')
    else:
        pass
    return word


def get_db_path(db_name='db_exa.db'):
    return os.path.join(dir_name, db_name)


def get_db_connection():

    db = get_db_path()
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    return conn


def table_insert(sql_statement, *args):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql_statement, [*args])
    conn.commit()
    conn.close()


def table_select_column(table, col):
    conn = get_db_connection()
    column = conn.execute('SELECT ' + col + ' FROM ' + table + ';')
    rows = []
    for row in column:
        if row[col]:
            rows.append(row[col])

    conn.close()
    return rows


def empty_db_from_schema(db_name='db_exa.db', schema_file='db_exa_schema.sql'):
    """Initial for bruteforce, instances return not sequential,
    Caller exit is possible if last instance writes code word, to identify
    database.db in root is from SQLAlchemy template package
    """
    conn = sqlite3.connect((str(os.path.join(dir_name, db_name))))

    with open((os.path.join(dir_name, schema_file)), encoding='utf-8') as f:
        conn.executescript(f.read())

    cur = conn.cursor()
    cur.execute("INSERT INTO exa (title,col_1,col_2,col_3,col_4,col_5,col_6) VALUES (?,?,?,?,?,?,?)",
                ('init_tbl', 1, 2, 3, 4, 5, 6))
    conn.commit()
    conn.close()
