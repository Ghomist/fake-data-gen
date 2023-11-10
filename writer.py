from utils import replace_none


class BaseWriter:
    name: str = "base"

    def pass_target_name(self, name: str) -> None:
        pass

    def pass_headers(self, headers: list) -> None:
        self.headers = headers
        self.headers_len = len(headers)

    def pass_args(self, context: dict):
        self.args = context

    def pass_line(self, line: list) -> None:
        assert self.headers_len == len(line)
        pass  # do nothing in the base writer

    def write(self) -> None:
        pass  # do nothing in the base writer


class PrintWriter(BaseWriter):
    name = "print"

    def pass_target_name(self, name: str) -> None:
        pass  # dont need file

    def pass_line(self, line: list) -> None:
        super().pass_line(line)
        print(line)


class CsvWriter(BaseWriter):
    name = "csv"

    def pass_args(self, context: dict):
        super().pass_args(context)
        self.separator = self.args.get("separator", ",")
        self.separator = eval("'" + self.separator + "'")

    def pass_target_name(self, name: str) -> None:
        self.f = open(name + ".csv", "w")

    def pass_line(self, line: list) -> None:
        super().pass_line(line)
        line = [("" if x is None else str(x)) for x in line]
        self.f.write(self.separator.join(line) + "\n")

    def write(self) -> None:
        self.f.flush()
        self.f.close()


_name_class_mapping = {
    generator.name: generator for generator in BaseWriter.__subclasses__()
}

# export name list
rules = _name_class_mapping.keys()


# method to access writers
def get_writer(name: str):
    return _name_class_mapping.get(name, BaseWriter)()
