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
from collections import OrderedDict
from copy import deepcopy

import xmlschema

from .templates import get_dds_template_path


def tidy_xml(element):
    subiter = ElementTree.ElementTree(element).getiterator()
    for x in subiter:
        if x.text:
            x.text = x.text.strip()
        if x.tail:
            x.tail = x.tail.strip()
    return element


def pretty_xml(element):
    xmlstr = ElementTree.tostring(element, encoding='unicode', method='xml')
    xmlstr = minidom.parseString(xmlstr).toprettyxml(indent='    ', newl='\n', encoding='utf-8')
    return xmlstr.decode('utf-8')


class PermissionsHelper:
    """Interprite the permission into artifacts."""

    def __init__(self):
        pass

    def build(self, context):
        raise NotImplementedError


class DDSPermissionsHelper(PermissionsHelper):
    """Help interprite permission into artifacts."""

    def __init__(self):
        pass
        # self.namespaces = {
        #     'xmlns:xsi':
        #         'http://www.w3.org/2001/XMLSchema-instance',
        #     'xsi:noNamespaceSchemaLocation':
        #         'http://www.omg.org/spec/DDS-Security/20160303/omg_shared_ca_permissions.xsd',
        # }
        # permissions_xsd_path = get_dds_template_path('permissions.xsd')
        # self.permissions_schema = xmlschema.XMLSchema(permissions_xsd_path)

    def _build_criterias(self, context, criteria):
        # TODO
        dds_criterias = []
        if criteria.tag == 'ros_publish':
            dds_publish = ElementTree.Element('publish')
            dds_criterias.append(dds_publish)
            # dds_subscribe = ElementTree.Element('subscribe')
            # dds_relay = ElementTree.Element('relay')

            for expression_list in criteria.getchildren():

                if expression_list.tag in ['partitions', 'data_tags']:
                    for dds_criteria in dds_criterias:
                        dds_criteria.append(expression_list)
                    continue
                else:
                    # TODO expand
                    expression_list.tag = 'topics'
                    dds_publish.append(expression_list)
                    dds_criterias.append(dds_publish)
                    # dds_topic_expression_list = ElementTree.Element('topics')
                    # dds_topic_expression_list = ElementTree.Element('partitions')
                    # dds_topic_expression_list = ElementTree.Element('data_tags')
        return dds_criterias

    def _build_rule(self, context, rule):
        dds_rule = ElementTree.Element(rule.tag)

        domains = rule.find('domains')
        if domains is not None:
            dds_rule.append(domains)
            rule.remove(domains)

        for criteria in rule.getchildren():
            if criteria.tag == 'publish':
                dds_rule.append(criteria)
                continue
            elif criteria.tag == 'subscribe':
                dds_rule.append(criteria)
                continue
            elif criteria.tag == 'relay':
                dds_rule.append(criteria)
                continue
            else:
                dds_criterias = self._build_criterias(context, criteria)
                dds_rule.extend(dds_criterias)
        return dds_rule

    def _build_grant(self, context, grant):

        dds_grant = ElementTree.Element('grant')

        name = grant.get('name')
        dds_grant.set('name', name)

        subject_name = grant.find('subject_name')
        if subject_name is not None:
            dds_grant.append(subject_name)
            grant.remove(subject_name)

        validity = grant.find('validity')
        if validity is not None:
            dds_grant.append(validity)
            grant.remove(validity)

        for rule in grant.getchildren():
            dds_rule = self._build_rule(context, rule)
            dds_grant.append(dds_rule)

        default = grant.find('default')
        if default is not None:
            dds_grant.append(default)
            grant.remove(default)

        return dds_grant

    def build(self, context):
        permissions = deepcopy(context.package_manifest.permissions)
        dds_permissions = ElementTree.Element('permissions')

        for grant in permissions.findall('grant'):
            dds_grant = self._build_grant(context, grant)
            dds_permissions.append(dds_grant)

        dds_permissions = tidy_xml(dds_permissions)
        xmlstr = pretty_xml(dds_permissions)
        print(xmlstr)
