import os
class FileHandler:

    COMMENT_CHAR = '#'
    OPTION_CHAR = ':'
    settings_file = "settings.cfg"
    settings_file_name = ""
    skipFileValidations = 0

    def __init__(self):
        self.options = {}

    def parse_config(self, fileName):
        with open(fileName) as f:
            for line in f:
                # First, remove comments:
                if self.COMMENT_CHAR in line:
                    # split on comment char, keep only the part before
                    line, comment = line.split(self.COMMENT_CHAR, 1)
                # Second, find lines with an option=value:
                if self.OPTION_CHAR in line:
                    # split on option char:
                    option, value = line.split(self.OPTION_CHAR, 1)
                    # strip spaces:
                    option = option.strip()
                    value = value.strip()
                    # store in dictionary:
                    self.options[option] = value
        return self.options

    def load_settings(self, fileName):
        with open(fileName) as f:
            for line in f:
                # First, remove comments:
                if self.COMMENT_CHAR in line:
                    # split on comment char, keep only the part before
                    line, comment = line.split(self.COMMENT_CHAR, 1)
                # Second, find lines with an option=value:
                if self.OPTION_CHAR in line:
                    # split on option char:
                    option, value = line.split(self.OPTION_CHAR, 1)
                    # strip spaces:
                    option = option.strip()
                    value = value.strip()
                    print(str(value))
                    if option.lower() == "skip_file_validations":
                        self.set_skip_file_validations(value)

    def set_skip_file_validations(self, value):
        self.skipFileValidations = value

    def get_skip_file_validations(self):
        return self.skipFileValidations
