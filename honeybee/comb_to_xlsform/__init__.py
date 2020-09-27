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
