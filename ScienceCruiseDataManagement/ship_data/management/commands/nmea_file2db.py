from django.core.management.base import BaseCommand, CommandError
import time


class Command(BaseCommand):
    help = 'Reads the NMEA data and writes it into the database'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        process = ProcessNMEAFile(options['path'])
        process.process()


class ProcessNMEAFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def process(self):
        tail_file = TailFile(self.file_path, self._process_line)
        tail_file.readlines_then_tail()

    def _process_line(self, line):
        if line.startswith("GPZDA"):
            self.process_gpzda()
        elif line.startswith("GPGGA"):
            self.process_gpgga()
        else:
            print("Ignoring line", line)

    @staticmethod
    def process_gpzda(line):
        pass

    @staticmethod
    def process_gpgga(line):
        pass


class TailFile:
    def __init__(self, file_path, callback):
        self.file_path = file_path
        self.SLEEP_INTERVAL = 0.5
        self.callback = callback

    def readlines_then_tail(self):
        """ Yields all the lines of the file and then starts tailing. """

        file = open(self.file_path, "r")

        for line in self._yield_lines(file):
            line = line.rstrip()
            self.callback(line)

    def _yield_lines(self, file):
        while True:
            line = file.readline()
            if line:
                yield line
            else:
                self._tail(file)

    def _tail(self, file):
        while True:
            where = file.tell()
            line = file.readline()
            if not line:
                    time.sleep(self.SLEEP_INTERVAL)
                    file.seek(where)
            else:
                    yield line
