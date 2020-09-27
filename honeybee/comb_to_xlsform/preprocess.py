import re


def remove_whitespace(string):
    return re.sub(r"[ \t\n]+", " ", string).strip()


def remove_indent(match):
    return "{}{}{}{}: {}".format(
        match.group(1),
        match.group(2),
        match.group(3),
        match.group(4),
        remove_whitespace(match.group(5)))


def preprocess_indent(code):
    return re.sub(
        # First line: a possibly indented set of letters ending
        # with a colon.
        #
        r"(^|\n)([ \t]*(?!if\s|group\s|repeat\s))(\w+)(.*):[ ]*"

        # Subsequent lines: a set of letters with deeper inden-
        # tation, possibly occurring multiple times.
        #
        + r"((?:\n\2[ \t]+[\"\w].*){1,})",

        remove_indent,
        code,
        re.VERBOSE)
