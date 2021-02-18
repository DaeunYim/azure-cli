# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pytest
from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (
    JMESPathCheck,
    NoneCheck,
    ResourceGroupPreparer,
    ScenarioTest,
    StringContainCheck,
    VirtualNetworkPreparer,
    LocalContextScenarioTest,
    live_only)
from azure.cli.testsdk.preparers import (
    AbstractPreparer,
    SingleValueReplacer)
from .test_rdbms_flexible_commands_local_context import (
    ServerPreparer,
    FlexibleServerLocalContextScenarioTest
)
from .conftest import postgres_location

#Local context test is separated out from the rest of the test due to daily pipeline run issue
@pytest.fixture(autouse=True, scope='class')
def postgres_location(request):
    request.cls.postgres_location = request.config.getoption("--postgres-location")

@pytest.mark.usefixtures("postgres_location")
class PostgresFlexibleServerLocalContextScenarioTest(FlexibleServerLocalContextScenarioTest):
    
    @AllowLargeResponse()
    @ResourceGroupPreparer(location=postgres_location)
    def test_postgres_flexible_server_local_context(self, resource_group):
        self._test_flexible_server_local_context('postgres', resource_group)
