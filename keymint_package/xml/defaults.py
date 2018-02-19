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
from xmlschema.etree import etree_iselement
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
        xml_document=data,
        path=path,
        use_defaults=use_defaults,
        validation='lax')

    for chunk in iter_decoder:
        if isinstance(chunk, XMLSchemaValidationError):
            if chunk.reason.startswith("The child n.") or \
               chunk.reason.startswith("The content of element '"):
                expecteds = chunk.expected
                if expecteds:
                    if not isinstance(expecteds, (list, tuple)):
                        expecteds = [expecteds]
                    for i, expected in enumerate(expecteds):
                        index = chunk.index + i
                        default_elem = defaults_data.find(expected)
                        if default_elem is not None:
                            chunk.elem.insert(index, default_elem)
                            yield chunk
                            return
                        else:
                            missing_elem = ElementTree.Element(expected)
                            chunk.elem.insert(index, missing_elem)
                            yield chunk
                            return
                else:
                    raise chunk
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