"""ThreatConnect TI Campaign"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mappings.group import Group
from tcex.exit.error_codes import handle_error

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence import ThreatIntelligence


class Campaign(Group):
    """Unique API calls for Campaign API Endpoints

    Args:
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
        first_seen (str, kwargs): The first seen datetime expression for this Group.
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize Class Properties."""
        super().__init__(
            ti, sub_type='Campaign', api_entity='campaign', api_branch='campaigns', **kwargs
        )

    def first_seen(self, first_seen):
        """Update the campaign with the new first_seen date.

        Args:
            first_seen (str): The first_seen date. Converted to %Y-%m-%dT%H:%M:%SZ date format

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            handle_error(910, [self.type])

        # TODO [high] when datetime module is replaced, this must be updated.
        first_seen = self._utils.datetime.format_datetime(
            first_seen, date_format='%Y-%m-%dT%H:%M:%SZ'
        )
        self._data['firstSeen'] = first_seen
        request = {'firstSeen': first_seen}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)