import argparse
import argparse
parser = argparse.ArgumentParser(prog="coffin", usage="%(prog)s [OPTIONS]... PATTERN")
# Regexes
regexes = parser.add_mutually_exclusive_group()
regexes.add_argument("-F", "--fixed", help="interprets PATTERN as a fixed string", action="store_true")
regexes.add_argument("--basic", help="interprets PATTERN as a BRE", action="store_true")
regexes.add_argument("--extended", help="interprets PATTERN as an ERE", action="store_true")
# Format
parser.add_argument("-C", "--colors", help="toggles colored output", action="store_true")
parser.add_argument("-E", "--exclude", help="toggles exclusion based on file extensions (-e option)", action="store_true")
parser.add_argument("-v", "--autovim", help="toggles automatically calling coffin inside vim", action="store_true")
parser.add_argument("-V", "--vimformat", help="toggles vim-friendly output formatting", action="store_true")
parser.add_argument("-d", "--dry", help="toggles only outputting the names of files whose content match PATTERN", action="store_true")
parser.add_argument("--case", help="toggles case sensitivity in pattern matching", action="store_true")
parser.add_argument("--lines-num", help="toggles outputting the line number of a match", action="store_true")
# Filters
parser.add_argument("-r", "--root", help="uses ROOT as the starting point to list files to process")
parser.add_argument("-p", "--prune", help="prunes directories given")
parser.add_argument("-e", "--ext", help="filters files based on file extensions given")
# Misc
parser.add_argument("--debug", help="outputs debug informations to stderr", action="store_true")
parser.add_argument("PATTERN", help="pattern to look for in files")
args = parser.parse_args()
print(args)
