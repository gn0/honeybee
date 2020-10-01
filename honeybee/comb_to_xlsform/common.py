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
import copy


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


def if_cond_to_relevance(cond):
    if isinstance(cond, str):
        return cond

    if isinstance(cond[0], list):
        left_expr = "".join(str(element) for element in cond[0])
    else:
        left_expr = cond[0]

    return f"{left_expr} {cond[1]} {cond[2]}"


def args_to_params(args):
    params = {key: value for key, value in pairwise(args)}

    if "if" in params:
        params["relevance"] = if_cond_to_relevance(params["if"])
        del params["if"]

    return params


def merge_relevance(cond_1, cond_2):
    return f"({cond_1}) and ({cond_2})"


def merge_params(params_1, params_2):
    params = copy.deepcopy(params_1)
    params.update(params_2)

    if "relevance" in params_1 and "relevance" in params_2:
        params["relevance"] = merge_relevance(
            params_1["relevance"], params_2["relevance"])

    return params


def substitute_macros(string, macros):
    def callback(match):
        macro_name = match.group(1)

        if macro_name not in macros:
            raise NameError(f"Unknown macro: {macro_name}.")

        return macros[macro_name]

    return re.sub(r"\$\{!([^}]+)\}", callback, string)
