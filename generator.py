from random import random, randrange, choice
from typing import Any

from xeger import Xeger

from context import context
from utils import type_convert

# record how many times 'gen()' called
gen_cnt = 0
# how many times generate collide
gen_col_cnt = 0
# how many times generate failed (and leave it None)
gen_failed_cnt = 0


class BaseGenerator:
    rule_name: str

    def __init__(self) -> None:
        self.condition = "True"

    def set_props(self, props: dict[str, Any]):
        self.args: dict[str, Any] = props.get("args", {})
        self.unique: bool = props.get("unique", False)
        self.value: str = props.get("value", "")
        self.condition: str = props.get("if", "True")
        self.convert = props.get("type", None)
        self.limit: str | None = props.get("limit", None)

        self._set = set()

    def assert_condition(self):
        return bool(eval(self.condition, context))

    def gen(self) -> Any:
        pass  # return None


def _converted(gen):
    def wrap_func(self: BaseGenerator):
        global gen_cnt, gen_col_cnt, gen_failed_cnt

        max_try = 100
        for _ in range(max_try):
            r = gen(self)
            gen_cnt += 1

            # test unique
            if self.unique:
                if r in self._set:
                    gen_col_cnt += 1
                    continue
                else:
                    self._set.add(r)

            # test limit
            if self.limit:
                if not eval(self.limit, context):
                    gen_col_cnt += 1
                    continue

            return type_convert(r, self.convert)

        gen_failed_cnt += 1
        return None

    return wrap_func


class EvalGenerator(BaseGenerator):
    rule_name = "eval"

    @_converted
    def gen(self):
        return eval(self.value, context)


class RangeGenerator(BaseGenerator):
    rule_name = "range"

    def set_props(self, props: dict[str, Any]):
        super().set_props(props)

        start, end = self.value.split("...")
        assert end and start
        try:
            self.start_i = int(start)
            self.end_i = int(end)
            self.as_float = False
        except ValueError:
            self.start = float(start)
            self.end = float(end)
            self.width = self.end - self.start
            self.as_float = True

    @_converted
    def gen(self):
        if self.as_float:
            return random() * self.width + self.end
        else:
            return randrange(self.start_i, self.end_i + 1)


class RegexGenerator(BaseGenerator):
    rule_name = "regex"

    def __init__(self) -> None:
        super().__init__()
        self._x = Xeger()

    @_converted
    def gen(self):
        return self._x.xeger(self.value)


class ForeignGenerator(BaseGenerator):
    rule_name = "foreign"

    def set_props(self, props: dict[str, Any]):
        super().set_props(props)

        # cast mode
        self.cast_mode = self.args.get("cast", None)
        assert self.cast_mode

        # source field
        self.table, self.field = self.value.split(".")

    @_converted
    def gen(self):
        if not hasattr(self, "data_list"):
            self.data_list: list = [*context["__data_map__"][self.table][self.field]]

        # cast to foreign field
        if self.cast_mode == "one":
            try:
                c = choice(self.data_list)
                self.data_list.remove(c)
                return c
            except:
                return None
        elif self.cast_mode == "random":
            return choice(self.data_list)
        elif self.cast_mode == "filter":
            # get filter list
            filters = self.args["filters"]
            if type(filters) is not list:
                filters = [filters]

            # indexes of filtered lines
            indexes = {i for i in range(len(self.data_list))}

            for f in filters:
                field_name = f["field"]
                condition = f["condition"]
                filtered_list = context["__data_map__"][self.table][field_name]

                # check condition
                filtered_list = list(
                    filter(
                        lambda item: eval(condition, {"field": item[1], **context}),
                        enumerate(filtered_list),
                    )
                )

                # map to index
                index_set = set(map(lambda item: item[0], filtered_list))
                indexes &= index_set

            # generate choices list
            choices = list(
                map(
                    lambda item: item[1],
                    filter(lambda item: item[0] in indexes, enumerate(self.data_list)),
                )
            )
            try:
                return choice(choices)
            except:
                return None
        else:
            return None


class ConstGenerator(BaseGenerator):
    rule_name = "const"

    @_converted
    def gen(self):
        return str(self.value)


class EnumGenerator(BaseGenerator):
    rule_name = "enum"

    @_converted
    def gen(self) -> Any:
        return choice(self.value)


class NoneGenerator(BaseGenerator):
    rule_name = "none"

    @_converted
    def gen(self):
        return None


class IncreaseGenerator(BaseGenerator):
    rule_name = "increase"

    def set_props(self, props: dict[str, Any]):
        super().set_props(props)

        self.n = int(self.value) - 1

    @_converted
    def gen(self) -> Any:
        self.n += 1
        return self.n


class DecreaseGenerator(BaseGenerator):
    rule_name = "decrease"

    def set_props(self, props: dict[str, Any]):
        super().set_props(props)

        self.n = int(self.value) + 1

    @_converted
    def gen(self) -> Any:
        self.n -= 1
        return self.n


_rule_class_mapping = {
    generator.rule_name: generator for generator in BaseGenerator.__subclasses__()
}

# export rule list
rules = list(_rule_class_mapping.keys())

# default generator that generate nothing (None)
default_generator = BaseGenerator()


# method to access generators
def gen(rule):
    return _rule_class_mapping.get(rule, BaseGenerator)()


if __name__ == "__main__":
    print(rules)
