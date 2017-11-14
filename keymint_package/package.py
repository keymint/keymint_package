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

import re

from .exceptions import InvalidPackage


class Package:
    """Object representation of a package manifest file."""

    __slots__ = [
        'package_format',
        'name',
        'version',
        'description',
        'maintainers',
        'licenses',
        'urls',
        'authors',
        'permissions',
        'identity',
        'governance',
        'string',
        'dict',
        'tree',
        'export',
        'filename',
    ]

    def __init__(self, *, filename=None, **kwargs):
        """
        Constructor.

        :param filename: location of keyage.xml.  Necessary if
        converting ``${prefix}`` in ``<export>`` values, ``str``.
        """
        # initialize all slots ending with "s" with lists
        # all other with plain values
        for attr in self.__slots__:
            value = kwargs[attr] if attr in kwargs else None
            setattr(self, attr, value)
        self.filename = filename
        # verify that no unknown keywords are passed
        unknown = set(kwargs.keys()).difference(self.__slots__)
        if unknown:
            raise TypeError('Unknown properties: %s' % ', '.join(unknown))

    def __iter__(self):
        for slot in self.__slots__:
            yield slot

    def __str__(self):
        data = {}
        for attr in self.__slots__:
            data[attr] = getattr(self, attr)
        return str(data)

    def get_build_type(self):
        """
        Return value of export/build_type element, or 'unknown' if unspecified.

        :returns: package build type
        :rtype: str
        :raises: :exc:`InvalidPackage`
        """
        build_type_exports = self.export.findall('build_type')
        if len(build_type_exports) == 1:
            return build_type_exports[0].text
        raise InvalidPackage('Only one <build_type> element is permitted.')

    def validate(self):
        """
        Ensure that all standards for packages are met.

        :raises InvalidPackage: in case validation fails
        """
        errors = []
        if self.package_format:
            if not re.match('^[1-9][0-9]*$', str(self.package_format)):
                errors.append("The 'format' attribute of the package must "
                              'contain a positive integer if present')

        if not self.name:
            errors.append('Package name must not be empty')
        # Must start with a lower case alphabetic character.
        # Allow lower case alphanummeric characters and underscores in
        # keymint packages.
        valid_package_name_regexp = '([^/ ]+/*)+(?<!/)'
        build_type = self.get_build_type()
        if not build_type.startswith('keymint'):
            # Dashes are allowed for other build_types.
            valid_package_name_regexp = '^[a-z][a-z0-9_-]*$'
        if not re.match(valid_package_name_regexp, self.name):
            errors.append("Package name '%s' does not follow naming "
                          'conventions' % self.name)

        if self.version:
            # errors.append('Package version must not be empty')
            if not re.match('^[0-9]+\.[0-9_]+\.[0-9_]+$', self.version):
                errors.append("Package version '%s' does not follow version "
                              'conventions' % self.version)

        # if not self.description:
        #     errors.append('Package description must not be empty')

        if self.maintainers is not None:
            # if not self.maintainers:
            #     errors.append('Package must declare at least one maintainer')
            for maintainer in self.maintainers:
                try:
                    maintainer.validate()
                except InvalidPackage as e:
                    errors.append(str(e))
                if not maintainer.email:
                    errors.append('Maintainers must have an email address')

        # if not self.licenses:
        #     errors.append('The package node must contain at least one '
        #                   "'license' tag")

        if self.authors is not None:
            for author in self.authors:
                try:
                    author.validate()
                except InvalidPackage as e:
                    errors.append(str(e))

        if errors:
            raise InvalidPackage('\n'.join(errors))
