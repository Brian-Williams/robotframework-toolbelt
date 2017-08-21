from robot.api import SuiteVisitor
from robot.conf import gatherfailed
from robot.model.testsuite import TestSuites
from copy import copy


class rename(SuiteVisitor):
    """Store the original longname so that rerunning can happen even with virtually reorganized tests."""

    def __init__(self, new_name):
        self.new_name = new_name

    def start_suite(self, suite):
        originallongname = suite.longname
        suite.metadata.setdefault('originallongname', originallongname)
        suite.configure(name=self.new_name)


class resetname(SuiteVisitor):
    def start_suite(self, suite):
        originallongname = suite.metadata['originallongname']
        suite.configure(name=originallongname)


class RenameThenGatherFailedTests(resetname):

    def __init__(self):
        self.tests = []

    def visit_test(self, test):
        if not test.passed:
            self.tests.append(test.longname)

    def visit_keyword(self, kw):
        pass

gatherfailed.GatherFailedTests = RenameThenGatherFailedTests


class rerunrenamedtests(SuiteVisitor):
    def __init__(self, output):
        self.output = output

    def start_suite(self, suite):
        tests = gatherfailed.gather_failed_tests(self.output)
        suite.filter(included_tests=tests)
