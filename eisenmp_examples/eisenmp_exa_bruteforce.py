"""Generator module, Worker in /worker folder

Mandatory:
- import eisenmp
- worker must have the 'toolbox' as arg in entry function (arg count 1)
- path to worker module and the entry function reference, all are str

"""
import os
import io
import time
from zipfile import ZipFile

import eisenmp
from eisenmp_examples.utils.eisenmp_search import SearchStr
from eisenmp_examples.utils.eisenmp_download import DownLoad

dir_name = os.path.dirname(__file__)  # absolute dir path


class ModuleConfiguration:
    """
    - Loading the worker module has nothing to do with name resolution in 'this' module.
    We can load from network share.

    We have full access to all queues and methods, GhettoBoss has. eisenmp = eisenmp.GhettoBoss()

    """
    # path to worker module and entry function reference, worker module import in [isolated] process environment
    # -------------------- MANDATORY WORKER STRINGS (large worker live in /worker) --------------------
    bruteforce_module = {
        'worker_path': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_bf_bruteforce.py'),
        'worker_ref': 'worker_entrance',
    }
    list_reducer_module = {
        'worker_path': os.path.join(dir_name, 'worker', 'eisenmp_exa_wrk_bf_reduce.py'),
        'worker_ref': 'worker_entrance',
    }
    lang_dicts_paths = [
        r'.\lang_dictionaries\ger\german.dic',
        r'.\lang_dictionaries\eng\words.txt'
    ]

    lang_dicts_url_zip_dct = {

        'https://github.com/44xtc44/eisenmp_examples/raw/dev/eisenmp_examples/lang_dictionaries/ger/german.zip':
            'german.dic',
        'https://github.com/44xtc44/eisenmp_examples/raw/dev/eisenmp_examples/lang_dictionaries/eng/SCOWL-wl.zip':
            'words.txt',
    }

    def __init__(self):
        # load order list, first module is called in an endless loop, you can append your own loop inside the worker
        self.worker_modules = []  # init for kwargs/toolbox, 'worker_module_set'

        self.num_cores = None  # number of process we want, default is None; one proc/CPU core
        self.num_rows = 500  # workload for each proc per cycle, can make the difference
        self.store_result = True  # False: no result in lists or dicts as end result

        # Worker part
        self.multi_tool_get = None  # True: blocks Worker as long as no tool is in the mp_tools_q
        self.multi_tool = None  # informational: toolbox.multi_tool can host the dict from mp_tools_q
        self.info_td_max = None  # target value for info thread to calculate % and ETA if 'enable_info' set

        # custom
        self.use_file_system = False  # False: download and unzip in mem        ------------ SWITCH --------------------
        self.result_lbl = None  # set by caller
        self.num_lists = 0  # add one for each list done, print out worker
        self.lowercase = True
        self.url = None  # 'use_file_system' False, URL of csv file
        self.zipped_filename = None  # None: we have to loop over two; name of the uncompressed file in zip archive
        self.str_permutation = None  # the search string we want to find in the dictionary/wordlist


modConf = ModuleConfiguration()  # accessible in module
searchStr = SearchStr()


def load_lang_word_dict():
    """Load dictionaries from disk or gitHub"""
    word_dicts_file_system_load() if modConf.use_file_system else word_dicts_git_hub_load()


def mp_start_raid():
    """
    - Manager -

    Decide raid tactics.
    Brute force on smaller strings. List reduce attempt for larger strings.

    Grab config values and push it to the two possible functions.

    - (A) len(String) <=  10, combined brute force dictionary attack.
    - (B) len(String) >=  11, Reduce a dictionary len(str) condensed list and count characters.
    """
    pass
    modConf.str_permutation = searchStr.search_string
    if modConf.lowercase:
        modConf.str_permutation = modConf.str_permutation.lower()
    searchStr.create_key_word_val_none_shrink(lowercase=modConf.lowercase)  # dict, remove words != len(search str)
    modConf.info_td_max = len(searchStr.words_dict)  # info thread calc rows done and len

    # ---------- selection of generator function reference ----------
    brute_force = True if len(modConf.str_permutation) <= 10 else False
    function_ref = mp_brute_force if brute_force else mp_reduce
    worker_module_set(function_ref)

    msg_b, msg_r = f'\n\t[BRUTE_FORCE]\t{modConf.str_permutation}', f'\n\t[LIST_REDUCTION]\t{modConf.str_permutation}'
    msg = msg_b if function_ref == mp_brute_force else msg_r
    print(msg)

    generator = function_ref(searchStr)
    words_dict = searchStr.words_dict if function_ref == mp_brute_force else None

    mP = eisenmp.Mp()
    mP.start(**modConf.__dict__)
    if brute_force:
        for _ in mP.proc_list:
            mP.mp_tools_q.put(words_dict)
    mP.run_q_feeder(generator=generator)


def worker_module_set(function_ref):
    """which worker module and function to load"""
    modConf.worker_modules = []  # del existing

    if function_ref == mp_brute_force:
        modConf.multi_tool_get = True
        modConf.worker_modules.append(modConf.bruteforce_module)
    else:
        modConf.multi_tool_get = False
        modConf.worker_modules.append(modConf.list_reducer_module)


def mp_brute_force(search_instance):
    """Generator Part

    - Worker 1

    Produce str permutations for len(str), if len(str) = 3 we have 3! = 6 permutations
    """
    generator = search_instance.generator(lowercase=modConf.lowercase)  # itertools
    return generator


def mp_reduce(search_instance):
    """
    - Worker 2

    We took all language word list and put em in a dict.
    Deleted all words with more or less characters.

    Worker will now reduce the list generated from dict.
    Remove all words not matching characters and
    character count in search str from list.
    Worker puts result in output q.
    """
    generator = (word for word in search_instance.words_dict)  # generator expression; pre reduced in searchString;
    return generator


def word_dicts_file_system_load():
    """
    - Entry ZIP FS

    """
    extract_zip_wordlists()
    searchStr.create_key_word_val_none_dict(modConf.lang_dicts_paths, lowercase=modConf.lowercase)


def extract_zip_wordlists():
    """File system unzip.
    """
    dicts_ger_zip = os.path.join(dir_name, 'lang_dictionaries', 'ger', 'german.zip')
    dicts_eng_zip = os.path.join(dir_name, 'lang_dictionaries', 'eng', 'SCOWL-wl.zip')
    zip_lst = [dicts_ger_zip, dicts_eng_zip]
    for zip_file in zip_lst:
        with ZipFile(zip_file, 'r') as un_zip:
            un_zip.extractall(os.path.dirname(zip_file))


def word_dicts_git_hub_load():
    """
    - Entry ZIP load URL

    """
    downloader = DownLoad()
    mem_word_lst = []

    for url, in_zip in modConf.lang_dicts_url_zip_dct.items():
        modConf.url = url
        modConf.zipped_filename = in_zip
        wordlist_download(downloader)  # stored the response object
        mem_word_lst.extend(wordlists_in_memory(downloader))  # download the zip archive, open one file, return txt file

    if modConf.lowercase:  # store the word list in searchStr instance with lowercase if set {'ethic': None}
        # .rstrip() else single chars, later in shrink method of searchStr
        searchStr.loader_words_dict = {word.lower().rstrip(): None for word in mem_word_lst}
    else:
        searchStr.loader_words_dict = {word.rstrip(): None for word in mem_word_lst}
    pass


def wordlists_in_memory(downloader):
    """Open zip archive and load one file 'zipped_filename'
    Return as text.
    """
    archive = downloader.unzip_mem()
    with io.TextIOWrapper(archive.open(modConf.zipped_filename, 'r')) as file:
        txt_lst = file.readlines()
    return txt_lst


def wordlist_download(downloader):
    """Store response object in downloader instance.
    We could show dots during download, or open in binary, or csv, or ....
    """
    downloader.url = modConf.url
    downloader.zipped_filename = modConf.zipped_filename
    print(downloader.url)
    downloader.load_url()


def main():
    """
    """
    str_list_alphabet_salad = ['EEEFFIKORRS', 'AMGNO', 'DIKKLOOR', 'BEEINNRST',
                               'AACEFHKLMSS', 'CEEHNNRST', 'EEHINORST'
                               'EEEFFIKORRS', 'CFHHILORRS'
                               ]

    start = time.perf_counter()

    load_lang_word_dict()
    for string in str_list_alphabet_salad:
        searchStr.search_string = string
        modConf.result_lbl = string
        modConf.lowercase = True
        mp_start_raid()

        time.sleep(1)

    print(f'BF Time in sec: {round((time.perf_counter() - start))}')


if __name__ == '__main__':
    main()
