import argparse
import argparse
parser = argparse.ArgumentParser(
    usage="%(prog)s [OPTIONS]... PATTERN",
    description="Search for a pattern for all files under a directory"
)
# Regexes
regexes = parser.add_argument_group("Regex options")
m_regexes = regexes.add_mutually_exclusive_group()
m_regexes.add_argument("-F", "--fixed", help="interprets PATTERN as a fixed string", action="store_true")
m_regexes.add_argument("--basic", help="interprets PATTERN as a BRE", action="store_true")
m_regexes.add_argument("--extended", help="interprets PATTERN as an ERE", action="store_true")
# Format
format = parser.add_argument_group("Formatting options")
format.add_argument("-C", "--colors", help="toggles colored output", action="store_true")
format.add_argument("-E", "--exclude", help="toggles exclusion based on file extensions (-e option)", action="store_true")
format.add_argument("-v", "--autovim", help="toggles automatically calling coffin inside vim", action="store_true")
format.add_argument("-V", "--vimformat", help="toggles vim-friendly output formatting", action="store_true")
format.add_argument("-d", "--dry", help="toggles only outputting the names of files whose content match PATTERN", action="store_true")
format.add_argument("--case", help="toggles case sensitivity in pattern matching", action="store_true")
format.add_argument("--lines-num", help="toggles outputting the line number of a match", action="store_true")
# Filters
filtering = parser.add_argument_group("Filtering options")
filtering.add_argument("-r", "--root", help="uses ROOT as the starting point to list files to process")
filtering.add_argument("-p", "--prune", nargs='*', help="prunes directories given", metavar="DIRS")
filtering.add_argument("-e", "--ext", nargs='*', help="filters files based on their extensions", metavar="EXTS")
# Misc
parser.add_argument("--debug", help="outputs debug informations (to stderr)", action="store_true")
parser.add_argument("PATTERN", help="pattern to look for in files")
args = parser.parse_args()
print(args)
