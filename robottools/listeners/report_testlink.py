from .docstring import DocTestParser
from testlink import TestLinkHelper, TestlinkAPIGeneric
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger as robot_logger


reportTCResultParams = [
    'testcaseid', 'testplanid', 'buildname', 'status', 'notes', 'testcaseexternalid', 'buildid', 'platformid',
    'platformname', 'guess', 'bugid', 'custumfields', 'overwrite', 'user', 'execduration', 'timestamp', 'steps',
    'devKey']
report_params = {str(param): 'testlink' + str(param) for param in reportTCResultParams}


class reporttestlink(object):
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, test_prefix, dev_key, server, *report_kwargs):
        """
        This is specifically for looking at testcaseexternalids in testcase documentation and sending results to all
        testcases found.

        If you would like to set a default input from the test itself you can add 'testlink' to the beginning of the
        parameter and it will select and add if it wasn't passed in at __init__.
        For example if you wanted to pass in the platformname you would set testlinkplatformname. This is to avoid
        robot name collisions with incredibly common variable names like user and timestamp.
        Note: dev_key is set during testlink connection and used as a default by the testlink library.
              So, if `testlinkdevkey` is passed in it will effectively take priority as the second positional arg
              dev_key is *not* put into report_kwargs. This is by design.

        Since kwargs are not supported in listeners you must pass in args with an equal sign between the key and the
        value (<argument>=<value).

        :param test_prefix: The letters preceding testlink numbers. ex. abc-1234 the test_prefix would be 'abc'
        :param dev_key: API key of the user running the tests
        :param server: The testlink server
        :param report_kwargs: These are args in the format `<argument>=<value>`.
        """
        self.test_prefix = test_prefix
        self.dev_key = dev_key
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

        self._tlh = self._testcases = None

    @property
    def tlh(self):
        if not self._tlh:
            self.connect_testlink()
        return self._tlh

    def connect_testlink(self):
        self._tlh = TestLinkHelper(self.testlink_server, self.dev_key).connect(TestlinkAPIGeneric)

    def _get_params_from_variables(self):
        for testlink_param, robot_variable in report_params.items():
            # setdefault but only if real non-None value from test
            if testlink_param not in self.report_kwargs:
                tc_report_val = BuiltIn().get_variable_value("${" + str(robot_variable) + "}")
                if tc_report_val is not None:
                    self.report_kwargs[testlink_param] = tc_report_val

    def _get_testlink_status(self, test):
        # testlink accepts p/f for passed and failed
        status = 'f'
        if test.passed:
            status = 'p'
        return status

    @property
    def testcases(self):
        if not self._testcases:
            self._testcases = self._get_testcases()
        return self._testcases

    def _get_testcases(self, test):
        return DocTestParser(self.test_prefix).get_testcases(test)

    def end_test(self, data, test):
        self.report_kwargs['status'] = self._get_testlink_status(test)
        self._get_params_from_variables()

        # This is supposed to default to true by the API spec, but doesn't on some testlink versions
        self.report_kwargs.setdefault('guess', True)

        for testcase in self.testcases:
            resp = self.tlh.reportTCResult(testcaseexternalid=testcase, **self.report_kwargs)
            robot_logger.info(resp, also_console=True)


class generatetestlink(reporttestlink):
    """This will generate a needed planid, or platform if required. And will copy the testcase into it."""
    def __init__(self, *args, **kwargs):
        super(generatetestlink, self).__init__(*args, **kwargs)
        self.gen_opts = ['testprojectid', 'testplanid', 'platformname']
        self._testplanname = self._testprojectid = self._testplanid = self._plan_testcases = None

    def generate(self):
        for gen_opt in self.gen_opts:
            value = getattr(self, gen_opt)
            if value and not getattr(self.report_kwargs, gen_opt):
                setattr(self.report_kwargs, gen_opt, value)

    @property
    def testprojectname(self):
        return self.report_kwargs.get('testprojectname')

    @property
    def testprojectid(self):
        if self._testprojectid:
            return self._testprojectid

        tpn_kwarg = self.report_kwargs.get('testprojectid')
        if tpn_kwarg:
            self._testprojectid = tpn_kwarg
        else:
            try:
                self._testprojectid = self.tlh.getTestProjectByName(self.testprojectname)['id']
            except TypeError:
                # TODO: Generate testprojectid
                self._testprojectid = None

        return self._testprojectid

    @property
    def testplanid(self):
        """This won't necessarily be able to create a testplanid. It requires a planname and projectname."""
        if not self._testplanid:
            try:
                self._testplanid = self.tlh.getTestPlanByName(self.testprojectname, self.testplanname)[0]['id']
            except TypeError:
                self._testplanid = self.generate_testplanid()
        return self._testplanid

    def generate_testplanid(self):
        if all(arg in self.report_kwargs for arg in ['testplanname', 'testprojectname']):
            tp = self.tlh.createTestPlan(self.report_kwargs['testplanname'], self.report_kwargs['testprojectname'])
            self.report_kwargs['testplanid'] = tp[0]['id']
            return self.report_kwargs['testplanid']

    @property
    def platformname(self):
        """Return a platformname added to the testplan if there is one."""
        pn_kwarg = self.report_kwargs.get('platformname')
        if pn_kwarg:
            self.generate_platformname(pn_kwarg)
        return pn_kwarg

    def generate_platformname(self, platformname):
        if platformname not in self.tlh.getTestPlanPlatforms(self.testplanid):
            self.tlh.addPlatformToTestPlan(self.testplanid, platformname)

    @property
    def plan_testcases(self):
        if not self._plan_testcases:
            self._plan_testcases = set()
            tc_dict = self.tlh.getTestCasesForTestPlan(self.testplanid)
            for _, platform in tc_dict.items():
                for k, v in platform.items():
                    self._plan_testcases.add(v['full_external_id'])
        return self._plan_testcases

    def ensure_testcases_added(self):
        for testcase in self.testcases:
            if testcase not in self.plan_testcases:
                self.tlh.addTestCaseToTestPlan(self.testprojectid, self.testplanid, testcase)
