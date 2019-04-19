class colors:
    '''Colors class:
    reset all colors with colors.reset
    two subclasses fg for foreground and bg for background.
    use as colors.subclass.colorname.
    i.e. colors.fg.red or colors.bg.green
    also, the generic bold, disable, underline, reverse, strikethrough,
    and invisible work with the main class
    i.e. colors.bold
    '''
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg:
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg:
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'
    @staticmethod
    def good_news(self, news):
        '''
        Print a Success
        '''
        print(self.bold + self.fg.green + "[>] " + self.reset + news)
    
    @staticmethod
    def bad_news(self, news):
        '''
        Print a Failure, error
        '''
        print(self.bold + self.fg.red + "[!] " + self.reset + news)
    
    @staticmethod
    def info_news(self, news):
        '''
        Print an information with grey text
        '''
        print(self.bold + self.fg.lightblue + "[~] " + self.reset + self.fg.lightgrey + news + self.reset)
    
    @staticmethod
    def question_news(self, news):
        '''
        Print an information with yellow text
        '''
        print(self.bold + self.fg.blue + "[?] " + self.reset + self.fg.yellow + news + self.reset)
    
    @staticmethod
    def print_result(self, target, data, source):
        '''
        Print Breach results
        '''
        # print(self.fg.lightblue, source, self.fg.lightgrey, "| ", self.fg.pink, target, self.fg.lightgrey, "> ", self.bold, self.fg.red, data, self.reset)
        print("{}{}{:15} | {}{}{:^20} > {}{}{:^40}{}".format(self.fg.lightblue, source, \
            self.fg.lightgrey, self.fg.pink, target, self.fg.lightgrey, self.bold, self.fg.red, data, self.reset))
    
    @staticmethod
    def print_res_header(self, target):
        '''
        Print Breach results
        '''
        print(self.bold + self.fg.green + "[>] " + self.reset + "Showing results for " + target + self.reset)
