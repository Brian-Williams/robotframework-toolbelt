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


# won't work because of critically from root bug
class RenameThenGatherFailedSuites(resetname, gatherfailed.GatherFailedSuites):
    def start_suite(self, suite):
        for test in suite.tests:
            print("test {} {}".format(test, not test.passed))

        if any(not test.passed for test in suite.tests):
            print("goteeeem, {}".format(suite.longname))
            print("suites before append {}".format(self.suites))
            self.suites.append(suite.longname)
            print("suites after append {}".format(self.suites))

        super(RenameThenGatherFailedSuites, self).start_suite(suite)


gatherfailed.GatherFailedSuites = RenameThenGatherFailedSuites


def gather_failed_suites(output):
    if output.upper() == 'NONE':
        return []
    gatherer = RenameThenGatherFailedSuites()

    from robot.result import ExecutionResult
    ExecutionResult(output, include_keywords=False).suite.visit(gatherer)
    if not gatherer.suites:
        print('All suites passed. {}'.format(gatherer.suites))

    print("return {}".format(gatherer.suites))
    return gatherer.suites


class rerunrenamedsuites(SuiteVisitor):
    def __init__(self, output):
        self.output = output

    def start_suite(self, suite):
        print("running for {}".format(suite))
        print("Beofre {}...{}".format(suite.tests, suite.suites))

        suites = gather_failed_suites(self.output)
        print("suites {}".format(suites))
        suite.filter(included_suites=suites)
        print("After {}".format(suite.tests))
