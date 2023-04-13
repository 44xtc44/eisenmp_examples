import itertools

import eisenmp_examples.utils_exa.eisenmp_utils as e_utils


class SearchStr:
    """Hosts the dict to compare,
    and a 'search string shaker' generator.

    el cheapo goes brute force, but it shows the basics
    go further with 'create_key_digest_val_word_dict' and load
    later a rainbow table with the 'mp_tools_q' into each process

    """

    def __init__(self):
        super().__init__()
        self.search_string = ''
        self.loader_words_dict = {}  # THE dict
        self.words_dict = {}  # work with this dict
        self.csv_column = []  # free to use list, should have one row
        self.search_a_str_thread_name = 'eisenmp_search_a_str_thread'

    def create_key_word_val_none_shrink(self, lowercase=True):
        """Optimized 'create_key_word_val_none_dict'.
        Half of the time. Shrink dict to match only search str length.

        :params: args: OS paths to word lists
        :params: lower: can convert to lower string
        """
        shrink_list = e_utils.condense_list_from_fs(self.search_string, self.loader_words_dict)

        if lowercase:
            self.words_dict = {word.lower(): None for word in shrink_list}
            return

        self.words_dict = {word: None for word in shrink_list}  # None value

    def create_key_word_val_none_dict(self, *args, lowercase=True):
        """{'aal': None, ...}
        Create a dict from wordlists (procs mem inflates to 10 x word_list_size in mb). Faster reading vs list.
        - Dict. Each process gets a copy of the dict vs Multiprocess shared manager dict, which is utter slow.
        - Merged List. Add as many as you like.

        :params: args: OS paths to word lists
        :params: lower: can convert to lower string
        """
        if lowercase:
            self.loader_words_dict = {word: None for word in e_utils.merge_list(*args, lowercase=lowercase)}
            return self.words_dict

        self.loader_words_dict = {word: None for word in e_utils.merge_list(*args)}  # None value

    def create_key_digest_val_word_dict(self, *args, lower=None):
        """{'83c54220e5f2c521819cb6d80163858dd6def3c5a9ed37281a532284b342104a': 'aal',}
        Creates a ``real`` sha256 hash dict for pwd bruteforce.

        :params: args: OS paths to word lists
        :params: lower: can convert to lower string
        """
        if lower:
            wd = {digest: word.lower() for digest, word in
                  zip(map(e_utils.create_hash, e_utils.merge_list(*args)),
                      e_utils.merge_list(*args))}
            self.loader_words_dict = wd  # key is hash output from list (must be lower()): value is string lower()
            return

        self.loader_words_dict = {digest: word for digest, word in
                                  zip(map(e_utils.create_hash, e_utils.merge_list(*args)),
                                      e_utils.merge_list(*args))}

    def generator(self, lowercase=True):
        """STRING generator with all permutations of init_str.
        Itertools creates duplicates of a string permutation.
        We could redirect output to dict, key val, but 15! is a Terabyte string thingy. Needs custom, paid ;), solution.
        - Permutation list generator. 15! is 1,307,674,368,000; 'AEEFFGILNNOPRTT' not solved yet
        1.3 Trillion x 10 byte (guess for a list); 12,770,257,500 kb is 12,7702575 Terabyte list size
        A 16 core XEON will need approximately 20 days for a 15! string, to generate and test all permutations.
        Looks like linear Ordnung to calculate for other core counts. See 'ProcInfo' how to calc ETA.

        :params: init_str: string to shuffle and shake 'DIKKLOOR' -> results in german KROKODIL
        """
        s_str = self.search_string if not lowercase else self.search_string.lower()

        for permutation in itertools.permutations(s_str):
            yield ''.join(permutation)


if __name__ == '__main__':
    ss = SearchStr()
