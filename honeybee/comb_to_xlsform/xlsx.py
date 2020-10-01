import openpyxl


SURVEY_ORDER = (
    "type", "name", "label", "hint", "appearance", "constraint",
    "constraint_message", "calculation", "required",
    "required_message", "repeat_count")

CHOICES_ORDER = (
    "list_name", "value", "label", "filter")

SETTINGS_ORDER = (
    "form_title", "form_id", "version")


def column_key(order, value):
    try:
        return order.index(value)
    except ValueError:
        return len(order)


def get_column_names(rows):
    return set(name for row in rows
                    for name in row.keys())


def write_sheet(sheet, rows, column_key):
    column_names = sorted(
        get_column_names(rows), key=column_key)

    sheet.append(column_names)

    for row in rows:
        sheet.append(
            tuple(row.get(name) for name in column_names))


def write_xlsx(survey, filename):
    workbook = openpyxl.Workbook()

    survey_sheet = workbook.active
    survey_sheet.title = "survey"

    choices_sheet = workbook.create_sheet(title="choices")
    settings_sheet = workbook.create_sheet(title="settings")

    write_sheet(
        survey_sheet,
        survey.survey,
        lambda x: column_key(SURVEY_ORDER, x))
    write_sheet(
        choices_sheet,
        survey.choices,
        lambda x: column_key(CHOICES_ORDER, x))
    write_sheet(
        settings_sheet,
        survey.settings,
        lambda x: column_key(SETTINGS_ORDER, x))

    workbook.save(filename)
