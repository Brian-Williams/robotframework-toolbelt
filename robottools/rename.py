from robot.api import SuiteVisitor
from robot.conf import gatherfailed


class rename(SuiteVisitor):
    """Store the original longname so that rerunning can happen even with virtually reorganized tests."""

    def __init__(self, new_name):
        self.new_name = new_name

    def start_suite(self, suite):
        originallongname = suite.longname
        suite.metadata.setdefault('originallongname', originallongname)
        suite.configure(name=self.new_name)


class resetname(SuiteVisitor):
    def config_test(self, suite):
        originallongname = suite.metadata['originallongname']
        try:
            suite.configure(name=originallongname)
        # Critically setting from non-root error
        except TypeError:
            for test in suite.tests:
                test.parent.name = originallongname
                test.parent.parent = None

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


# won't work because of critically from root bug
class RenameThenGatherFailedSuites(resetname, gatherfailed.GatherFailedSuites):
    pass


gatherfailed.GatherFailedSuites = RenameThenGatherFailedSuites


class rerunrenamedsuites(SuiteVisitor):
    def __init__(self, output):
        self.output = output

    def start_suite(self, suite):
        suites = gatherfailed.gather_failed_suites(self.output)
        suite.filter(included_suites=suites)
