#!/bin/python
import os
import sys
import subprocess
import logging
from enum import Enum

# TODO: clean this up
if("--debug" in sys.argv):
    FORMAT_COLOR = True
    if(FORMAT_COLOR):
        format="%(levelname)s\x1b[33m[%(lineno)s]\x1b[36m%(funcName)s()\x1b[m    %(message)s" #]]]
    else:
        format="%(levelname)s[%(lineno)s]%(funcName)s():\t%(message)s"
    logging.basicConfig(level=logging.DEBUG, format=format)

class Match(Enum):
    fixed = "-F"
    basic_regex = "-G"
    extended_regex = "-E"
    pcre = "-P"

class Options():
    def __init__(self):
        self.COLOR = True
        self.EXTS = []
        self.EXT_EXCLUDE = False
        self.FILENAME = True
        self.IGNORE_CASE = True
        self.LINES_NUM = True
        self.MATCH_TYPE = Match.pcre
        self.NAME_ONLY = False
        self.PRUNES = ["\.git", "node_modules",]
        self.ROOT = os.environ['PWD']
        self.AUTO_VIM = False
        self.VIM_FORMAT = True
        self.PATTERN = ""

def display_help(exit_code: int):
    """ Displays help and exits with exit_code
    if exit_code is non-zero, outputs help to stderr

    :param exit_code: code to exit with
    """
    file = sys.stderr if exit_code else sys.stdout
    print("""\
Usage: coffin [OPTION]... PATTERN
Searches recursively under the current directory for the pattern inside files.
By default, the pattern is interpreted as a PCRE regex

Options:
  -F, --fixed               interprets PATTERN as a fixed string
  --basic                   interprets PATTERN as a BRE
  --extended                interprets PATTERN as an ERE
  -C, --colors              toggles colored output (on by default)
  -r, --root <path>         uses <path> as the root of searches (cwd by default)
  -p, --prune <names>       prunes the directories inside <names> (must be
                            separated by whitespaces)
  -e, --ext <extensions>    only looks for files with these extensions (must
                            be separated by whitespaces)
  -E, --exclude             toggles exclusion based on extensions given to -e
  --debug                   outputs debug infos
  -v, --autovim             toggles automatically calling coffin inside vim
  -V, --vimformat           toggles vim-friendly output formatting
  -d, --dry                 toggles only displaying the name of matching files
  --case                    toggles case sensitivity in pattern matching
  --lines-num               toggles displaying line numbers in the output
  -h, --help                shows this message\
""", file=file)
    exit(exit_code)


def parse_args(args: list, options: Options):
    """ Parses args to modify options

    :param list args: args given to coffin
    :param Options options: options to modify
    """
    logging.debug("args: %s",args)
    nb_args = len(args)-1
    if(nb_args < 1):
        logging.error("not enough arguments")
        display_help(1)
    # Strips script name
    args_iter = iter(args[1:])
    for arg in args_iter:
        # Booleans are toggled to account for user's config file
        match arg:
            case "-F" | "--fixed":
                options.MATCH_TYPE = Match.fixed
            case "--basic":
                options.MATCH_TYPE = Match.basic_regex
            case "--extended":
                options.MATCH_TYPE = Match.extended_regex
            case "-C" | "--colors":
                options.COLOR ^= True
            case "-r" | "--root":
                options.ROOT = args_iter.__next__()
                nb_args -= 1
            case "-p" | "--prune":
                prunes = args_iter.__next__()
                nb_args -= 1
                options.PRUNES += prunes.split(' ')
            case "-e" | "--ext":
                exts = args_iter.__next__()
                nb_args -= 1
                options.EXTS += exts.split(' ')
            case "-E" | "--exclude":
                options.EXT_EXCLUDE ^= True
            case "-v" | "--autovim":
                options.AUTO_VIM ^= True
            case "-V" | "--vimformat":
                options.VIM_FORMAT ^= True
            case "-d" | "--dry":
                options.NAME_ONLY ^= True
            case "--case":
                options.IGNORE_CASE ^= True
            case "--lines-num":
                options.LINES_NUM ^= True
            case "-h" | "--help":
                display_help(0)
            case "--debug":
                # TODO: clean this up
                pass
            case _:
                if(nb_args > 1):
                    logging.error("more than one pattern")
                    logging.error(sys.argv)
                    display_help(1)
                else:
                    options.PATTERN = arg
        nb_args -= 1
    logging.debug("options: %s", options.__dict__)


def extension_regex(root: str, extensions: list):
    """Produces the regex used to filter files by extension

    :param str root: root of the file walking point
    :param list extensions: extension names to filter by
    :return: str regex: posix-extended regex to match extensions to filter by
    """
    # dot added by join(), except for first element
    exts = "|\.".join(extensions)
    return f"^{root}/.*(\.{exts})$"

def prune_regex(root: str, prunes: list):
    """Produces the regex used to prune dirs

    :param str root: root of the file walking point
    :param list prunes: dir names to prune
    :return: str regex: posix-extended regex to match dir names to prune
    """
    names = "|".join(prunes)
    return f"^{root}/.*({names})$"

def get_files(opts: Options):
    """Get the list of files matching the search criteria

    :param opts: options object to alter behavior of search. Uses PRUNES, EXT, ROOT, EXT_EXCLUDE
    :return list[str]: paths to files after filtering
    """

    prune_args = ext_args = []
    # TODO
    root = opts.ROOT
    prunes = opts.PRUNES
    exts = opts.EXTS
    ext_exclude = opts.EXT_EXCLUDE

    if(prunes):
        prune_expr = prune_regex(root, prunes)
        prune_args = ["-type","d","-regex",prune_expr,"-prune","-o"]
        logging.debug("prunes_args: %s", prune_args)
    if(exts):
        ext_expr = extension_regex(root, exts)
        ext_args = ["-regex",ext_expr]
        ext_exclude and ext_args.insert(0, "-not")
        logging.debug("ext_args: %s", ext_args)

    find_args = ["find", root, "-regextype", "posix-extended",
        *prune_args, "-type", "f", *ext_args, "-print0"]
    
    logging.debug("find_args: %s", find_args)
    return subprocess.run(find_args, text=True, capture_output=True).stdout.split("\0")[:-1]

def get_matches(files: list, expr: str, opts: Options):
    """Get lines that match the expr

    :param files: path of files to inspect
    :param expr: expression to match in files
    :param opts: options object to alter behavior of search. Uses COLOR, FILENAME, IGNORE_CASE, NAME_ONLY, LINES_NUM
    :return list[str]: lines matching the expression
    """
    grep_args = [
        "grep", "-I", opts.MATCH_TYPE.value,
        f"--color={'always' if opts.COLOR else 'never'}",
        "-H" if opts.FILENAME else "-h",
        expr
    ]
    opts.IGNORE_CASE and grep_args.insert(2, "-i")
    opts.NAME_ONLY and grep_args.insert(2, "-l")
    opts.LINES_NUM and grep_args.insert(2, "-n")
    logging.debug("grep_args: %s", grep_args)
    grep_args += files

    grep = subprocess.run(grep_args, text=True, capture_output=True).stdout.splitlines()
    return grep

def vim_format(lines: list):
    """ formats lines to be fed to vim 

    :param lines: lines that matched the expression
    :return list[str]: the same lines, formatted for vim
    """

def vim_auto():
    """ Uses vim's :grep to do the search """
    coffin_args = [arg for arg in sys.argv[1:] if arg not in ["-v", "--autovim"]]
    logging.debug("coffin_args: %s", coffin_args)
    grep_args = 'silent grep %s | cw | wincmd p' %(" ".join(coffin_args))
    logging.debug("grep_args: %s", grep_args)
    args = ["vim", "-c", grep_args]
    logging.debug("args: %s",args)
    subprocess.run(args)

options = Options()

def main():
    options = Options()
    parse_args(sys.argv, options)
    if(not options.PATTERN):
        logging.error("not enough arguments")
        display_help(1)
    if(options.AUTO_VIM):
        vim_auto()
        exit(0)
    files = get_files(options)
    logging.debug("files: %s", files)
    lines = get_matches(files, options.PATTERN, options)
    logging.debug("lines: %s", lines)
    for line in lines:
        print(line)

main()
