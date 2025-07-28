#!/usr/bin/env python3

import os
import time
import errno

class GlobalLock:
    def __init__(self, name, timeout=30):
        self.timeout = timeout
        self.filename = f'/tmp/{name}_lock'
        self.have_key = False  # indicates that the instance has obtained the key

    def __enter__(self):
        first_timeout = False
        start_time = time.time()
        while not self.have_key :
            #print("Waiting for lock")
            try:
                f = os.open(self.filename, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(f)
                self.have_key = True
            except OSError as e:
                if e.errno == errno.EEXIST:  # Failed as the file already exists.
                    time.sleep(0.1)
                else:  # Something unexpected went wrong
                    raise
                    #logger.error( "Problem acquiring the lock" )
                    exit(1)

                if (time.time() - start_time) > self.timeout and not first_timeout:
                    print(f"Could not aquire a lock, please check lock file {self.filename}")
                    print(f"Will timeout in {self.timeout}s")
                    first_timeout = True
                if (time.time() - start_time) > 2*self.timeout:
                    print(f"Timeout: Could not aquire a lock, please check lock file {self.filename}")
                    raise

    def __exit__(self, exc_type, exc_value, traceback):
        os.remove(self.filename)
