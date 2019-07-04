# -*- coding: utf-8 -*-
"""Validate Data Testing Module"""
import difflib
import hashlib
import json
import operator
import os
import re
import math
import random
from six import string_types

try:
    from urllib import unquote  # Python 2
except ImportError:
    from urllib.parse import unquote  # Python


class Validator(object):
    """Validator"""

    def __init__(self, tcex, log, log_data):
        """Initialize class properties."""
        self.log = log
        self.log_data = log_data
        self.tcex = tcex

        # properties
        self._redis = None
        self._threatconnect = None
        self.max_diff = 10

    def details(self, app_data, test_data, op):
        """Return details about the validation."""
        details = ''
        if app_data is not None and test_data is not None and op in ['eq', 'ne']:
            try:
                diff_count = 0
                for i, diff in enumerate(difflib.ndiff(app_data, test_data)):
                    if diff[0] == ' ':  # no difference
                        continue
                    elif diff[0] == '-':
                        details += '\n    * Missing data at index {}'.format(i)
                        self.log_data(
                            'validate',
                            'App Data',
                            '({}), Type: [{}]'.format(app_data, type(app_data)),
                        )
                        # self.log.info(
                        #     '[validate] App Data   : ({}), Type: [{}]'.format(
                        #         app_data, type(app_data)
                        #     )
                        # )
                    elif diff[0] == '+':
                        details += '\n    * Extra data at index {}'.format(i)
                        self.log_data(
                            'validate',
                            'Diff',
                            ('[validate] Diff       : Extra data at index {}'.format(i)),
                        )
                        # self.log.info('[validate] Diff       : Extra data at index {}'.format(i))
                    if diff_count > self.max_diff:
                        details += '\n    * Max number of differences reached.'
                        # don't spam the logs if string are vastly different
                        self.log_data(
                            'validate', 'Maximum Reached', 'Max number of differences reached.'
                        )
                        # self.log.info('[validate] Max number of differences reached.')
                        break
                    diff_count += 1
            except TypeError:
                pass
            except KeyError:
                pass
        return details

    def get_operator(self, op):
        """Get the corresponding operator"""
        operators = {
            'dd': self.operator_deep_diff,
            'eq': self.operator_eq,
            '=': self.operator_eq,
            'le': self.operator_le,
            '<=': self.operator_le,
            'lt': self.operator_lt,
            '<': self.operator_lt,
            'ge': self.operator_ge,
            '>=': self.operator_ge,
            'gt': self.operator_gt,
            '>': self.operator_gt,
            'jeq': self.operator_json_eq,
            'json_eq': self.operator_json_eq,
            'kveq': self.operator_keyvalue_eq,
            'keyvalue_eq': self.operator_keyvalue_eq,
            'ne': self.operator_ne,
            '!=': self.operator_ne,
            'rex': self.operator_regex_match,
        }
        return operators.get(op, None)

    def operator_deep_diff(self, app_data, test_data):
        """Compare app data equals tests data.

        Args:
            app_data (dict|str|list): The data created by the App.
            test_data (dict|str|list): The data provided in the test case.
            exclude_keys (list, kwargs): A list of key for a KeyValueArray to be removed.

        Returns:
            bool: The results of the operator.
        """
        try:
            from deepdiff import DeepDiff
        except ImportError:
            self.log.error('Could not import DeepDiff module (try "pip install deepdiff").')
            return False

        # run operator
        try:
            ddiff = DeepDiff(app_data, test_data, ignore_order=True)
        except KeyError:
            return False, 'Encountered KeyError when running deepdiff'
        except NameError:
            return False, 'Encountered NameError when running deepdiff'

        if ddiff:
            return False, ddiff
        return True, ''

    def operator_eq(self, app_data, tests_data):
        """Compare app data is equal to tests data.

        Args:
            app_data (dict, list, str): The data created by the App.
            test_data (dict, list, str): The data provided in the test case.

        Returns:
            bool, str: The results of the operator and any error message
        """
        results = operator.eq(app_data, tests_data)
        return results, self.details(app_data, tests_data, 'eq')

    @staticmethod
    def operator_ge(app_data, tests_data):
        """Compare app data is greater than or equal to tests data.

        Args:
            app_data (dict, list, str): The data created by the App.
            test_data (dict, list, str): The data provided in the test case.

        Returns:
            bool, str: The results of the operator and any error message
        """
        results = operator.ne(app_data, tests_data)
        details = ''
        if not results:
            details = 'App data is not greater than or equal to test data'
        return results, details

    @staticmethod
    def operator_gt(app_data, tests_data):
        """Compare app data is greater than tests data.

        Args:
            app_data (dict, list, str): The data created by the App.
            test_data (dict, list, str): The data provided in the test case.

        Returns:
            bool, str: The results of the operator and any error message
        """
        results = operator.ne(app_data, tests_data)
        details = ''
        if not results:
            details = 'App data is not greater than to test data'
        return results, details

    def operator_json_eq(self, app_data, test_data, **kwargs):
        """Compare app data equals tests data.

        Args:
            app_data (dict|str|list): The data created by the App.
            test_data (dict|str|list): The data provided in the test case.

        Returns:
            bool: The results of the operator.
        """
        if isinstance(app_data, (string_types)):
            app_data = json.loads(app_data)
        if isinstance(test_data, (string_types)):
            test_data = json.loads(test_data)

        # remove exclude field. usually dynamic data like date fields.
        for e in kwargs.get('exclude', []):
            try:
                del app_data[e]
            except KeyError:
                pass

            try:
                del test_data[e]
            except KeyError:
                pass
            del kwargs['exclude']
        return self.operator_deep_diff(app_data, test_data)

    def operator_keyvalue_eq(self, app_data, test_data, **kwargs):
        """Compare app data equals tests data.

        Args:
            app_data (dict|str|list): The data created by the App.
            test_data (dict|str|list): The data provided in the test case.

        Returns:
            bool: The results of the operator.
        """
        # remove exclude_key field. usually dynamic data like date fields.
        if kwargs.get('exclude_keys') is not None:
            app_data = [
                kv for kv in app_data if kv.get('key') not in kwargs.get('exclude_keys', [])
            ]
            test_data = [
                kv for kv in test_data if kv.get('key') not in kwargs.get('exclude_keys', [])
            ]
            del kwargs['exclude_keys']

        return self.operator_deep_diff(app_data, test_data, **kwargs)

    @staticmethod
    def operator_le(app_data, tests_data):
        """Compare app data is less than or equal to tests data.

        Args:
            app_data (dict, list, str): The data created by the App.
            test_data (dict, list, str): The data provided in the test case.

        Returns:
            bool, str: The results of the operator and any error message
        """
        results = operator.ne(app_data, tests_data)
        details = ''
        if not results:
            details = 'App data is not less than or equal to test data'
        return results, details

    @staticmethod
    def operator_lt(app_data, tests_data):
        """Compare app data is less than tests data.

        Args:
            app_data (dict, list, str): The data created by the App.
            test_data (dict, list, str): The data provided in the test case.

        Returns:
            bool, str: The results of the operator and any error message
        """
        results = operator.ne(app_data, tests_data)
        details = ''
        if not results:
            details = 'App data is not less than to test data'
        return results, details

    def operator_ne(self, app_data, tests_data):
        """Compare app data is not equal to tests data.

        Args:
            app_data (dict, list, str): The data created by the App.
            test_data (dict, list, str): The data provided in the test case.

        Returns:
            bool, str: The results of the operator and any error message
        """
        results = operator.ne(app_data, tests_data)
        return results, self.details(app_data, tests_data, 'eq')

    @staticmethod
    def operator_regex_match(app_data, test_data):
        """Compare app data equals tests data.

        Args:
            app_data (dict|str|list): The data created by the App.
            test_data (dict|str|list): The data provided in the test case.

        Returns:
            bool: The results of the operator.
        """
        if re.match(test_data, app_data) is None:
            return False, 'app_data id not match regex ({})'.format(test_data)
        return True, ''

    @property
    def redis(self):
        """Get the current instance of Redis for validating data"""
        if not self._redis:
            self._redis = Redis(self)
        return self._redis

    @property
    def threatconnect(self):
        """Get the current instance of ThreatConnect for validating data"""
        if not self._threatconnect:
            self._threatconnect = ThreatConnect(self)
        return self._threatconnect


class Redis(object):
    """Validates Redis data"""

    def __init__(self, provider, truncate=50):
        """Initialize class properties."""
        self.provider = provider
        self.truncate = truncate

        # Properties
        self.log_data = self.provider.log_data
        self.redis_client = provider.tcex.playbook.db.r

    def not_null(self, variable):
        """Validate that a variable is not empty/null"""
        # Could do something like self.ne(variable, None), but want to be pretty specific on
        # the errors on this one
        variable_data = self.provider.tcex.playbook.read(variable)
        self.log_data('validate', 'Variable', variable)
        self.log_data('validate', 'DB Data', variable_data)
        # self.provider.log.info('[validate] Variable: {}'.format(variable))
        # self.provider.log.info('[validate] DB Data: {}'.format(variable_data))
        if not variable:
            self.provider.log.error('NoneError: Redis Variable not provided')
            return False

        if not variable_data:
            self.provider.log.error(
                'NotFoundError: Redis Variable {} was not found.'.format(variable)
            )
            return False

        return True

    def type(self, variable):
        """Validate the type of a redis variable"""
        variable_data = self.provider.tcex.playbook.read(variable)
        self.log_data('validate', 'Variable', variable)
        self.log_data('validate', 'DB Data', variable_data)
        # self.provider.log.info('[validate] Variable: {}'.format(variable))
        # self.provider.log.info('[validate] App Data: {}'.format(variable_data))
        redis_type = self.provider.tcex.playbook.variable_type(variable)
        if redis_type.endswith('Array'):
            redis_type = list
        elif redis_type.startswith('String'):
            redis_type = str
        elif redis_type.startswith('KeyValuePair'):
            redis_type = dict
        else:
            redis_type = str

        if not variable_data:
            self.provider.log.error(
                'NotFoundError: Redis Variable {} was not found.'.format(variable)
            )
            return False
        if not isinstance(variable_data, redis_type):
            self.provider.log.error(
                'TypeMismatchError: Redis Type: {} and Variable: {} '
                'do not match'.format(redis_type, variable)
            )
            return False

        return True

    def data(self, variable, test_data, op=None, **kwargs):
        """Validate Redis data <operator> test_data.

        Args:
            variable (str): The variable to read from REDIS.
            data (dict or list or str): The validation data
            op (str, optional): The comparison operator expression. Defaults to "eq".

        Returns:
            [type]: [description]
        """
        op = op or 'eq'
        if not variable:
            self.provider.log.error('NoneError: Redis Variable not provided')
            return False

        if not self.provider.get_operator(op):
            self.provider.log.error('Invalid operator provided ({})'.format(op))
            return False

        if variable.endswith('Binary'):
            app_data = self.provider.tcex.playbook.read_binary(variable, False, False)
        elif variable.endswith('BinaryArray'):
            app_data = self.provider.tcex.playbook.read_binary_array(variable, False, False)
        else:
            app_data = self.provider.tcex.playbook.read(variable)

        # logging header
        self.provider.log.info('{0} {1} {0}'.format('-' * 10, variable))

        # run operator
        passed, details = self.provider.get_operator(op)(app_data, test_data, **kwargs)

        # log validation data in a readable format
        self.validate_log_output(passed, app_data, test_data, details.strip(), op)

        # build assert error
        assert_error = '\n App Data     : {}\n Expected Data: {}\n Details      : {}\n'.format(
            app_data, test_data, details
        )
        return passed, assert_error

    def eq(self, variable, data):
        """Validate test data equality"""
        return self.data(variable, data)

    def dd(self, variable, data, **kwargs):
        """Validate test data equality"""
        return self.data(variable, data, op='dd', **kwargs)

    def ge(self, variable, data):
        """Validate test data equality"""
        return self.data(variable, data, op='ge')

    def gt(self, variable, data):
        """Validate test data equality"""
        return self.data(variable, data, op='gt')

    def jeq(self, variable, data, **kwargs):
        """Validate JSON data equality"""
        return self.data(variable, data, op='jeq', **kwargs)

    def json_eq(self, variable, data, **kwargs):
        """Validate JSON data equality"""
        return self.data(variable, data, op='jeq', **kwargs)

    def kveq(self, variable, data, **kwargs):
        """Validate JSON data equality"""
        return self.data(variable, data, op='kveq', **kwargs)

    def keyvalue_eq(self, variable, data, **kwargs):
        """Validate JSON data equality"""
        return self.data(variable, data, op='kveq', **kwargs)

    def lt(self, variable, data):
        """Validate test data less than"""
        return self.data(variable, data, op='lt')

    def le(self, variable, data):
        """Validate test data less than or equal"""
        return self.data(variable, data, op='le')

    def ne(self, variable, data):
        """Validate test data non equality"""
        return self.data(variable, data, op='ne')

    def rex(self, variable, data):
        """Test App data with regex"""
        return self.data(variable, r'{}'.format(data), op='rex')

    def validate_log_output(self, passed, app_data, test_data, details, op):
        """Format the validation log output to be easier to read.

        Args:
            passed (bool): The results of the validation test.
            app_data (str): The data store in Redis.
            test_data (str): The user provided data.
            op (str): The comparison operator.

        Raises:
            RuntimeError: Raise error on validation failure if halt_on_fail is True.
        """
        truncate = self.truncate
        if app_data is not None and passed:
            if isinstance(app_data, (string_types)) and len(app_data) > truncate:
                app_data = app_data[:truncate]
            elif isinstance(app_data, (list)):
                db_data_truncated = []
                for d in app_data:
                    if d is not None and isinstance(d, string_types) and len(d) > truncate:
                        db_data_truncated.append('{} ...'.format(d[: self.truncate]))
                    else:
                        db_data_truncated.append(d)
                app_data = db_data_truncated

        if test_data is not None and passed:
            if isinstance(test_data, (string_types)) and len(test_data) > truncate:
                test_data = test_data[: self.truncate]
            elif isinstance(test_data, (list)):
                user_data_truncated = []
                for u in test_data:
                    if isinstance(app_data, (string_types)) and len(u) > truncate:
                        user_data_truncated.append('{} ...'.format(u[: self.truncate]))
                    else:
                        user_data_truncated.append(u)
                test_data = user_data_truncated

        self.log_data('validate', 'App Data', '({}), Type: [{}]'.format(app_data, type(app_data)))
        self.log_data('validate', 'Operator', op)
        self.log_data('validate', 'Test Data', '({}), Type: [{}]'.format(test_data, type(app_data)))
        # self.provider.log.info(
        #     '[validate] App Data   : ({}), Type: [{}]'.format(app_data, type(app_data))
        # )
        # self.provider.log.info('[validate] Operator  : ({})'.format(op))
        # self.provider.log.info(
        #     '[validate] Test Data  : ({}), Type: [{}]'.format(test_data, type(test_data))
        # )

        if passed:
            self.log_data('validate', 'Result', 'Passed')
            # self.provider.log.info('[validate] Results    : Passed')
        else:
            self.log_data('validate', 'Result', 'Failed')
            self.log_data('validate', 'Details', details)
            # self.provider.log.error('[validate] Results    : Failed')
            # self.provider.log.error('[validate] Details    : {}'.format(details))


class ThreatConnect(object):
    """Validate ThreatConnect data"""

    def __init__(self, provider):
        """Initialize class properties"""
        self.provider = provider

    def batch(self, context, owner, validation_criteria):
        """Validates the batch submission"""

        validation_percent = validation_criteria.get('percent', 100)
        validation_count = validation_criteria.get('count', None)
        batch_submit_totals = self._get_batch_submit_totals(context)

        if validation_count:
            validation_percent = self._convert_to_percent(validation_count, batch_submit_totals)

        for filename in os.listdir(os.path.join('.', 'log', context)):
            if not filename.startswith('batch-') or not filename.endswith('.json'):
                continue

            with open(os.path.join('.', 'log', context, filename), 'r') as fh:
                data = json.load(fh)
                validation_data = self._partition_batch_data(data)
                sample_validation_data = []
                for key in validation_data:
                    for sub_partition in validation_data.get(key).values():
                        sample_size = math.ceil(len(sub_partition) * (validation_percent / 100))
                        sample_validation_data.extend(random.sample(sub_partition, sample_size))
                results = self.tc_entities(sample_validation_data, owner)
                passed = True
                for result in results:
                    if not result:
                        passed = False
                assert passed, (
                    'One or more of the Batch Requests did not match with what is '
                    'currently in ThreatConnect. View tests.log for additional details.'
                )

    def dir(self, directory, owner):
        """Validate the content of a given dir"""
        results = []
        for test_file in os.listdir(directory):
            if not (test_file.endswith('.json') and test_file.startswith('validate_')):
                continue
            results.append(self.file('{}/{}'.format(directory, test_file), owner))
        return results

    def file(self, file, owner):
        """Validate the content of a given file"""
        entities = self._convert_to_entities(file)
        return self.tc_entities(entities, owner)

    def tc_entities(self, tc_entities, owner, files=None):
        """Validate a array of tc_entities"""
        results = []
        if files:
            if not len(tc_entities) == len(files):
                return {
                    'valid': True,
                    'errors': [
                        'LengthError: Length of files provided does not '
                        'match length of entities provided.'
                    ],
                }

        for index, entity in enumerate(tc_entities):
            if files:
                results.append(self.tc_entity(entity, owner, files[index]))
            results.append(self.tc_entity(entity, owner))
        return results

    def tc_entity(self, tc_entity, owner, file=None):
        """Validate the ti_response entity"""
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        valid = True
        ti_entity = self._convert_to_ti_entity(tc_entity, owner)
        ti_response = ti_entity.single(params=parameters)
        if not self.success(ti_response):
            print('unique_id: ', ti_entity.unique_id)
            self.provider.log.error(
                'NotFoundError: Provided {}: {} could not be fetched from ThreatConnect'.format(
                    tc_entity.get('type'), tc_entity.get('summary', tc_entity.get('name', None))
                )
            )
            return False

        ti_response_entity = None
        ti_response = ti_response.json().get('data', {}).get(ti_entity.api_entity, {})
        for entity in self.provider.tcex.ti.entities(ti_response, tc_entity.get('type', None)):
            ti_response_entity = entity
            valid_attributes = self._response_attributes(ti_response, tc_entity)
            valid_tags = self._response_tags(ti_response, tc_entity)
            valid_labels = self._response_labels(ti_response, tc_entity)
            valid_file = self._file(ti_entity, file)
            if not valid_attributes or not valid_tags or not valid_labels or not valid_file:
                valid = False

        if ti_entity.type == 'Indicator':
            provided_rating = tc_entity.get('rating', None)
            expected_rating = ti_response.get('rating', None)
            if not provided_rating == expected_rating:
                self.provider.log.error(
                    'RatingError: Provided rating {} does not match '
                    'actual rating {}'.format(provided_rating, expected_rating)
                )
                valid = False

            provided_confidence = tc_entity.get('confidence', None)
            expected_confidence = ti_response.get('confidence', None)
            if not provided_confidence == expected_confidence:
                self.provider.log.error(
                    'ConfidenceError: Provided confidence {} does not match '
                    'actual confidence {}'.format(provided_confidence, expected_confidence)
                )
                valid = False
            provided_summary = unquote(
                ':'.join([x for x in ti_entity.unique_id.split(':') if x.strip()])
            )
            expected_summary = unquote(ti_response_entity.get('value', ''))
            if provided_summary != expected_summary:
                self.provider.log.error(
                    'SummaryError: Provided summary {} does not match '
                    'actual summary {}'.format(provided_summary, expected_summary)
                )
                valid = False
        elif ti_entity.type == 'Group':
            provided_summary = tc_entity.get('name', None)
            expected_summary = ti_response_entity.get('value', None)
            if not provided_summary == expected_summary:
                self.provider.log.error(
                    'SummaryError: Provided summary {} does not match '
                    'actual summary {}'.format(provided_summary, expected_summary)
                )
                valid = False
        return valid

    def flatten(self, lis):
        """Idk why python doesnt have this built in but helper function to flatten a list"""
        new_lis = []
        for item in lis:
            if isinstance(item, list):
                new_lis.extend(self.flatten(item))
            else:
                new_lis.append(item)
        return new_lis

    def compare_dicts(self, expected, actual, error_type=''):
        """Compare two dicts and returns a list of errors if they don't match"""
        valid = True
        for item in expected:
            if item in actual:
                if str(expected.get(item)) != actual.get(item):
                    self.provider.log.error(
                        '{0}{1} : {2} did not match {1} : {3}'.format(
                            error_type, item, expected.get(item), actual.get(item)
                        )
                    )
                    valid = False
                actual.pop(item)
            else:
                self.provider.log.error(
                    '{}{} : {} was in expected results but not in actual results.'.format(
                        error_type, item, expected.get(item)
                    )
                )
                valid = False
        for item in list(actual.items()):
            self.provider.log.error(
                '{}{} : {} was in actual results but not in expected results.'.format(
                    error_type, item, actual.get(item)
                )
            )
            valid = False

        return valid

    def compare_lists(self, expected, actual, error_type=''):
        """Compare two lists and returns a list of errors if they don't match"""
        valid = True
        for item in expected:
            if item in actual:
                actual.remove(item)
            else:
                self.provider.log.error(
                    '{}{} was in expected results but not in actual results.'.format(
                        error_type, item
                    )
                )
                valid = False
        for item in actual:
            self.provider.log.error(
                '{}{} was in actual results but not in expected results.'.format(error_type, item)
            )
            valid = False

        return valid

    @staticmethod
    def _convert_to_entities(file):
        """Convert file to tc_entity array"""
        with open(file, 'r') as read_file:
            data = json.load(read_file)
        return data

    def _custom_indicators(self):
        indicator_details = self.provider.tcex.indicator_types_data
        custom_indicators = []
        for indicator in indicator_details.values():
            if indicator.get('custom', False):
                custom_indicators.append(indicator.get('name'))

        return custom_indicators

    def _convert_to_ti_entity(self, tc_entity, owner):
        """Convert a tc_entity to a ti_entity"""
        ti_entity = None

        if tc_entity.get('type') in self.provider.tcex.group_types:
            # We can't search by xid sadly so have to search by name and validate xid to
            # get the id of the group.
            filters = self.provider.tcex.ti.filters()
            filters.add_filter('name', '=', tc_entity.get('name'))
            generic_group_entity = self.provider.tcex.ti.group(
                group_type=tc_entity.get('type'), owner=owner
            )
            parameters = {'includes': ['additional']}
            for entity in generic_group_entity.many(filters=filters, params=parameters):
                if entity.get('xid') == tc_entity.get('xid'):
                    ti_entity = self.provider.tcex.ti.group(
                        group_type=tc_entity.get('type'),
                        owner=owner,
                        name=entity.get('name'),
                        unique_id=entity.get('id'),
                    )
        elif tc_entity.get('type') in self.provider.tcex.indicator_types:
            tc_entity['summary'] = unquote(tc_entity.get('summary'))
            if tc_entity.get('type').lower() == 'file':
                tc_entity['summary'] = tc_entity.get('summary').upper()
            ti_entity = self.provider.tcex.ti.indicator(
                indicator_type=tc_entity.get('type'),
                owner=owner,
                unique_id=tc_entity.get('summary'),
            )
        elif tc_entity.get('type') == 'Victim':
            # TODO: Will need to do something similar to what was done to get the groups entity.
            pass

        return ti_entity

    def _get_batch_submit_totals(self, context):
        """Breaks the batch submitions up into seperate partitions with each partition containing
        its total."""
        counts = {}
        for filename in os.listdir(os.path.join('.', 'log', context)):
            if not filename.startswith('batch-') or not filename.endswith('.json'):
                continue
            with open(os.path.join('.', 'log', context, filename), 'r') as fh:
                data = json.load(fh)
                partitioned_data = self._partition_batch_data(data)
                for key in partitioned_data:
                    if key not in counts:
                        counts[key] = {}
                    for sub_key in partitioned_data.get(key):
                        if sub_key not in counts:
                            counts[key][sub_key] = 0
                        counts[key][sub_key] += len(partitioned_data[key][sub_key])
        return counts

    @staticmethod
    def _convert_to_percent(validation_count, batch_submit_totals):
        """Given a count, calculate what percentage of the batch submits that is"""
        total = 0
        for key in batch_submit_totals.keys():
            for count in batch_submit_totals.get(key).values():
                total += count
        if validation_count > total:
            return 100
        return round((validation_count / total) * 100, 2)

    @staticmethod
    def _partition_batch_data(data):
        """Partitions the batch submittions into batch_submit[type][subtype] partitions"""
        partitioned_data = {}
        for key in data.keys():
            partitioned_sub_data = {}
            for sub_data in data.get(key):
                if not sub_data.get('type') in partitioned_sub_data.keys():
                    partitioned_sub_data[sub_data.get('type')] = [sub_data]
                else:
                    partitioned_sub_data[sub_data.get('type')].append(sub_data)
            partitioned_data[key] = partitioned_sub_data
        return partitioned_data

    def _response_attributes(self, ti_response, tc_entity):
        """Validate the ti_response attributes"""
        if not ti_response or not tc_entity:
            return True

        expected = {}
        actual = {}
        for attribute in tc_entity.get('attribute', []):
            expected[attribute.get('type')] = attribute.get('value')
        for attribute in ti_response.get('attribute', []):
            actual[attribute.get('type')] = attribute.get('value')
        valid = self.compare_dicts(expected, actual, error_type='AttributeError: ')

        return valid

    def _response_tags(self, ti_response, tc_entity):
        """Validate the ti_response tags"""
        if not ti_response or not tc_entity:
            return True

        expected = []
        actual = []
        for tag in tc_entity.get('tag', []):
            expected.append(tag.get('name'))
        for tag in ti_response.get('tag', []):
            actual.append(tag.get('name'))
        valid = self.compare_lists(expected, actual, error_type='TagError: ')

        return valid

    def _response_labels(self, ti_response, tc_entity):
        """Validate the ti_response labels"""
        if not ti_response or not tc_entity:
            return True

        expected = []
        actual = []
        for tag in tc_entity.get('securityLabel', []):
            expected.append(tag)
        for tag in ti_response.get('securityLabel', []):
            actual.append(tag.get('name'))
        valid = self.compare_lists(expected, actual, error_type='SecurityLabelError: ')

        return valid

    def _file(self, ti_entity, file):
        """Handle file data"""
        if not file:
            return True

        valid = True
        if ti_entity.api_sub_type == 'Document' or ti_entity.api_sub_type == 'Report':
            actual_hash = ti_entity.get_file_hash()
            actual_hash = actual_hash.hexdigest()
            provided_hash = hashlib.sha256()
            with open(file, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    provided_hash.update(byte_block)
            provided_hash = provided_hash.hexdigest()
            if not provided_hash == actual_hash:
                self.provider.log.error(
                    'sha256 {} of provided file did not match sha256 of actual file {}'.format(
                        provided_hash, actual_hash
                    )
                )
                valid = False
        return valid

    @staticmethod
    def success(r):
        """

        Args:
            r:

        Return:

        """
        status = True
        if r.ok:
            try:
                if r.json().get('status') != 'Success':
                    status = False
            except Exception:
                status = False
        else:
            status = False
        return status