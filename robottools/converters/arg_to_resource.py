"""
This needs be run from your execution directory.

Any relative path that was used as an argument will have ${EXECDIR} added in front of it so that the absolute execution
directory will be used when this Resource file is imported into a test.
"""
import argparse
from collections import namedtuple, OrderedDict
import os

robot_opt = namedtuple('robot_option', ['opt', 'value'])

# OPTIONS = {
#     'rerunfailed': ('-R', '--rerunfailed'),
#     'critical': ('-c', '--critical'),
#     'noncritical': ('-n', '--noncritical'),
#     'variable': ('-v', '--variable'),
#     'outputdir': ('-d', '--outputdir'),
#     'output': ('-o', '--output'),
#     'log': ('-l', '--log'),
#     'report': ('-r', '--report'),
#     'xunit': ('-x', '--xunit'),
#     'xunitskipnoncritical': ('--xunitskipnoncritical'),
#     'debugfile': ('-b', '--debugfile'),
#     'timestampoutputs': ('-T', '--timestampoutputs'),
#     'splitlog': ('--splitlog',),
#     'logtitle': ('--logtitle',),
#     'reporttitle': ('--reporttitle',),
#     'reportbackground': ('--reportbackground',),
#     'loglevel': ('-L', '--loglevel'),
#     'suitestatlevel': ('--suitestatlevel',),
#     'tagstatinclude': ('--tagstatinclude',),
#     'tagstatexclude': ('--tagstatexclude',),
#     'tagstatcombine': ('--tagstatcombine',),
#     'tagdoc': ('--tagdoc',),
#     'tagstatlink': ('--tagstatlink',),
#     'removekeywords': ('--removekeywords',),
#     'flattenkeywords': ('--flattenkeywords',),
#     'listener': ('--listener',)
# }

RESOURCE_OPS = {
    'var': ('-v', '--variable'),
    'Variables': ('-V', '--variablefile'),
}

RESOURCE_ARGS = {}
for k, vs in RESOURCE_OPS.items():
    for v in vs:
        RESOURCE_ARGS[v] = k

PATHABLE_OPTS = ['Variables']

VARIABLE_TAB = ['var']
SETTING_TAB = [opt for opt in RESOURCE_OPS if opt not in VARIABLE_TAB]

EXTENSION = '.resource'


class ArgToResource(object):
    def __init__(self, argfile, execdir=os.getcwd()):
        self.argfile = argfile
        self.execdir = execdir
        self._tabs = self._raw_options = None

    def create_resourcefile(self):
        with open(self.resourcefile, 'w+') as f:
            for tab, options in self.tabs.items():
                f.write(tab + '\n')
                f.write(''.join(list(self._get_tab_contents(tab, options))))
                # newline between settings
                f.write('\n')
            print("Resourcefile made for {} at {}.".format(self.argfile, self.resourcefile))

    def _get_tab_contents(self, tab, roptions):
        if tab == '*** Variables ***':
            for ropt in roptions:
                print(ropt)
                s_ropt = ropt.value.split(':')
                var_name = s_ropt[0]
                var_value = ':'.join(s_ropt[1:])
                yield "${" + var_name + "}=  " + var_value + '\n'
        if tab == '*** Settings ***':
            for ropt in roptions:
                yield ropt.opt + '  ' + ropt.value + '\n'

    @property
    def relative_path(self):
        return '${EXECDIR}/'

    @property
    def tabs(self):
        if self._tabs is None:
            self._populate_tabs()
        return self._tabs

    @property
    def resourcefilename(self):
        no_ext_path = os.path.splitext(self.argfile)[0]
        return os.path.basename(no_ext_path) + EXTENSION

    @property
    def resourcefilepath(self):
        return os.path.dirname(self.argfile) + '/'

    @property
    def resourcefile(self):
        return self.resourcefilepath + self.resourcefilename

    @property
    def raw_options(self):
        if self._raw_options is None:
            self._get_raw_options_from_argfile()
        return self._raw_options

    def _populate_tabs(self):
        self._tabs = self._sort_options()

    def _yield_options_from_line(self, line):
        opts = line.split()
        for i, opt in enumerate(opts):
            if opt == '#':
                break
            if opt in RESOURCE_ARGS:
                # This assumes one argument per line
                value = ' '.join(opts[i + 1:]).strip()
                if RESOURCE_ARGS[opt] in PATHABLE_OPTS:
                    if not value.startswith('/'):
                        value = self.relative_path + value
                yield robot_opt(RESOURCE_ARGS[opt], value)

    def _get_raw_options_from_argfile(self):
        options = []
        with open(self.argfile, 'r') as f:
            for line in f:
                for option in self._yield_options_from_line(line):
                    options.append(option)
        self._raw_options = options

    def _sort_options(self):
        variables = [robot_option for robot_option in self.raw_options if robot_option.opt in VARIABLE_TAB]
        settings = [robot_option for robot_option in self.raw_options if robot_option.opt in SETTING_TAB]
        return OrderedDict([
            ('*** Settings ***', settings),
            ('*** Variables ***', variables)
        ])


def setup_argparse():
    parser = argparse.ArgumentParser(description='Process argfiles into resource files.')
    parser.add_argument('argfiles', metavar='A', nargs='+',
                        help='argfiles to be converted into resource files')
    parser.add_argument('--force', action='store_true', help="ignore args that can't be converted")
    return parser

if __name__ == '__main__':
    parser = setup_argparse()
    args = parser.parse_args()
    for file in args.argfiles:
        atr = ArgToResource(file)
        atr.create_resourcefile()
