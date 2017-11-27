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

"""Library for parsing keyage.xml and providing an object representation."""

# set version number
try:
    import pkg_resources
    try:
        __version__ = pkg_resources.require('keymint_package')[0].version
    except pkg_resources.DistributionNotFound:
        __version__ = 'unset'
    finally:
        del pkg_resources
except ImportError:
    __version__ = 'unset'

import os

PACKAGE_MANIFEST_FILENAME = 'keyage.xml'


def parse_package(path):
    """
    Parse package manifest.

    :param path: The path of the keyage.xml file, it may or may not
    include the filename

    :returns: return :class:`Package` instance, populated with parsed fields
    :raises: :exc:`InvalidPackage`
    :raises: :exc:`IOError`
    """
    import os

    from .exceptions import InvalidPackage

    if os.path.isfile(path):
        filename = path
    elif package_exists_at(path):
        filename = os.path.join(path, PACKAGE_MANIFEST_FILENAME)
        if not os.path.isfile(filename):
            raise IOError("Directory '%s' does not contain a '%s'" %
                          (path, PACKAGE_MANIFEST_FILENAME))
    else:
        raise IOError("Path '%s' is neither a directory containing a '%s' "
                      'file nor a file' % (path, PACKAGE_MANIFEST_FILENAME))

    with open(filename, 'r', encoding='utf-8') as f:
        try:
            return parse_package_string(f.read(), path, filename=filename)
        except InvalidPackage as e:
            e.args = [
                "Invalid package manifest '%s': %s" %
                (filename, e)]
            raise


def package_exists_at(path):
    """
    Check that a package exists at the given path.

    :param path: path to a package
    :type path: str
    :returns: True if package exists in given path, else False
    :rtype: bool
    """
    import os

    return os.path.isdir(path) and os.path.isfile(
        os.path.join(path, PACKAGE_MANIFEST_FILENAME))


def check_schema(schema, data, filename=None):
    from .exceptions import InvalidPackage
    if not schema.is_valid(data):
        try:
            schema.validate(data)
        except Exception as ex:
            if filename is not None:
                msg = "The manifest '%s' contains invalid XML:\n" % filename
            else:
                msg = 'The manifest contains invalid XML:\n'
            raise InvalidPackage(msg + str(ex))


def parse_package_string(data, path, *, filename=None):
    """
    Parse keyage.xml string contents.

    :param data: keyage.xml contents, ``str``
    :param filename: full file path for debugging, ``str``
    :returns: return parsed :class:`Package`
    :raises: :exc:`InvalidPackage`
    """
    import xmlschema
    import xml.etree.ElementTree as ElementTree

    # from .export import Export
    from .package import Package
    # from .person import Person
    # from .url import Url
    from .schemas import get_keyage_schema_path

    keyage_xsd_path = get_keyage_schema_path('keyage.xsd')
    keyage_schema = xmlschema.XMLSchema(keyage_xsd_path)

    check_schema(keyage_schema, data, filename)
    keyage_tree = ElementTree.ElementTree(ElementTree.fromstring(data))

    pkg = Package(filename=filename)
    pkg.string = data
    # pkg.dict = keyage_dict
    pkg.tree = keyage_tree

    root = keyage_tree.getroot()
    pkg.export = root.find('export')

    # format attribute
    value = root.get('format')
    pkg.package_format = int(value)
    assert pkg.package_format > 0, \
        ("Unable to handle '{filename}' format version '{format}', please update the "
         "manifest file to at least format version 1").format(
         filename=filename,
         format=pkg.package_format)
    assert pkg.package_format in [1], \
        ("Unable to handle '{filename}' format version '{format}', please update "
         "'keymint_package' (e.g. on Ubuntu/Debian use: sudo apt-get update && "
         'sudo apt-get install --only-upgrade python-keymint-package)').format(
         filename=filename,
         format=pkg.package_format)

    # name
    pkg.name = root.find('name').text

    permissions = root.find('permissions')
    if permissions is not None:
        permissions_xsd_path = get_keyage_schema_path('permissions.xsd')
        permissions_schema = xmlschema.XMLSchema(permissions_xsd_path)
        pkg.permissions = ElementTree.Element('permissions')
        for permission in permissions.findall('permission'):
            permission_path = os.path.join(path, permission.find('path').text)
            with open(permission_path, 'r') as f:
                permission_data = f.read()
            check_schema(permissions_schema, permission_data, permission_path)
            permission_root = ElementTree.fromstring(permission_data)
            permission_grants = permission_root.findall('permissions/grant')
            pkg.permissions.extend(permission_grants)
        pkg.permissions_ca = permissions.find('issuer_name')

    governances = root.find('governances')
    if governances is not None:
        governance_xsd_path = get_keyage_schema_path('governance.xsd')
        governance_schema = xmlschema.XMLSchema(governance_xsd_path)
        pkg.governance = ElementTree.Element('domain_access_rules')
        for governance in governances.findall('governance'):
            governance_path = os.path.join(path, governance.find('path').text)
            with open(governance_path, 'r') as f:
                governance_data = f.read()
            check_schema(governance_schema, governance_data, governance_path)
            governance_root = ElementTree.fromstring(governance_data)
            governance_domain_rules = governance_root.findall('domain_access_rules/domain_rule')
            pkg.governance.extend(governance_domain_rules)
        pkg.governance_ca = governances.find('issuer_name')

    identities = root.find('identities')
    if identities is not None:
        identities_xsd_path = get_keyage_schema_path('identities.xsd')
        identities_schema = xmlschema.XMLSchema(identities_xsd_path)
        pkg.identities = ElementTree.Element('identities')
        for identity in identities.findall('identity'):
            identity_path = os.path.join(path, identity.find('path').text)
            with open(identity_path, 'r') as f:
                identity_data = f.read()
            check_schema(identities_schema, identity_data, identity_path)
            identity_root = ElementTree.fromstring(identity_data)
            identity_elemts = identity_root.findall('identities/identity')
            pkg.identities.extend(identity_elemts)

    # version
    pkg.version = root.findtext('version')

    # description
    pkg.description = root.findtext('description')

    pkg.validate()

    return pkg
