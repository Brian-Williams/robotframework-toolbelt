import re
from testlink import TestLinkHelper, TestlinkAPIGeneric


class testlink(object):
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, test_prefix, api_key, testlink_server):
        """
        :param test_prefix: The letters preceding testlink numbers. ex. act-1234 the test_prefix would be 'act'
        :param api_key: API key of the user running the tests
        :param testlink_server:
        """
        self.test_prefix = test_prefix
        # self.tlh = TestLinkHelper(testlink_server, api_key).connect(TestlinkAPIGeneric)

    def get_testcases(self, test_doc):
        testcases = re.findall('{}\-[0-9]+'.format(self.test_prefix), test_doc)
        return testcases

    def end_test(self, data, test):
        # testlink accepts p/f for passed and failed
        status = 'f'
        if test.passed:
            status = 'p'

        testcases = self.get_testcases(test.doc)
        for testcase in testcases:
            
