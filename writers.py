import csv


class BaseWriter:
    def write(self, data, **kwargs):
        raise NotImplementedError()


class Printer(BaseWriter):
    def write(self, data, **kwargs):
        print(data)


class CsvWriter(BaseWriter):
    def __init__(self, path):
        self.path = path

    def write(self, data, **kwargs):
        mode = kwargs.get("mode", "w")
        with open(self.path, mode, encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerows(data)
