from time import time

from generator import BaseGenerator


def init():
    # load schema first
    from sys import argv
    from schema import load_schema

    schema_source = argv[1] if len(argv) > 1 else None
    load_schema(schema_source)

    # need schema to init faker
    from fake import init_faker

    init_faker()


def main():
    from classes import Expandable
    from context import context
    from generator import ForeignGenerator, default_generator, gen
    from schema import params, struct
    from writer import get_writer

    # user params
    amount = params.get("amount", 10)
    writer_type = params["format"]

    data_map = dict()

    # loop all tables
    for table_name, fields in struct.items():
        headers = list(fields.keys())
        header_data_map = {name: [] for name in headers}

        # sort fields by its order (default is 0)
        def _key(field_item):
            _, field = field_item
            if type(field) is list:
                all_orders = map(lambda x: x.get("order", 0), field)
                return max(all_orders)
            else:
                return field.get("order", 0)

        sorted_fields = sorted(fields.items(), key=_key)

        # generate every field
        for field_name, field in sorted_fields:
            # multi-fields
            props_list = field if type(field) is list else [field]
            generators: list[BaseGenerator] = []

            # prepare generators
            for props in props_list:
                gen_type = props.get("rule", "const")
                generator = gen(gen_type)
                generator.pass_args(props.get("args", {}))
                if gen_type == ForeignGenerator.rule_name:
                    context.update({"__data_map__": data_map})

                # TODO: support ref
                # reference to other table
                # ref = props.get("ref", None)
                # if ref:
                #     pass

                # str to be generated
                generator.set_unique(props.get("unique", False))
                generator.pass_value(props.get("value", ""))
                generator.pass_condition(props.get("if", None))
                generator.pass_convert(props.get("type", None))

                # append generator
                generators.append(generator)

            # need a empty generator for default 'None'
            generators.append(default_generator)

            # all data of this field
            gen_data = []

            for i in range(amount):
                # line index and variable
                line = Expandable()
                line.set("index", i)
                for header, data in header_data_map.items():
                    if header == field_name or not data:
                        line.set(header, None)
                    else:
                        line.set(header, data[i])
                context.update({"line": line})

                # iterate generators
                for generator in generators:
                    if generator.assert_condition():
                        gen_value = generator.gen()
                        gen_data.append(gen_value)
                        break

            # save data to map
            header_data_map[field_name] = gen_data

        # write/dump
        writer = get_writer(writer_type)
        writer.pass_target_name(table_name)
        writer.pass_headers(headers)
        writer.pass_args(params.get("args", {}))
        for line in zip(*list(header_data_map.values())):
            writer.pass_line(line)
        writer.write()

        data_map[table_name] = header_data_map


if __name__ == "__main__":
    t = time()
    init()
    main()
    cost = time() - t
    print(f"Generated done in {cost:.3}s")

    from generator import gen_cnt, gen_col_cnt, gen_failed_cnt

    print(
        f"""
        Generate    \t{gen_cnt}
        Collide     \t{gen_col_cnt}
        Failed None \t{gen_failed_cnt}
        """
    )
