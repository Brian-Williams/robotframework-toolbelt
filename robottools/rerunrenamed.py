from robot.errors import DataError
from robot.model import SuiteVisitor
from robot.result import ExecutionResult
from robot.utils import get_error_message


class RenameThenGatherFailedTests(SuiteVisitor):

    def __init__(self, rename):
        self.tests = []
        self.rename = rename

    def start_suite(self, suite):
        originallongname = suite.metadata['originallongname']
        # TODO: remove this
        print(originallongname)
        suite.configure(name=originallongname)

    def visit_test(self, test):
        if not test.passed:
            self.tests.append(test.longname)

    def visit_keyword(self, kw):
        pass


def rename_then_gather_failed_tests(output):
    if output.upper() == 'NONE':
        return []
    gatherer = RenameThenGatherFailedTests(output)
    try:
        ExecutionResult(output, include_keywords=False).suite.visit(gatherer)
        if not gatherer.tests:
            raise DataError('All tests passed.')
    except:
        raise DataError("Collecting failed tests from '%s' failed: %s"
                        % (output, get_error_message()))
    return gatherer.tests


class rerunrenamedtests(SuiteVisitor):
    def __init__(self, output):
        self.output = output

    def start_suite(self, suite):
        print("Original suite tests {}".format(suite.tests))
        tests = rename_then_gather_failed_tests(self.output)
        print("New tests {}".format(tests))
        suite.filter(included_tests=tests)
