# Copyright 2017 Open Source Robotics Foundation, Inc.
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

from xml.etree import ElementTree

from xmlschema import XMLSchemaValidationError
from xmlschema.core import etree_iselement
from xmlschema.resources import load_xml_resource


def load_xml(xml_document):

    try:
        xml_root = xml_document.getroot()
    except (AttributeError, TypeError):
        if etree_iselement(xml_document):
            xml_root = xml_document
        else:
            xml_root = load_xml_resource(xml_document)
    else:
        if not etree_iselement(xml_root):
            raise XMLSchemaTypeError(
                "wrong type %r for 'xml_document' argument." % type(xml_document)
            )
    return xml_root


def default_preprocessor(xsd_schema, xml_document, xml_document_defaults,
                         path=None, use_defaults=False):

    data = load_xml(xml_document)
    defaults_data = load_xml(xml_document_defaults)

    iter_decoder = xsd_schema.iter_decode(
        xml_document=xml_document,
        path=path,
        use_defaults=use_defaults,
        validation='lax')

    for chunk in iter_decoder:
        if isinstance(chunk, XMLSchemaValidationError):
            name = chunk.validator.name
            expected_reason = "tag '{name}' expected.".format(name=name)
            if chunk.reason == expected_reason:
                defaults_elem = defaults_data.find(name)
                if defaults_elem is not None:
                    # print('Default element found!')
                    # print('    ', 'name: ', name)
                    # print('    ', 'chunk.elem', chunk.elem)
                    # print('    ', 'defaults_elem: ', defaults_elem)
                    # print('    ', 'chunk.context.expected_index: ', chunk.context.expected_index)
                    chunk.elem.insert(chunk.context.expected_index, defaults_elem)
                    yield chunk
                    return
                else:
                    raise chunk
                    # # could create an empty element and expect user provided default children
                    # missing_elem = ElementTree.Element(name)
                    # print('No default found!')
                    # print('    ', 'name: ', name)
                    # print('    ', 'chunk.elem', chunk.elem)
                    # print('    ', 'missing_elem: ', missing_elem)
                    # print('    ', 'chunk.context.expected_index: ', chunk.context.expected_index)
                    # chunk.elem.insert(chunk.context.expected_index, missing_elem)
                    # yield chunk
                    # return
            else:
                raise chunk


def set_defaults(xsd_schema, data, defaults_data,
                filename=None, path=None, use_defaults=False):

    missing_error = True
    while missing_error:

        iter_errors = default_preprocessor(
            xsd_schema,
            data,
            defaults_data,
            path,
            use_defaults)

        missing_error = next(iter_errors, None)

    return data
