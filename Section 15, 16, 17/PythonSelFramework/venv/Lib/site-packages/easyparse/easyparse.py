#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import sys
    from .terminal_colors import colors
except(ImportError, ModuleNotFoundError) as failed_import:
    print(f"easyparse: {failed_import}")
    raise SystemExit(1)


# Arguments can be read from sys.argv (default) or any other list.
# Support may be added to parse arguments from a dictionary.
class opt_parser(object):
    '''The main argument parser class'''

    # Setup our __init__ method.
    def __init__(self, argument_list=sys.argv, show_colors=True):
        self.filename = sys.argv[0]
        self.argument_list = argument_list
        self.option_list = []
        self.parsed_args = 0
        self.argument_dict = {}

        # Add the colors
        if show_colors:
            self.__add_colors()
        else:
            self.__add_blank_colors()

    # Parse the Arguments
    def parse_args(self):

        # Check for duplicates
        self.__find_dupes()

        # Get a new list by splitting the joined arguments
        refined_list = self.__clean_passed_args()
        refined_list.remove(self.filename)

        # Build the argument dictionary
        # Dictionary structure is as follows:
        # { argument : [present, needs_value, value]}
        for i in refined_list:
            self.argument_dict.update({i: [self.is_present(i), self.__needs_value(i), self.value_of(i)]})

        # Check for invalid arguments
        self.__check_invalid()

    # Add a custom argument.
    def add_arg(self, short_form, long_form=None, meta_var=None, description=None, optional=False):
        argument_to_append = [
            short_form,
            long_form,
            meta_var,
            description,
            optional
        ]
        for sublist in self.option_list:
            match_prev_arg = [
                argument_to_append == sublist[:2],
                argument_to_append[0] == sublist[0],
                argument_to_append[1] == sublist[1]
            ]
            if max(match_prev_arg):
                return False

        # Check if short hand arg is in correct format
        if not self.__check_format(argument_to_append[0]):
            self.__show_error(f"Argument error: '{argument_to_append[0]}' is in invalid format.", "Easyparse")
            self.__show_error("Short arguments follow this pattern: '-{letter}', e.g. '-s' ", "Easyparse")
            self.__quit_program(1)

        # Check if long form args is in correct format
        if argument_to_append[1] is not None:
            if not self.__check_format(argument_to_append[1], short_form=False):
                self.__show_error(f"Argument error: '{argument_to_append[1]}' is in invalid format.", "Easyparse")
                self.__show_error("Long arguments follow this pattern: '--{full-word}', e.g. '--full-name' ",
                                  "Easyparse")
                self.__quit_program(1)

        self.option_list.append(argument_to_append)
        return True

    # Show an error if there are any argument conflicts.
    def __show_error(self, error_msg, name_to_prepend=None):
        if name_to_prepend is None:
            name_to_prepend = self.filename
        self.yellow.print_status(
            "!",
            f"{name_to_prepend}: {error_msg}"
            )

    # Check if argument needs a passed value
    def __needs_value(self, arg_with_value):
        search_arg = self.__search_list(arg_with_value)
        if search_arg is not None:
            if self.option_list[search_arg[0]][2] is not None:
                return True
            else:
                return False

    # Split multiple arguments into separate ones for easier processing
    @staticmethod
    def __split_joined_args(arg_to_split):
        if arg_to_split == str():
            return None
        if arg_to_split[0].startswith("-") and arg_to_split[1:].isalpha():
            arg_to_split = [i for i in arg_to_split]
            del arg_to_split[0]
            split_arg_list = []
            for i in arg_to_split:
                split_arg_list.append("-" + i)
            return split_arg_list
        else:
            return None

    # Show an error for duplicated arguments.
    def __find_dupes(self):
        for i in self.argument_list:

            # Basic check for duplicates.
            if self.argument_list.count(i) > 1 and self.__is_arg(i):
                self.duplicate_error = True

            # Check if alternate form is given instead.
            elif self.is_present(i, False) and self.is_present(self.__fetch_alt(i), False):
                self.duplicate_error = True

            # Display an error and exit.
            if hasattr(self, 'duplicate_error'):
                self.__show_error("Duplicate arguments supplied.")
                self.__quit_program(1)
        else:
            return False

    # Check for invalid arguments.
    def __check_invalid(self):

        # This is all the passed values.
        ignore_values = []

        # Populate the ignore_values list.
        for i in self.argument_dict.items():
            if i[1][2] is not None:
                ignore_values.append(i[1][2])

        # Find invalid arguments or missing values.
        for i in self.argument_dict.items():
            if i[0] not in ignore_values and all(_ is None for _ in i[1]):
                self.__show_error(f"Invalid option: {i[0]}")
                self.__quit_program(1)
            elif i[1][1] is True and (i[1][2] is False or i[1][2] is None):
                self.__show_error(f"Option: '{i[0]}' missing value")
                self.__quit_program(1)

    # Clean the argument list. Remove duplicated args, and return the list.
    def __clean_passed_args(self):
        expanded_list = []
        for i in self.argument_list:
            arg_is_joined = self.__split_joined_args(i)
            if arg_is_joined is not None:
                for k in arg_is_joined:
                    expanded_list.append(k)
            else:
                expanded_list.append(i)
        return expanded_list

    # Check if argument is present.
    # Passing include_alternate_form=True makes the function consider
    # whether the alternate form of the argument is present.
    def is_present(self, arg_to_check, include_alternate_form=True):
        list_to_use = self.__clean_passed_args()
        list_to_use.remove(self.filename)
        if arg_to_check in list_to_use and self.__is_arg(arg_to_check):
            return True
        elif include_alternate_form:
            alt_arg = self.__fetch_alt(arg_to_check)
            if alt_arg in list_to_use and self.__is_arg(alt_arg):
                return True
        else:
            return False

    # Check if a series of arguments are present.
    # The sep flag can be set to true.
    # This will return a list rather than a boolean value.
    def check_multiple(self, *args_to_check, sep=False):
        try:
            present_list = []
            for i in args_to_check:
                present_list.append(self.is_present(i))
            if sep:
                return present_list
            else:
                return min(present_list)
        except(TypeError):
            return False

    # Search the option list for a particular value and get the x,y postion.
    def __search_list(self, value):
        for i in enumerate(self.option_list):
            if value in i[1][:2]:
                return (i[0], i[1].index(value))

    # Check the value passed to the argument.
    def value_of(self, arg_option):
        alt_form = self.__fetch_alt(arg_option)
        if self.is_present(arg_option):
            if self.__needs_value(arg_option):
                if arg_option in self.argument_list:
                    get_index = self.argument_list.index(arg_option)
                elif alt_form in self.argument_list:
                    get_index = self.argument_list.index(alt_form)
        if "get_index" in locals():
            try:
                item_after = self.argument_list[get_index + 1]
                if not self.__is_arg(item_after):
                    return item_after
            except(IndexError):
                return None

    # Return the alternate argument
    def __fetch_alt(self, alt_arg):
        get_pos = self.__search_list(alt_arg)
        if get_pos is not None:
            if get_pos[-1] == 1:
                return self.option_list[get_pos[0]][0]
            elif get_pos[-1] == 0:
                return self.option_list[get_pos[0]][1]

    # View all the arguments.
    def view_args(self):
        for i in self.option_list:
            self.green.print_success(i[0] + ":")
            print(self.blue.return_color("\tLong form") + "   : " + str(i[1]))
            print(self.blue.return_color("\tMeta var") + "    : " + str(i[2]))
            print(self.blue.return_color("\tDescription") + " : " + str(i[3]))
            print(self.blue.return_color("\tOptional") + "    : " + str(i[4]))

    # Check if value matches an argument
    def __is_arg(self, argument):
        for i in self.option_list:
            if argument in i[:2]:
                return True
        return False

    # Check if argument complies with a certain format.
    @staticmethod
    def __check_format(arg_value, short_form=True):
        try:
            if short_form:
                str_is_valid = arg_value[1].isprintable() and arg_value[1] != ""
                if arg_value[0] == "-" and str_is_valid and len(arg_value) == 2:
                    return True
            elif not short_form:
                long_str_valid = arg_value[2:].isprintable() and arg_value[2] != ""
                if arg_value[:2] == "--" and long_str_valid:
                    return True
            return False
        except(IndexError, ValueError):
            return False

    # Add optional comments for the help screen.
    def add_comment(self, optional_comment):
        if not hasattr(self, 'comment_list'):
            self.comment_list = []
        if optional_comment not in self.comment_list:
            self.comment_list.append(optional_comment)

    # Add optional examples to help user.
    def add_example(self, usage_example, prepend_name=None):
        if not hasattr(self, 'example_list'):
            self.example_list = []
        if prepend_name is None:
            prepend_name = self.filename
        if usage_example not in self.example_list:
            self.example_list.append(f"     {prepend_name} {usage_example}")

    # Display arguments in a manpage-like format.
    def __print_argline(self, argument_array, append_space=False):

        # Set a few values
        long_str = argument_array[1]
        if long_str is None:
            long_str = str()
        meta_type = argument_array[2]
        if meta_type is None:
            meta_type = str()

        # Print the argument
        print(f"       {self.deep_end.color_code}{argument_array[0]} "
              f"{long_str}{self.end.color_code} {self.underline.color_code}"
              f"{meta_type}{self.end.color_code}"
              )
        print("              " + str(argument_array[3]))
        if append_space:
            print()

    # Display arguments for the help screen.
    def show_help(self, add_space=False):

        # Print the header
        self.green.print_success(f"Usage: {self.red.return_color(self.filename)} [options]\n")

        # If any examples were added, print them.
        if hasattr(self, 'example_list'):
            self.green.print_status("i", "Examples:\n")
            for each_example in self.example_list:
                print(each_example + "\n")

        # Print any standard positional arguments
        if False in [i[4] for i in self.option_list]:
            self.green.print_status("i", "Positional arguments:\n")
            for argument in self.option_list:
                if not argument[4]:
                    self.__print_argline(argument, add_space)
            if not add_space:
                print()

        # Print any optional arguments
        if True in [i[4] for i in self.option_list]:
            self.green.print_status("i", "Optional arguments:\n")
            for argument in self.option_list:
                if argument[4]:
                    self.__print_argline(argument, add_space)
            if not add_space:
                print()

        # If there are comments, print them here.
        if hasattr(self, 'comment_list'):
            self.green.print_status("i", "Comments:\n")
            for comment in self.comment_list:
                print(f"     {comment}")
            print()

    # Add the colors to display statuses
    def __add_colors(self):
        self.pink = colors('\033[95m')
        self.blue = colors('\033[94m')
        self.green = colors('\033[92m')
        self.yellow = colors('\033[93m')
        self.red = colors('\033[91m')
        self.end = colors('\033[0m')
        self.deep_blue = colors('\033[1;34;48m')
        self.deep_yellow = colors('\033[1;33;48m')
        self.deep_red = colors('\033[1;31;48m')
        self.deep_green = colors('\033[1;32;48m')
        self.deep_end = colors('\033[1;39;48m')
        self.marine_blue = colors('\033[0;36;48m')
        self.deep_pink = colors('\033[1;35;48m')
        self.light_blue = colors('\033[1;36;48m')
        self.highlight = colors('\033[1;37;40m')
        self.underline = colors('\u001b[4m')
        self.end_underline = colors('\u001b[0m')
        self.deep_highlight = colors('\u001b[7m')

    # Set all colors to blank if required.
    def __add_blank_colors(self):
        self.pink = colors(str())
        self.blue = colors(str())
        self.green = colors(str())
        self.yellow = colors(str())
        self.red = colors(str())
        self.end = colors(str())
        self.deep_blue = colors(str())
        self.deep_yellow = colors(str())
        self.deep_red = colors(str())
        self.deep_green = colors(str())
        self.deep_end = colors(str())
        self.marine_blue = colors(str())
        self.deep_pink = colors(str())
        self.light_blue = colors(str())
        self.highlight = colors(str())
        self.underline = colors(str())
        self.end_underline = colors(str())
        self.deep_highlight = colors(str())

    # Exit the Program
    @staticmethod
    def __quit_program(exit_code=0):
        sys.exit(exit_code)
