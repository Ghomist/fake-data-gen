from os import mkdir, path
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
        if not path.exists(r"data/"):
            mkdir(r"data/")
        self.file = open(r"data/" + filename, "w") if filename else None
        if self.file:
            header_line = self._get_header_line()
            if header_line:
                self.file.write(header_line + "\n")

    def pass_line(self, line: list) -> None:
        assert self.headers_len == len(line)

        line = [self._format_value(x) for x in line]

        line_str = self._parse_line(line)
        if self.file:
            self.file.write(line_str + "\n")
        else:
            print(line_str)

    def finish(self) -> None:
        if self.file:
            self.file.flush()
            self.file.close()

    def _format_value(self, content) -> str:
        if content is None:
            return ""
        return str(content)

    def _on_setup(self) -> str | None:
        return None

    def _get_header_line(self) -> str | None:
        return None

    def _parse_line(self, line: list) -> str:
        return ""


class PrintWriter(BaseWriter):
    name = "print"


class CsvWriter(BaseWriter):
    name = "csv"

    def _on_setup(self) -> str | None:
        self.separator = self.args.get("separator", ",")
        self.separator: str = eval("'" + self.separator + "'")
        self.use_headers = self.args.get("headers", False)
        self.quotation = self.args.get("quotation", "none")
        return self.target_name + ".csv"

    def _get_header_line(self) -> str | None:
        return self.separator.join(self.headers) if self.use_headers else None

    def _parse_line(self, line: list) -> str:
        return self.separator.join(line)

    def _format_value(self, content) -> str:
        if type(content) is str:
            if self.quotation == "single":
                return "'" + content + "'"
            elif self.quotation == "double":
                return '"' + content + '"'
            else:
                return content
        return super()._format_value(content)


class SqlWriter(BaseWriter):
    name = "sql"

    def _on_setup(self) -> str | None:
        self.pattern = (
            f"INSERT INTO {self.target_name} ({', '.join(self.headers)}) VALUES "
        )
        return self.target_name + ".sql"

    def _parse_line(self, line: list) -> str:
        return self.pattern + f"({', '.join(line)});"

    def _format_value(self, content) -> str:
        if type(content) is str:
            return '"' + content + '"'
        return super()._format_value(content)


_name_class_mapping = {
    generator.name: generator for generator in BaseWriter.__subclasses__()
}

# export name list
rules = _name_class_mapping.keys()


# method to access writers
def get_writer(name: str):
    return _name_class_mapping.get(name, BaseWriter)()
