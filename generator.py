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

    def pass_args(self, args: dict):
        self.args = args

    def pass_value(self, value):
        self.value = value

    def pass_condition(self, condition):
        self.condition = condition

    def pass_convert(self, convert):
        self.convert = convert

    def set_unique(self, unique: bool):
        self.unique = unique
        if unique:
            self.set = set()

    def assert_condition(self):
        if hasattr(self, "condition") and self.condition is not None:
            return bool(eval(self.condition, context))
        else:
            return True

    def gen(self) -> Any:
        pass  # return None


def _converted(gen):
    def wrap_func(self: BaseGenerator):
        global gen_cnt, gen_col_cnt, gen_failed_cnt

        max_try = 100
        while max_try:
            r = gen(self)
            gen_cnt += 1
            if not self.unique:
                return type_convert(r, self.convert)
            if r not in self.set:
                self.set.add(r)
                return type_convert(r, self.convert)
            max_try -= 1
            gen_col_cnt += 1
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

    def pass_value(self, value: str):
        start, end = value.split("...")
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
        self._x = Xeger()

    @_converted
    def gen(self):
        return self._x.xeger(self.value)


class ForeignGenerator(BaseGenerator):
    rule_name = "foreign"

    def pass_args(self, args: dict):
        # cast mode
        self.args = args
        self.cast_mode = args.get("cast", None)
        assert self.cast_mode

    def pass_value(self, value: str):
        self.table, self.field = value.split(".")

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
                index_list = map(lambda item: item[0], filtered_list)
                s = set(index_list)
                indexes &= s
            choices = list(
                map(
                    lambda item: item[1],
                    filter(lambda item: item[0] in indexes, enumerate(self.data_list)),
                )
            )
            if not choices:
                return None
            else:
                return choice(choices)
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

    def pass_value(self, value: str):
        self.value = int(value)

    @_converted
    def gen(self) -> Any:
        if hasattr(self, "cnt"):
            self.cnt = self.value
        else:
            self.cnt += 1
        return self.cnt


class DecreaseGenerator(BaseGenerator):
    rule_name = "decrease"

    def pass_value(self, value: str):
        self.value = int(value)

    @_converted
    def gen(self) -> Any:
        if hasattr(self, "cnt"):
            self.cnt = self.value
        else:
            self.cnt -= 1
        return self.cnt


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
