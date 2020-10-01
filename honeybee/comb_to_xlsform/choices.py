import re
import copy

from collections import namedtuple

from pyparsing import (
    Forward, OneOrMore, Group, ungroup, alphas, alphanums, nums,
    Word, QuotedString, restOfLine, LineEnd, Combine,
    indentedBlock, ZeroOrMore, Suppress)

from honeybee.comb_to_xlsform.common import (
    args_to_params, merge_params, substitute_macros)


def parse_choices():
    indent_stack = [1]
    stmt = Forward()

    identifier = Word(alphas, alphanums + "_")
    number = Word(nums)
    string = QuotedString('"', escChar="\\")
    value = number | string

    comment = Group("#" + restOfLine)

    command = Group("@" + identifier + OneOrMore((identifier | value), stopOn=LineEnd()))

    choice_param = ((identifier + identifier) | (identifier + value))
    choice_params = Group(ZeroOrMore(choice_param, stopOn=LineEnd()))
    choice_value = value
    choice_label = value
    choice = Group(choice_value + choice_label + choice_params)

    list_name = identifier
    list_def = "list" + list_name + choice_params + Suppress(":")
    list_body = indentedBlock(ungroup(stmt), indent_stack)
    list_block = Group(list_def + list_body)

    stmt <<= (comment | list_block | choice)
    stmts = OneOrMore(stmt)

    return stmts


def compile_choice(value, args, params):
    choice = {"value": value,
              "label": args[0]}

    choice.update(
        merge_params(
            params, args_to_params(args[1:])))

    return choice


def expand_choices(tree, params):
    rows = []

    for command, *args in tree:
        if command == "#":
            continue

        if command == "@":
            if args[0] == "include":
                with open(args[1]) as f:
                    include_params = copy.deepcopy(params)
                    include_macros = args_to_params(args[2:])

                    rows.extend(
                        expand_choices(
                            parse_choices().parseString(
                                substitute_macros(
                                    f.read(),
                                    include_macros),
                                parseAll=True).asList(),
                            include_params))
            else:
                raise NameError(f"Unknown command: @{args[0]}.")
        elif command == "list":
            list_params = merge_params(
                params,
                {"list_name": args[0]})

            list_params.update(
                args_to_params(args[1]))

            rows.extend(
                expand_choices(
                    args[2], list_params))
        else:
            rows.append(
                compile_choice(
                    command, args, copy.deepcopy(params)))

    return rows
