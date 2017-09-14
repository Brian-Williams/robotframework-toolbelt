"""Search docstrings for """
import re
from robot.libraries.BuiltIn import BuiltIn


class DocTestParser(object):
    def __init__(self, doc_matcher=None, doc_matchers=None):
        """
        :param doc_matchers: List of regex to find in docstring
        """
        self.doc_matchers = doc_matchers if doc_matchers is not None else []
        if doc_matcher:
            self.doc_matchers.append(doc_matcher)

    def get_testcases(self, test):
        testcases = set()
        for matcher in self.doc_matchers:
            testcases |= set(re.findall('{}-\d+'.format(matcher), test.doc))
        return testcases


class testme(object):
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, **report_kwargs):
        self.report_kwargs = report_kwargs

    def end_test(self, data, test):
        print("the variable is " + str(BuiltIn().get_variable_value(
            "${" + self.report_kwargs.get('var') + "}")))
