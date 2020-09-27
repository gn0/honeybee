from honeybee.comb_to_xlsform.survey import compile_survey
from honeybee.comb_to_xlsform.xlsx import write_xlsx


def comb_to_xlsx(string, filename):
    write_xlsx(
        compile_survey(string),
        filename)
