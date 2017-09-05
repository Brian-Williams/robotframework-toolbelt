from robot.api import SuiteVisitor
import re
# from testlink import TestLinkHelper, TestlinkAPIGeneric


class testlink(SuiteVisitor):
    def __init__(self, test_prefix, api_key, testlink_server):
        """
        :param test_prefix: The letters preceding testlink numbers. ex. act-1234 the test_prefix would be 'act'
        :param api_key: API key of the user running the tests
        :param testlink_server:
        """
        self.test_prefix = test_prefix
        # self.tlh = TestLinkHelper(testlink_server, api_key).connect(TestlinkAPIGeneric)

    def end_test(self, test):
        testcases = re.findall('{}\-[0-9]+'.format(self.test_prefix))
        # testlink accepts p/f for passed and failed
        status = 'f'
        if test.passed:
            status = 'p'
