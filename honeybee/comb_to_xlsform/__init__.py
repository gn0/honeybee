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

import argh

from honeybee.comb_to_xlsform.survey import compile_survey
from honeybee.comb_to_xlsform.xlsx import write_xlsx


def comb_to_xlsx(string, filename):
    write_xlsx(
        compile_survey(string),
        filename)


@argh.arg("-o", "--output-filename", type=str, required=True)
def main(input_filename, output_filename=None):
    with open(input_filename) as f:
        comb_to_xlsx(
            f.read(), output_filename)


def dispatch():
    argh.dispatch_command(main)
