import re
import copy
import datetime

from collections import namedtuple

import pyparsing as pp
from pyparsing import (
    Forward, Group, LineEnd, Combine, restOfLine,
    indentedBlock, QuotedString, Optional,
    Word, oneOf, OneOrMore, ZeroOrMore, Literal, Suppress,
    alphas, alphanums, nums)

from honeybee.comb_to_xlsform.common import (
    if_cond_to_relevance, args_to_params, merge_params,
    substitute_macros)
from honeybee.comb_to_xlsform.preprocess import preprocess_indent
from honeybee.comb_to_xlsform.choices import parse_choices, expand_choices


def parse_survey():
    indent_stack = [1]
    stmt = Forward()

    identifier = Word(alphas, alphanums + "_")
    number = Word(nums)
    doublequoted_string = QuotedString('"', escChar="\\")
    singlequoted_string = QuotedString("'", escChar="\\")
    string = doublequoted_string | singlequoted_string
    value = number | string

    op = oneOf("+ - * /")
    comp_op = oneOf("= != >= > <= <")

    comment = Group("#" + restOfLine)

    command = Group("@" + identifier + OneOrMore((identifier | value), stopOn=LineEnd()))

    variable = Group("${" + identifier + "}")
    dot = Literal(".")
    expr = Group((variable | dot) + comp_op + value)
    if_cond = "if" + (expr | value)
    if_body = indentedBlock(pp.ungroup(stmt), indent_stack)
    if_block = Group(if_cond + Suppress(":") + if_body)

    q_name = identifier
    q_type = Group(OneOrMore(identifier))
    q_label = string
    q_param = ((identifier + identifier) | (identifier + value))
    q_params = ZeroOrMore(q_param, stopOn=LineEnd())
    question = Group(q_name + q_type + Suppress(":") + Optional(q_label) + q_params)

    group_params = Group(ZeroOrMore(q_param, stopOn=LineEnd()) + Optional(if_cond))

    group_label = string
    group_def = "group" + Group(identifier + Optional(group_label)) + group_params + Optional(if_cond) + Suppress(":")
    group_body = indentedBlock(pp.ungroup(stmt), indent_stack)
    group_block = Group(group_def + group_body)

    repeat_def = "repeat" + Group(identifier + Optional(group_label)) + group_params + Suppress(":")
    repeat_block = Group(repeat_def + group_body)

    # TODO Add + Suppress(LineEnd())?
    stmt <<= (comment | command | if_block | group_block | repeat_block | question)
    stmts = OneOrMore(stmt)

    return stmts


def compile_question(name, args, params):
    question = {"name": name,
                "type": " ".join(str(word) for word in args[0])}

    if len(args) % 2 == 1:
        question_params = args[1:]
    else:
        if question["type"] == "calculate":
            question["calculation"] = args[1]
        else:
            question["label"] = args[1]

        question_params = args[2:]

    question.update(
        merge_params(
            params, args_to_params(question_params)))

    return question


def expand_survey(tree, params):
    rows = []
    choices = []
    settings = None

    for command, *args in tree:
        if command == "#":
            continue

        if command == "@":
            if args[0] == "form":
                form_id = args[1]
                form_version = args[2]
                form_title = args[3]
                form_args = args[4:]

                form_settings = {"form_title": form_title,
                                 "form_id": form_id}
                form_settings.update(
                    args_to_params(form_args))

                if form_version == "auto":
                    form_settings["version"] = (
                        datetime.datetime.utcnow()
                        .strftime("%y%m%d%H%M"))
                else:
                    form_settings["version"] = form_version

                settings = [form_settings]
            elif args[0] == "choices":
                with open(args[1]) as f:
                    choices_macros = args_to_params(args[2:])

                    choices.extend(
                        expand_choices(
                            parse_choices().parseString(
                                substitute_macros(
                                    f.read(),
                                    choices_macros),
                                parseAll=True).asList(),
                            dict()))
            elif args[0] == "include":
                with open(args[1]) as f:
                    include_params = copy.deepcopy(params)
                    include_macros = args_to_params(args[2:])

                    try:
                        include_tree = parse_survey().parseString(
                                           preprocess_indent(
                                               substitute_macros(
                                                   f.read(),
                                                   include_macros)),
                                           parseAll=True).asList()
                    except pp.ParseException:
                        raise ValueError(
                            f"Error when parsing {args[1]}.")

                    expanded = expand_survey(
                        include_tree, include_params)
                    rows.extend(expanded.survey)
            elif args[0] == "required":
                params["required"] = args[1]
            else:
                raise NameError(f"Unknown command: @{args[0]}.")
        elif command == "if":
            if_params = merge_params(
                params,
                {"relevance": if_cond_to_relevance(args[0])})

            expanded = expand_survey(args[1], if_params)
            rows.extend(expanded.survey)
        elif command in ("group", "repeat"):
            group_name = args[0][0]
            group_def = {
                "type": f"begin {command}",
                "name": group_name
            }

            if len(args[0]) > 1:
                group_def["label"] = args[0][1]

            group_params = merge_params(
                params, args_to_params(args[1]))

            rows.append({**group_def, **group_params})

            for param_name in ("relevance", "appearance"):
                if param_name in group_params:
                    del group_params[param_name]

            expanded = expand_survey(args[2], group_params)
            rows.extend(expanded.survey)

            rows.append(
                {"type": f"end {command}",
                 "name": group_name})
        else:
            rows.append(
                compile_question(
                    command, args, copy.deepcopy(params)))

    return namedtuple("Survey", ("survey", "choices", "settings"))(
        survey=rows,
        choices=choices,
        settings=settings)


def compile_survey(string):
    return expand_survey(
        parse_survey().parseString(
            preprocess_indent(
                string),
            parseAll=True).asList(),
        dict())
