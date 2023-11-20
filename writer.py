from schema import params


class BaseWriter:
    name: str = "base"

    def __init__(self) -> None:
        self.args: dict = params.get("args", {})

    def setup(self, name: str, headers: list[str]):
        self.target_name = name
        self.headers = headers
        self.headers_len = len(headers)
        filename = self._on_setup()
        self.file = open(filename, "w") if filename else None

    def pass_line(self, line: list) -> None:
        assert self.headers_len == len(line)

        def handle_special(content) -> str:
            if content is None:
                return ""
            if type(content) is str:
                return '"' + content + '"'
            return str(content)

        line = [handle_special(x) for x in line]

        line_str = self._parse_line(line)
        if self.file:
            self.file.write(line_str + "\n")
        else:
            print(line_str)

    def finish(self) -> None:
        if self.file:
            self.file.flush()
            self.file.close()

    def _on_setup(self) -> str | None:
        return ""

    def _parse_line(self, line: list) -> str:
        return ""


class PrintWriter(BaseWriter):
    name = "print"


class CsvWriter(BaseWriter):
    name = "csv"

    def _on_setup(self) -> str | None:
        self.separator = self.args.get("separator", ",")
        self.separator = eval("'" + self.separator + "'")
        return self.target_name + ".csv"

    def _parse_line(self, line: list) -> str:
        return self.separator.join(line)


class SqlWriter(BaseWriter):
    name = "sql"

    def _on_setup(self) -> str | None:
        self.pattern = (
            f"INSERT INTO {self.target_name} ({', '.join(self.headers)}) VALUES "
        )
        return self.target_name + ".sql"

    def _parse_line(self, line: list) -> str:
        return self.pattern + f"({', '.join(line)});"


_name_class_mapping = {
    generator.name: generator for generator in BaseWriter.__subclasses__()
}

# export name list
rules = _name_class_mapping.keys()


# method to access writers
def get_writer(name: str):
    return _name_class_mapping.get(name, BaseWriter)()
