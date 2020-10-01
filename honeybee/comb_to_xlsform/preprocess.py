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

import re


def remove_whitespace(string):
    return re.sub(r"[ \t\n]+", " ", string).strip()


def remove_indent(match):
    return "{}{}{} {}".format(
        match.group(1),
        match.group(2),
        match.group(3),
        remove_whitespace(match.group(4)))


indent_re = re.compile(
    r"""# Beginning of file or new line:
        #
        (^|\n)

        # Arbitrary amount of indentation, with the first word
        # not being a keyword:
        #
        ([ \t]*(?!if\s|group\s|repeat\s))

        # Question definition or "@" command possibly followed
        # by whitespace:
        #
        (\w+ .*:
         | @.*)
        [ ]*

        # Subsequent lines with deeper indent:
        #
        ((?:\n\2[ \t]+["\w].*){1,})
    """,
    re.VERBOSE)


def preprocess_indent(code):
    return indent_re.sub(remove_indent, code)
