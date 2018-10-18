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

from xml.etree import cElementTree as ElementTree

from xmlschema import XMLSchemaValidationError
from xmlschema.etree import is_etree_element
from xmlschema.resources import load_xml_resource

from .utils import pretty_xml

def load_xml(xml_document):

    try:
        xml_root = xml_document.getroot()
    except (AttributeError, TypeError):
        if is_etree_element(xml_document):
            xml_root = xml_document
        else:
            xml_root = load_xml_resource(xml_document)
    else:
        if not is_etree_element(xml_root):
            raise XMLSchemaTypeError(
                "wrong type %r for 'xml_document' argument." % type(xml_document)
            )
    return xml_root


def default_preprocessor(xsd_schema, xml_document, xml_document_defaults,
                         path=None, use_defaults=False):

    data = load_xml(xml_document)
    defaults_data = load_xml(xml_document_defaults)

    iter_decoder = xsd_schema.iter_decode(
        source=data,
        path=path,
        use_defaults=use_defaults,
        validation='lax')

    for chunk in iter_decoder:
        if isinstance(chunk, XMLSchemaValidationError):
            if chunk.reason.startswith("The content of element ") or \
               chunk.reason.startswith("Unexpected child with tag "):
                expecteds = chunk.expected
                if expecteds:
                    if not isinstance(expecteds, (list, tuple)):
                        expecteds = [expecteds]
                    for i, expected in enumerate(expecteds):
                        index = chunk.index + i
                        default_elem = defaults_data.find(expected.tag)
                        if default_elem is not None:
                            chunk.elem.insert(index, default_elem)
                            yield chunk
                            return
                        else:
                            missing_elem = ElementTree.Element(expected.tag)
                            chunk.elem.insert(index, missing_elem)
                            yield chunk
                            return
                else:
                    print("##########")
                    print("chunk.reason")
                    print(chunk.reason)
                    print("chunk.message")
                    print(vars(chunk))
                    print("chunk.elem")
                    print(pretty_xml(chunk.elem))
                    print("##########")
                    raise chunk
            elif chunk.reason.startswith("invalid literal for"):
                expected = chunk.elem.tag
                default_elem = defaults_data.find(expected)
                chunk.elem.text = default_elem.text
                yield chunk
                return
            else:
                # TODO: raise an informative error to user
                print("##########")
                print("chunk.reason")
                print(chunk.reason)
                print("chunk.message")
                print(vars(chunk))
                print("chunk.elem")
                print(pretty_xml(chunk.elem))
                print("##########")
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
