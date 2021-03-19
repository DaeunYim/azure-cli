# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from ..generated._client_factory import cf_ssh_public_key

    vm_ssh_public_key = CliCommandType(
        operations_tmpl='azure.mgmt.compute.operations._ssh_public_keys_operations#SshPublicKeysOperations.{}',
        client_factory=cf_ssh_public_key,
    )
    with self.command_group('sshkey', vm_ssh_public_key, client_factory=cf_ssh_public_key) as g:
        g.custom_command('create', 'sshkey_create')
