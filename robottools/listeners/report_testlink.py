from .docstring import DocTestParser
from testlink import TestLinkHelper, TestlinkAPIGeneric
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger as robot_logger



class reporttestlink(object):
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, test_prefix, api_key, server, *report_kwargs):
        """
        This is specifically for looking at testcaseexternalids in testcase documentation and sending results to all
        testcases found.

        If platformname is not passed in to the listener it will search the test for ${testlinkplatform} for the
        platformname.

        Since kwargs are not supported in listeners you must pass in args with an equal sign between the key and the
        value (<argument>=<value).

        :param test_prefix: The letters preceding testlink numbers. ex. abc-1234 the test_prefix would be 'abc'
        :param api_key: API key of the user running the tests
        :param server: The testlink server
        :param report_kwargs: These are args in the format `<argument>=<value>`.
        :param nonposkwargs: py2 support for py3 style non positional kwargs
            Internal values:
                - guess=True
        """
        self.test_prefix = test_prefix
        self.api_key = api_key
        self.testlink_server = server

        # Listeners don't support real kwargs
        self.report_kwargs = {}
        for kwarg in report_kwargs:
            try:
                arg, value = kwarg.split('=')
            except ValueError:
                raise RuntimeError("Report kwarg was passed in without equal sign. '{}'".format(kwarg))
            if isinstance(value, list):
                raise RuntimeError("Report kwarg was passed in with multiple equal signs. '{}'".format(kwarg))
            self.report_kwargs[arg] = value

        self.report_kwargs.setdefault('guess', True)

        self._tlh = self._platformname = None

    @property
    def platformname(self):
        if not self._platformname:
            self._get_platform_from_variable()
        return self._platformname

    @property
    def tlh(self):
        if not self._tlh:
            self.connect_testlink()
        return self._tlh

    def connect_testlink(self):
        self._tlh = TestLinkHelper(self.testlink_server, self.api_key).connect(TestlinkAPIGeneric)

    def _get_platform_from_variable(self):
        self._platformname = BuiltIn().get_variable_value("${testlinkplatform}")

    def _get_testlink_status(self, test):
        # testlink accepts p/f for passed and failed
        status = 'f'
        if test.passed:
            status = 'p'
        return status

    def end_test(self, data, test):
        testcases = DocTestParser(self.test_prefix).get_testcases(test)
        self.report_kwargs['status'] = self._get_testlink_status(test)
        self.report_kwargs.setdefault('platformname', self.platformname)

        for testcase in testcases:
            resp = self.tlh.reportTCResult(testcaseexternalid=testcase, **self.report_kwargs)
            robot_logger.info(resp, also_console=True)
