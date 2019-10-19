# -*- coding: utf-8 -*-


class colors:
    """Colors class:
    reset all colors with colors.reset
    two subclasses fg for foreground and bg for background.
    use as colors.subclass.colorname.
    i.e. colors.fg.red or colors.bg.green
    also, the generic bold, disable, underline, reverse, strikethrough,
    and invisible work with the main class
    i.e. colors.bold
    """

    reset = "\033[0m"
    bold = "\033[01m"
    disable = "\033[02m"
    underline = "\033[04m"
    reverse = "\033[07m"
    strikethrough = "\033[09m"
    invisible = "\033[08m"

    class fg:
        black = "\033[30m"
        red = "\033[31m"
        green = "\033[32m"
        orange = "\033[33m"
        blue = "\033[34m"
        purple = "\033[35m"
        cyan = "\033[36m"
        lightgrey = "\033[37m"
        darkgrey = "\033[90m"
        lightred = "\033[91m"
        lightgreen = "\033[92m"
        yellow = "\033[93m"
        lightblue = "\033[94m"
        pink = "\033[95m"
        lightcyan = "\033[96m"

    class bg:
        black = "\033[40m"
        red = "\033[41m"
        green = "\033[42m"
        orange = "\033[43m"
        blue = "\033[44m"
        purple = "\033[45m"
        cyan = "\033[46m"
        lightgrey = "\033[47m"

    @staticmethod
    def good_news(news):
        """
        Print a Success
        """
        print(colors.bold + colors.fg.green + "[>] " + colors.reset + news.strip())

    @staticmethod
    def debug_news(news):
        """
        Print a Debug
        """
        print()
        print(colors.bold + colors.fg.lightred + "[@] " + news + colors.reset)

    @staticmethod
    def bad_news(news):
        """
        Print a Failure, error
        """
        print(colors.bold + colors.fg.red + "[!] " + colors.reset + news.strip())

    @staticmethod
    def info_news(news):
        """
        Print an information with grey text
        """
        print(
            colors.bold
            + colors.fg.lightblue
            + "[~] "
            + colors.reset
            + colors.fg.lightgrey
            + news.strip()
            + colors.reset
        )

    @staticmethod
    def question_news(news):
        """
        Print an information with yellow text
        """
        print(
            colors.bold
            + colors.fg.blue
            + "[?] "
            + colors.reset
            + colors.fg.yellow
            + news.strip()
            + colors.reset
        )

    @staticmethod
    def print_result(target, data, source):
        """
        Print Breach results
        """
        if "PASS" in source:
            print(
                "{}{}{:15}{}|{}{:>25.25}{} > {}{}{}{}".format(
                    colors.fg.lightblue,
                    colors.bold,
                    source,
                    colors.fg.lightgrey,
                    colors.fg.pink,
                    target,
                    colors.fg.lightgrey,
                    colors.bold,
                    colors.fg.green,
                    data,
                    colors.reset,
                )
            )
        elif "LOCALSEARCH" in source:
            if len(data) > 140:
                print(
                    "{}{}{:15}{}|{}{:>25.25}{} > {}{}{}{}".format(
                        colors.fg.lightblue,
                        colors.bold,
                        source,
                        colors.fg.lightgrey,
                        colors.fg.pink,
                        target,
                        colors.fg.lightgrey,
                        colors.bold,
                        colors.fg.green,
                        "[...]" + data[-135:],
                        colors.reset,
                    )
                )
            else:
                print(
                    "{}{}{:15}{}|{}{:>25.25}{} > {}{}{}{}".format(
                        colors.fg.lightblue,
                        colors.bold,
                        source,
                        colors.fg.lightgrey,
                        colors.fg.pink,
                        target,
                        colors.fg.lightgrey,
                        colors.bold,
                        colors.fg.green,
                        data,
                        colors.reset,
                    )
                )

        elif "HASH" in source:
            print(
                "{}{:15}{}|{}{:>25.25}{} > {}{}{}".format(
                    colors.fg.lightblue,
                    source,
                    colors.fg.lightgrey,
                    colors.fg.pink,
                    target,
                    colors.fg.lightgrey,
                    colors.fg.red,
                    data,
                    colors.reset,
                )
            )
        elif "USER" in source:
            print(
                "{}{:15}{}|{}{:>25.25}{} > {}{}{}".format(
                    colors.fg.lightblue,
                    source,
                    colors.fg.lightgrey,
                    colors.fg.pink,
                    target,
                    colors.fg.lightgrey,
                    colors.fg.lightcyan,
                    data,
                    colors.reset,
                )
            )
        elif "SOURCE" in source:
            print(
                "{}{:15}{}|{}{:>25.25}{} > {}{}{}".format(
                    colors.fg.lightblue,
                    source,
                    colors.fg.lightgrey,
                    colors.fg.pink,
                    target,
                    colors.fg.lightgrey,
                    colors.reset,
                    data,
                    colors.reset,
                )
            )
        elif "IP" in source:
            print(
                "{}{:15}{}|{}{:>25.25}{} > {}{}{}".format(
                    colors.fg.lightblue,
                    source,
                    colors.fg.lightgrey,
                    colors.fg.pink,
                    target,
                    colors.fg.lightgrey,
                    colors.fg.red,
                    data,
                    colors.reset,
                )
            )
        else:
            print(
                "{}{:15}{}|{}{:>25.25}{} > {}{}{}".format(
                    colors.fg.lightblue,
                    source,
                    colors.fg.lightgrey,
                    colors.fg.pink,
                    target,
                    colors.fg.lightgrey,
                    colors.fg.lightgrey,
                    data,
                    colors.reset,
                )
            )

    @staticmethod
    def print_res_header(target):
        """
        Print Breach result header
        """
        print(colors.bold, "{:_^90}\n".format(""), colors.reset)
        print(
            colors.bold
            + colors.fg.green
            + "[>] "
            + colors.reset
            + "Showing results for "
            + target
            + colors.reset
        )
