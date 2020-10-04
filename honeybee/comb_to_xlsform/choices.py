# This file is part of Honeybee.
#
# Honeybee is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later
# version.
#
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General
# Public License along with Honeybee.  If not, see
# <https://www.gnu.org/licenses/>.

import copy

from pyparsing import (
    Forward, OneOrMore, Group, ungroup, alphas, alphanums, nums,
    Word, QuotedString, restOfLine, LineEnd,
    indentedBlock, ZeroOrMore, Suppress)

from honeybee.comb_to_xlsform.common import (
    new_path_and_filename, args_to_params, merge_params,
    substitute_macros)


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

    stmt <<= (comment | command | list_block | choice)
    stmts = OneOrMore(stmt)

    return stmts


def execute_include(filename, args, params, include_path):
    """Generate entries for the 'choices' worksheet based on an
    @include command."""

    include_path, filename = new_path_and_filename(
        include_path, filename)

    include_macros = args_to_params(args)

    with open(filename) as f:
        return expand_choices(
            parse_choices().parseString(
                substitute_macros(
                    f.read(),
                    include_macros),
                parseAll=True).asList(),
            params,
            include_path)


def compile_choice(value, args, params):
    choice = {"value": value,
              "label": args[0]}

    choice.update(
        merge_params(
            params, args_to_params(args[1:])))

    return choice


def expand_choices(tree, params, include_path):
    rows = []

    for command, *args in tree:
        if command == "#":
            continue

        if command == "@":
            if args[0] == "include":
                rows.extend(
                    execute_include(
                        filename=args[1],
                        args=args[2:],
                        params=copy.deepcopy(params),
                        include_path=include_path))
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
                    args[2], list_params, include_path))
        else:
            rows.append(
                compile_choice(
                    command, args, copy.deepcopy(params)))

    return rows
