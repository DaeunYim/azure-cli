import time

from datetime import datetime
from time import sleep
from dateutil.tz import tzutc   # pylint: disable=import-error
from azure_devtools.scenario_tests import AllowLargeResponse
from msrestazure.azure_exceptions import CloudError
from azure.cli.core.local_context import AzCLILocalContext, ALL, LOCAL_CONTEXT_FILE
from azure.cli.core.util import CLIError
from azure.cli.core.util import parse_proxy_resource_id
from azure.cli.testsdk.base import execute
from azure.cli.testsdk.exceptions import CliTestError   # pylint: disable=unused-import
from azure.cli.testsdk import (
    JMESPathCheck,
    NoneCheck,
    ResourceGroupPreparer,
    ScenarioTest,
    live_only)
from azure.cli.testsdk.preparers import (
    AbstractPreparer,
    SingleValueReplacer)


# Constants
SERVER_NAME_PREFIX = 'azuredbclitest-'
SERVER_NAME_MAX_LENGTH = 63
GROUP_NAME_PREFIX = 'azuredbclitest-'
GROUP_NAME_MAX_LENGTH = 20

class FlexibleServerMgmtScenarioTest(ScenarioTest):

    def _remove_resource_group(self, resource_group_name):
        self.cmd(self.cli_ctx, 'az group delete --name {} --yes --no-wait'.format(resource_group_name))
    
    def _remove_server(self, database_engine, resource_group_name, server_name):
        self.cmd(self.cli_ctx, 'az {} flexible-server delete -g {} -n {} --yes --no-wait'.format(database_engine, resource_group_name, server_name))
    
    @AllowLargeResponse()
    def test_postgres_flexible_server_mgmt(self):
        self._test_flexible_server_mgmt('postgres')
    
    @AllowLargeResponse()
    def test_mysql_flexible_server_mgmt(self):
        self._test_flexible_server_mgmt('mysql')

    def _test_flexible_server_mgmt(self, database_engine):

        if not self.cli_ctx.local_context.is_on:
            self.cmd('local-context on')
        
        # 1. test flexible-server create
        # 1-1) Auto-generate
        try:
            auto_generated_output = self.cmd('{} flexible-server create'.format(database_engine)).get_output_in_json()
            self.assertIn('name', auto_generated_output)
            self.assertIn('resourceGroup', auto_generated_output)
            self.assertIn('location', auto_generated_output)
            self.assertIn('administratorLogin', auto_generated_output)
        except:
            self._remove_resource_group(resource_group_name)
        finally:
            resource_group_name = self.cli_ctx.local_context.get('all', 'server_name')
            location = self.cli_ctx.local_context.get('all', 'location')
            server_name = self.cli_ctx.local_context.get(database_engine + ' flexible-server', 'server_name')
            self._remove_server(database_engine, resource_group_name, server_name)
            

        # 1-2) rg, location local context, autogenerate the rest
        try:
            local_context_generated_output = self.cmd('{} flexible-server create'.format(database_engine),\
                checks=[JMESPathCheck('resourceGroup', resource_group_name), JMESPathCheck('location', location)]).get_output_in_json()
        except:
            self._remove_resource_group(resource_group_name)
        finally:
            server_name = self.cli_ctx.local_context.get(database_engine + ' flexible-server', 'server_name')
            self._remove_server(database_engine, resource_group_name, server_name)

        # 1-3) user input generate
        server_name = self.create_random_name(SERVER_NAME_PREFIX, SERVER_NAME_MAX_LENGTH)
        admin_user = 'cloudsa'
        admin_password = 'SecretPassword123'
        cu = 2; family = 'Gen5'
        skuname = 'Standard_D4s_v3' 
        loc = 'eastus2'

        list_checks = [JMESPathCheck('name', server_name),
                       JMESPathCheck('resourceGroup', resource_group_name),
                       JMESPathCheck('administratorLogin', admin_user),
                       JMESPathCheck('sslEnforcement', 'Enabled'),
                       JMESPathCheck('location', loc)]
        
        try:
            self.cmd('{} flexible-server create -g {} --name {} --admin-user {} --admin-password {} --sku-name {}'
                    .format(database_engine, resource_group_name, server_name, admin_user, admin_password, skuname),
                    checks=list_checks)
        except:
            self._remove_resource_group(resource_group_name)
        finally:
            self._remove_server(database_engine, resource_group, server_name)

        
        # 1-4) flexible-server create failure
        admin_user = 'root'
        self.cmd('{} flexible-server create -g {} --admin-user {}'.format(database_engine, resource_group, admin_user),
                 checks=list_checks, expect_failure=True)
        
        self._remove_resource_group(resource_group_name)