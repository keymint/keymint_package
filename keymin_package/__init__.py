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
            return parse_package_string(f.read(), filename=filename)
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


def parse_package_string(data, *, filename=None):
    """
    Parse keyage.xml string contents.

    :param data: keyage.xml contents, ``str``
    :param filename: full file path for debugging, ``str``
    :returns: return parsed :class:`Package`
    :raises: :exc:`InvalidPackage`
    """
    from attrdict import AttrDict
    from copy import deepcopy
    import xmlschema

    from .exceptions import InvalidPackage
    # from .export import Export
    from .package import Package
    # from .person import Person
    # from .url import Url
    from .templates import get_keyage_template_path

    keyage_xsd_path = get_keyage_template_path('keyage.xsd')
    keyage_schema = xmlschema.XMLSchema(keyage_xsd_path)

    if not keyage_schema.is_valid(data):
        try:
            keyage_schema.validate(data)
        except Exception as ex:
            if filename is not None:
                msg = "The manifest '%s' contains invalid XML:\n" % filename
            else:
                msg = 'The manifest contains invalid XML:\n'
            raise InvalidPackage(msg + str(ex))
    else:
        keyage_dict = keyage_schema.to_dict(data)

    pkg = Package(filename=filename)
    pkg.string = data
    pkg.dict = keyage_dict
    pkg.permissions = AttrDict(deepcopy(keyage_dict['permissions']))


# format attribute
    value = keyage_dict['@format']
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
    # pkg.name = _get_node_value(_get_node(root, 'name'))

    # version
    # version_node = _get_node(root, 'version')
    # pkg.version = _get_node_value(version_node)

    # description
    # pkg.description = _get_node_value(
    #     _get_node(root, 'description'), allow_xml=True, apply_str=False)

    # at least one maintainer, all must have email
    # maintainers = _get_nodes(root, 'maintainer')
    # for node in maintainers:
    #     pkg.maintainers.append(Person(
    #         _get_node_value(node, apply_str=False),
    #         email=_get_node_attr(node, 'email')))

    # urls with optional type
    # urls = _get_nodes(root, 'url')
    # for node in urls:
    #     pkg.urls.append(Url(
    #         _get_node_value(node),
    #         url_type=_get_node_attr(node, 'type', default='website')))

    # authors with optional email
    # authors = _get_nodes(root, 'author')
    # for node in authors:
    #     pkg.authors.append(Person(
    #         _get_node_value(node, apply_str=False),
    #         email=_get_node_attr(node, 'email', default=None)))

    # at least one license
    # licenses = _get_nodes(root, 'license')
    # for node in licenses:
    #     pkg.licenses.append(_get_node_value(node))

    pkg.validate()

    return pkg
