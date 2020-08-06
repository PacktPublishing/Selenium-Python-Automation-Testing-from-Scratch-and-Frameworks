#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class colors():
    '''
    A class to display colors in 256 color terminals.
    It uses ansi color codes as objects, with methods
    that can print various status messages, or just
    colorise the output in general. You as the user
    are free to add any colors you want, as long as
    you have the ansi code for it.
    '''

    # Setup our __init__ method.
    def __init__(self, color_code):
        self.color_code = color_code

        # The code that returns color to normal.
        self.end_code = "\033[0m"

    # Add a base method for printing statuses
    def print_status(self, symbol, message):
        print(f"{self.color_code}[{symbol}]{self.end_code}", message)

    # Add method to print a success message.
    def print_success(self, message):
        self.print_status("+", message)

    # Add method to print a failed message.
    def print_fail(self, message):
        self.print_status("-", message)

    # Add a method to print a question.
    def print_question(self, message):
        self.print_status("?", message)

    # Add a method to print an unsure message.
    def print_unsure(self, message):
        self.print_status("~", message)

    # Add method to simply print the colorised text.
    def print_color(self, message):
        print(self.color_code + message + self.end_code)

    # Add a method to return a status message.
    def return_status(self, symbol, message):
        return f"{self.color_code}[{symbol}]{self.end_code} {message}"

    # Add a method to return the colorised text.
    def return_color(self, message):
        return f"{self.color_code}{message}{self.end_code}"
