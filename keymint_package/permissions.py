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

from copy import deepcopy

# import xmlschema

from .exceptions import InvalidPermissionsXML
from .namespace import DDSNamespaceHelper
# from .templates import get_dds_template_path


from .utils import pretty_xml, tidy_xml


class CriteriasHelpter:
    """Help build criteria into artifacts."""

    def __init__(self):
        pass


class DDSCriteriasHelper(CriteriasHelpter):
    """Help build permission into artifacts."""

    _dds_expression_list_types = ['partitions', 'data_tags']

    def __init__(self):
        self.dds_namespaces_helper = DDSNamespaceHelper()

    def _dds_expressions(self, dds_criteria, dds_criterias):
        for dds_criteria in dds_criterias:
            dds_criteria.append(expression_list)

    def topics(self, expression_list):
        topics = ElementTree.Element('topics')
        for expression in expression_list.getchildren():
            topic = ElementTree.Element('topic')
            formater = getattr(self.dds_namespaces_helper, expression.tag)
            topic.text = formater(expression.text)
            topics.append(topic)
        return topics

    def ros_publish(self, context, criteria):
        dds_publish = ElementTree.Element('publish')
        dds_criterias = []
        dds_criterias.append(dds_publish)
        for expression_list in criteria.getchildren():
            if expression_list.tag in self._dds_expression_list_types:
                self._dds_expressions(dds_criteria, dds_criterias)
                continue
            else:
                formater = getattr(self, expression_list.tag)
                expression_list = formater(expression_list)
                dds_publish.append(expression_list)
        return dds_criterias

    def ros_subscribe(self, context, criteria):
        dds_subscribe = ElementTree.Element('subscribe')
        dds_criterias = []
        dds_criterias.append(dds_subscribe)
        for expression_list in criteria.getchildren():
            if expression_list.tag in self._dds_expression_list_types:
                self._dds_expressions(dds_criteria, dds_criterias)
                continue
            else:
                formater = getattr(self, expression_list.tag)
                expression_list = formater(expression_list)
                dds_subscribe.append(expression_list)
        return dds_criterias

    def ros_call(self, context, criteria):
        # TODO
        return []

    def ros_execute(self, context, criteria):
        # TODO
        return []

    def ros_request(self, context, criteria):
        # TODO
        return []

    def ros_operate(self, context, criteria):
        # TODO
        return []

    def ros_read(self, context, criteria):
        # TODO
        return []

    def ros_write(self, context, criteria):
        # TODO
        return []


class PermissionsHelper:
    """Help build permission into artifacts."""

    def __init__(self):
        pass

    def build(self, context):
        raise NotImplementedError


class DDSPermissionsHelper(PermissionsHelper):
    """Help build permission into artifacts."""

    _dds_criteria_types = ['publish', 'subscribe', 'relay']

    def __init__(self):
        self.dds_criterias_helper = DDSCriteriasHelper()
        # self.namespaces = {
        #     'xmlns:xsi':
        #         'http://www.w3.org/2001/XMLSchema-instance',
        #     'xsi:noNamespaceSchemaLocation':
        #         'http://www.omg.org/spec/DDS-Security/20160303/omg_shared_ca_permissions.xsd',
        # }
        # permissions_xsd_path = get_dds_template_path('permissions.xsd')
        # self.permissions_schema = xmlschema.XMLSchema(permissions_xsd_path)

    def _build_criterias(self, context, criteria):
        formater = getattr(self.dds_criterias_helper, criteria.tag)
        return formater(context, criteria)

    def _build_rule(self, context, rule):
        dds_rule = ElementTree.Element(rule.tag)

        domains = rule.find('domains')
        if domains is not None:
            dds_rule.append(domains)
            rule.remove(domains)

        for criteria in rule.getchildren():
            if criteria.tag in self._dds_criteria_types:
                dds_rule.append(criteria)
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

        default = grant.find('default')
        if default is not None:
            grant.remove(default)

        for rule in grant.getchildren():
            dds_rule = self._build_rule(context, rule)
            dds_grant.append(dds_rule)

        if default is not None:
            dds_grant.append(default)

        return dds_grant

    def build(self, context):
        permissions = deepcopy(context.package_manifest.permissions)
        dds_permissions = ElementTree.Element('permissions')

        for grant in permissions.findall('grant'):
            dds_grant = self._build_grant(context, grant)
            dds_permissions.append(dds_grant)

        dds_root = ElementTree.Element('dds')
        dds_root.append(dds_permissions)
        dds_root = tidy_xml(dds_root)
        return pretty_xml(dds_root)

    def test(self, dds_root_str, filename):
        permissions_xsd_path = get_dds_template_path('permissions.xsd')
        permissions_schema = xmlschema.XMLSchema(permissions_xsd_path)
        if not permissions_schema.is_valid(dds_root_str):
            try:
                permissions_schema.validate(dds_root_str)
            except Exception as ex:
                if filename is not None:
                    msg = "The permissions file '%s' contains invalid XML:\n" % filename
                else:
                    msg = 'The permissions file contains invalid XML:\n'
                raise InvalidPermissionsXML(msg + str(ex))
