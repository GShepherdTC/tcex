# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import pytest


# pylint: disable=no-self-use
class TestUtils:
    """Test the TcEx Batch Module."""

    tc_playbook_out_variables = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.tc_playbook_out_variables = [
            '#App:0001:b1!Binary',
            '#App:0001:b2!Binary',
            '#App:0001:b3!Binary',
            '#App:0001:b4!Binary',
            '#App:0001:ba1!BinaryArray',
            '#App:0001:ba2!BinaryArray',
            '#App:0001:ba3!BinaryArray',
            '#App:0001:ba4!BinaryArray',
            '#App:0001:kv1!KeyValue',
            '#App:0001:kv2!KeyValue',
            '#App:0001:kv3!KeyValue',
            '#App:0001:kv4!KeyValue',
            '#App:0001:kva1!KeyValueArray',
            '#App:0001:kva2!KeyValueArray',
            '#App:0001:kva3!KeyValueArray',
            '#App:0001:kva4!KeyValueArray',
            '#App:0001:s1!String',
            '#App:0001:s2!String',
            '#App:0001:s3!String',
            '#App:0001:s4!String',
            '#App:0001:sa1!StringArray',
            '#App:0001:sa2!StringArray',
            '#App:0001:sa3!StringArray',
            '#App:0001:sa4!StringArray',
            '#App:0001:te1!TCEntity',
            '#App:0001:te2!TCEntity',
            '#App:0001:te3!TCEntity',
            '#App:0001:te4!TCEntity',
            '#App:0001:tea1!TCEntityArray',
            '#App:0001:tea2!TCEntityArray',
            '#App:0001:tea3!TCEntityArray',
            '#App:0001:tea4!TCEntityArray',
            '#App:0001:r1!Raw',
            '#App:0001:dup.name!String',
            '#App:0001:dup.name!StringArray',
        ]

    @pytest.mark.parametrize(
        'output_data',
        [
            (
                [
                    {'variable': '#App:0001:b1!Binary', 'value': b'bytes'},
                    {
                        'variable': '#App:0001:ba1!BinaryArray',
                        'value': [b'not', b'really', b'binary'],
                    },
                    {'variable': '#App:0001:kv1!KeyValue', 'value': {'key': 'one', 'value': '1'}},
                    {
                        'variable': '#App:0001:kva1!KeyValueArray',
                        'value': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
                    },
                    {
                        'variable': '#App:0001:kva1!KeyValueArray',
                        'value': {'key': 'three', 'value': '3'},
                    },
                    {'variable': '#App:0001:s1!String', 'value': '1'},
                    {'variable': '#App:0001:sa1!StringArray', 'value': ['a', 'b', 'c']},
                    {'variable': '#App:0001:sa1!StringArray', 'value': ['d', 'e', 'f']},
                    {
                        'variable': '#App:0001:te1!TCEntity',
                        'value': {'id': '123', 'type': 'Address', 'value': '1.1.1.1'},
                    },
                    {
                        'variable': '#App:0001:tea1!TCEntityArray',
                        'value': [
                            {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                            {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                        ],
                    },
                    {'variable': '#App:0001:r1!Raw', 'value': 'raw data'},
                    {'variable': '#App:0001:n1!None', 'value': None},
                ]
            )
        ],
    )
    def test_playbook_add_output(self, output_data, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # add all output
        expected_data = {}
        for od in output_data:
            variable = od.get('variable')
            value = od.get('value')

            parsed_variable = tcex.playbook.parse_variable(variable)
            variable_name = parsed_variable.get('name')
            variable_type = parsed_variable.get('type')
            tcex.playbook.add_output(variable_name, value, variable_type)

            if variable in expected_data:
                if isinstance(value, list):
                    expected_data[variable].extend(value)
                else:
                    expected_data[variable].append(value)
            else:
                expected_data.setdefault(variable, value)

        # write output
        tcex.playbook.write_output()

        # validate output
        for variable, value in expected_data.items():
            result = tcex.playbook.read(variable)

            assert result == value, f'result of ({result}) does not match ({value})'

            tcex.playbook.delete(variable)
            assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'output_data',
        [
            (
                [
                    {'variable': '#App:0001:b1!Binary', 'value': b'bytes'},
                    {
                        'variable': '#App:0001:ba1!BinaryArray',
                        'value': [b'not', b'really', b'binary'],
                    },
                    {'variable': '#App:0001:kv1!KeyValue', 'value': {'key': 'one', 'value': '1'}},
                    {
                        'variable': '#App:0001:kva1!KeyValueArray',
                        'value': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
                    },
                    {'variable': '#App:0001:s1!String', 'value': '1'},
                    {'variable': '#App:0001:sa1!StringArray', 'value': ['a', 'b', 'c']},
                    {'variable': '#App:0001:sa1!StringArray', 'value': ['d', 'e', 'f']},
                    {
                        'variable': '#App:0001:te1!TCEntity',
                        'value': {'id': '123', 'type': 'Address', 'value': '1.1.1.1'},
                    },
                    {
                        'variable': '#App:0001:tea1!TCEntityArray',
                        'value': [
                            {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                            {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                        ],
                    },
                    {'variable': '#App:0001:r1!Raw', 'value': 'raw data'},
                    {'variable': '#App:0001:n1!None', 'value': None},
                ]
            )
        ],
    )
    def test_playbook_add_output_no_append(self, output_data, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # add all output
        expected_data = {}
        for od in output_data:
            variable = od.get('variable')
            value = od.get('value')

            parsed_variable = tcex.playbook.parse_variable(variable)
            variable_name = parsed_variable.get('name')
            variable_type = parsed_variable.get('type')
            tcex.playbook.add_output(variable_name, value, variable_type, append_array=False)

            expected_data[variable] = value

        # write output
        tcex.playbook.write_output()

        # validate output
        for variable, value in expected_data.items():
            result = tcex.playbook.read(variable)

            assert result == value, f'result of ({result}) does not match ({value})'

            tcex.playbook.delete(variable)
            assert tcex.playbook.read(variable) is None

    def test_playbook_check_output_variable(self, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        assert tcex.playbook.check_output_variable('b1') is True

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0001:b1!Binary', b'not really binary'),
            ('#App:0001:ba1!BinaryArray', [b'not', b'really', b'binary']),
            ('#App:0001:kv1!KeyValue', {'key': 'one', 'value': '1'}),
            (
                '#App:0001:kva1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
            ),
            ('#App:0001:s1!String', '1'),
            ('#App:0001:s2!String', '2'),
            ('#App:0001:s3!String', '3'),
            ('#App:0001:s4!String', '4'),
            ('#App:0001:sa1!StringArray', ['a', 'b', 'c']),
            ('#App:0001:te1!TCEntity', {'id': '123', 'type': 'Address', 'value': '1.1.1.1'}),
            (
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                    {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                ],
            ),
            ('#App:0001:r1!Raw', 'raw data'),
            ('#App:0001:dup.name!String', 'dup name'),
            ('#App:0001:dup.name!StringArray', ['dup name']),
        ],
    )
    def test_playbook_create_output(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # parse variable and send to create_output() method
        parsed_variable = tcex.playbook.parse_variable(variable)
        variable_name = parsed_variable.get('name')
        variable_type = parsed_variable.get('type')
        tcex.playbook.create_output(variable_name, value, variable_type)
        result = tcex.playbook.read(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0001:b1!Binary', b'not really binary'),
            ('#App:0001:ba1!BinaryArray', [b'not', b'really', b'binary']),
            ('#App:0001:kv1!KeyValue', {'key': 'one', 'value': '1'}),
            (
                '#App:0001:kva1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
            ),
            ('#App:0001:s1!String', '1'),
            ('#App:0001:s2!String', '2'),
            ('#App:0001:s3!String', '3'),
            ('#App:0001:s4!String', '4'),
            ('#App:0001:sa1!StringArray', ['a', 'b', 'c']),
            ('#App:0001:te1!TCEntity', {'id': '123', 'type': 'Address', 'value': '1.1.1.1'}),
            (
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                    {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                ],
            ),
            ('#App:0001:r1!Raw', 'raw data'),
        ],
    )
    def test_playbook_create_output_without_type(self, variable, value, playbook_app):
        """Test the create output method of Playbook module without passing type.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # parse variable and send to create_output() method
        parsed_variable = tcex.playbook.parse_variable(variable)
        variable_name = parsed_variable.get('name')
        tcex.playbook.create_output(variable_name, value)
        result = tcex.playbook.read(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0001:not_requested!String', 'not requested'),
            ('#App:0001:none!String', 'None'),
            ('#App:0001:dup.name!String', None),
            ('#App:0001:dup.name!StringArray', None),
        ],
    )
    def test_playbook_create_output_not_written(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # parse variable and send to create_output() method
        parsed_variable = tcex.playbook.parse_variable(variable)
        variable_name = parsed_variable.get('name')
        variable_type = parsed_variable.get('type')
        tcex.playbook.create_output(variable_name, value, variable_type)

        result = tcex.playbook.read(variable)
        assert result is None, f'result of ({result}) should be None'

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0001:not_requested!String', 'not requested'),
            ('#App:0001:none!String', None),
            (None, None),  # coverage
        ],
    )
    def test_playbook_create_output_not_written_without_type(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # parse variable and send to create_output() method
        parsed_variable = tcex.playbook.parse_variable(variable)
        variable_name = None  # coverage
        if variable is not None:
            variable_name = parsed_variable.get('name')
        tcex.playbook.create_output(variable_name, value)

        result = tcex.playbook.read(variable)
        assert result is None, f'result of ({result}) should be None'

    def test_playbook_exit(self, tcex):
        """Test the create output method of Playbook module.

        Args:
            tcex (TcEx, fixture): The tcex fixture.
        """
        try:
            tcex.playbook.exit(0)  # coverage
            assert False, 'Exit command did not trigger SystemExit'
        except SystemExit:
            pass

    def test_playbook_exit_code_3(self, tcex):
        """Test the create output method of Playbook module.

        Args:
            tcex (TcEx, fixture): The tcex fixture.
        """
        try:
            tcex.exit_code = 3
            tcex.playbook.exit()  # coverage
            assert False, 'Exit command did not trigger SystemExit'
        except SystemExit:
            pass

    def test_playbook_exit_code_9(self, tcex):
        """Test the create output method of Playbook module.

        Args:
            tcex (TcEx, fixture): The tcex fixture.
        """
        try:
            tcex.playbook.exit(3)  # coverage
            assert False, 'Exit command did not trigger SystemExit'
        except SystemExit:
            pass

    def test_playbook_exit_no_code(self, tcex):
        """Test the create output method of Playbook module.

        Args:
            tcex (TcEx, fixture): The tcex fixture.
        """
        try:
            tcex.playbook.exit()  # coverage
            assert False, 'Exit command did not trigger SystemExit'
        except SystemExit:
            pass

    @pytest.mark.parametrize(
        'variable,value', [('#App:0001:s1!String', '1')],
    )
    def test_playbook_read_array(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # parse variable and send to create_output() method
        parsed_variable = tcex.playbook.parse_variable(variable)
        variable_name = parsed_variable.get('name')
        variable_type = parsed_variable.get('type')
        tcex.playbook.create_output(variable_name, value, variable_type)
        result = tcex.playbook.read_array(variable)
        assert result == [value], f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value', [('#App:0001:s1!String', '1')],
    )
    def test_playbook_read(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # parse variable and send to create_output() method
        parsed_variable = tcex.playbook.parse_variable(variable)
        variable_name = parsed_variable.get('name')
        variable_type = parsed_variable.get('type')
        tcex.playbook.create_output(variable_name, value, variable_type)
        result = tcex.playbook.read(variable, True)
        assert result == [value], f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    def test_playbook_read_none_array(self, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # parse variable and send to create_output() method
        result = tcex.playbook.read('#App:0001:none!String', True)
        assert result == [], f'result of ({result}) does not match ([])'

    def test_playbook_variable_types(self, tcex):
        """Test the playbooks variable types property.

        Args:
            tcex (TcEx, fixture): The tcex fixture.
        """
        assert len(tcex.playbook._variable_types) == 10

    @pytest.mark.parametrize(
        'variable,value,alt_variable,alt_value,expected',
        [
            ('#App:0001:s1!String', '1', '#App:0001:s2!String', '2', '1'),
            ('-- Select --', None, '#App:0001:s2!String', '2', None),
            ('-- Variable Input --', None, '#App:0001:s2!String', '2', '2'),
        ],
    )
    def test_playbook_read_choice(
        self, variable, value, alt_variable, alt_value, expected, playbook_app
    ):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex

        # parse variable and send to create_output() method
        if value is not None:
            parsed_variable = tcex.playbook.parse_variable(variable)
            variable_name = parsed_variable.get('name')
            variable_type = parsed_variable.get('type')
            tcex.playbook.create_output(variable_name, value, variable_type)

        # parse alt variable and send to create_output() method
        parsed_variable = tcex.playbook.parse_variable(alt_variable)
        variable_name = parsed_variable.get('name')
        variable_type = parsed_variable.get('type')
        tcex.playbook.create_output(variable_name, alt_value, variable_type)

        # read choice
        result = tcex.playbook.read_choice(variable, alt_variable)
        assert result == expected, f'result of ({result}) does not match ({expected})'

        # cleanup
        if value is not None:
            tcex.playbook.delete(variable)
            assert tcex.playbook.read(variable) is None
        if alt_value is not None:
            tcex.playbook.delete(alt_variable)
            assert tcex.playbook.read(alt_variable) is None
