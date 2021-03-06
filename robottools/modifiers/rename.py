from robot.api import SuiteVisitor
from robot.conf import gatherfailed
from robot.errors import DataError
from robot.parsing.model import _TestData
from robot.result import ExecutionResult
from robot.utils import get_error_message


class rename(SuiteVisitor):
    """Store the original longname so that rerunning can happen even with virtually reorganized tests."""

    def __init__(self, new_name=None):
        self.new_name = new_name

    def start_suite(self, suite):
        if suite.id == 's1':
            originallongname = suite.longname
            suite.metadata.setdefault('originallongname', originallongname)
            suite.configure(name=self.new_name)


class resetname(SuiteVisitor):
    """Get the original longname from metadata and apply as the name."""
    def config_test(self, suite):
        originallongname = suite.metadata['originallongname']

        suite.name = originallongname
        suite.parent = None

    def config_all_suites(self, suite):
        for suite in suite.suites:
            try:
                self.config_test(suite)
            except KeyError:
                self.config_suites(suite)

    def config_suites(self, suite):
        try:
            self.config_test(suite)
        except KeyError:
            self.config_all_suites(suite)

    def start_suite(self, suite):
        self.config_suites(suite)


class RenameThenGatherFailedTests(resetname, gatherfailed.GatherFailedTests):
    pass


gatherfailed.GatherFailedTests = RenameThenGatherFailedTests


class rerunrenamedtests(SuiteVisitor):
    def __init__(self, output):
        self.output = output

    def start_suite(self, suite):
        tests = gatherfailed.gather_failed_tests(self.output)
        suite.filter(included_tests=tests)


class RenameThenGatherFailedSuites(gatherfailed.GatherFailedSuites, resetname):
    def start_suite(self, suite):
        resetname.start_suite.__get__(self)(suite)
        gatherfailed.GatherFailedSuites.start_suite.__get__(self)(suite)


# Should be copied exactly from robot/conf/gatherfailed.py
def gather_failed_suites(output):
    if output.upper() == 'NONE':
        return []
    gatherer = RenameThenGatherFailedSuites()
    try:
        ExecutionResult(output, include_keywords=False).suite.visit(gatherer)
        if not gatherer.suites:
            raise DataError('All suites passed.')
    except:
        raise DataError("Collecting failed suites from '%s' failed: %s"
                        % (output, get_error_message()))
    return gatherer.suites


class rerunrenamedsuites(SuiteVisitor):
    def __init__(self, output):
        self.output = output

    def start_suite(self, suite):
        suites = gather_failed_suites(self.output)
        suite.filter(included_suites=suites)


class TestDataNameHelper(_TestData):
    """Remove the blocker of not having *_table's defined, so that we can get name the same way as TestData"""
    def _get_tables(self, *args, **kwargs):
        # robot.utils NormalizedDict accepts None as a valid input
        return None


class unname(SuiteVisitor):
    """Change the suite names to be what they would've been had no names been changed.

    Set name based on the source regardless of name changes.

    Is the complement of name (-N, --name). Sets what would've been selected as the default name if name hadn't been
    used. Useful so external saving of original name isn't needed.
    """
    def start_suite(self, suite):
        if suite.source:
            suite.name = TestDataNameHelper(source=suite.source).name
