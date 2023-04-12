import io
import zipfile
from io import BytesIO

import eisenmp.utils_exa.eisenmp_utils as g_utils


class DownLoad:
    """If we have the response, we can read it at once or as a stream.

    """

    def __init__(self):
        self.url = None
        self.zipped_filename = None  # one file in zip container
        self.csv_col = None
        self.response = None
        self.file_bin = None

    def load_url(self):
        """
        """
        self.response = g_utils.load_url(self.url)

    def save(self, file_name):
        """Save response on file system with OS buf size.
        Dotted output in one line.
        """
        with open(file_name, 'wb') as file_writer:
            i = 0
            while 1:
                if not (i % 100):
                    print('.', end="", flush=True)
                chunk = self.response.read(io.DEFAULT_BUFFER_SIZE)
                if not chunk:
                    print('\n')
                    break
                file_writer.write(chunk)
                i += 1

    def unzip_mem(self):
        """Extract zip in memory to avoid unwanted files
        from archive on file system.
        """
        zip_file_mem = BytesIO(self.response.read())
        readable_archive = zipfile.ZipFile(zip_file_mem)
        return readable_archive

    def unzip_fs(self):
        """"""
        pass

    def store_mem(self):
        self.file_bin = bytearray()
        i = 0
        while 1:
            if not (i % 100):
                print('.', end="", flush=True)
            chunk = self.response.read(io.DEFAULT_BUFFER_SIZE)
            if not chunk:
                print('\n')
                break
            self.file_bin += chunk
            i += 1


if __name__ == '__main__':
    pass

