# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import xml.etree.ElementTree as ElementTree

from pprint import pprint
from xml.dom import minidom
from attrdict import AttrDict

import xmlschema

from .templates import get_dds_template_path

# from copy import deepcopy


class PermissionsHelper:
    """Interprite the permission into artifacts."""

    def __init__(self):
        pass

    def interprite(self, context):
        raise NotImplementedError


class DDSPermissionsHelper(PermissionsHelper):
    """Help interprite permission into artifacts."""

    def __init__(self):
        self.namespaces = {
            'xmlns:xsi':
                'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:noNamespaceSchemaLocation':
                'http://www.omg.org/spec/DDS-Security/20160303/omg_shared_ca_permissions.xsd',
        }
        permissions_xsd_path = get_dds_template_path('permissions.xsd')
        self.permissions_schema = xmlschema.XMLSchema(permissions_xsd_path)

    def interprite(self, context):
        dds_permissions_data = AttrDict()
        dds_permissions_data.dds
        context.pkg.permissions

        elem = self.permissions_schema.to_etree(
            data=dds_permissions_data,
            path='./dds',
            namespaces=self.namespaces)
        xmlstr = minidom.parseString(ElementTree.tostring(elem)).toprettyxml(indent="   ")
        pprint(xmlstr)
