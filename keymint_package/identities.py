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

import os

import xml.etree.ElementTree as ElementTree

from copy import deepcopy

import xmlschema

from .exceptions import InvalidPermissionsXML
from .namespace import DDSNamespaceHelper
from .templates import get_dds_template_path


from cryptography import hazmat, x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import asymmetric
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes


class CertificateHelper:
    """Help build certificate into artifacts."""

    def __init__(self):
        pass


class DDSCertificateHelper:
    """Help build certificate into artifacts."""

    def build_csr(self, context, csr, dds_key):
        # TODO use data in csr xml element to provide subject name
        hash_algorithm = getattr(hashes, csr.find('hash_algorithm').text)
        dds_csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
            # Provide various details about who we are.
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
            x509.NameAttribute(NameOID.COMMON_NAME, u"mysite.com"),
            ])).add_extension(
                x509.SubjectAlternativeName([
                    # Describe what sites we want this certificate for.
                    x509.DNSName(u"mysite.com"),
                    x509.DNSName(u"www.mysite.com"),
                    x509.DNSName(u"subdomain.mysite.com"),
                    ]),
            critical=False,
            # Sign the CSR with our private key.
            ).sign(dds_key, hash_algorithm(), default_backend())
        return dds_csr

    def serialize(self, context, cert, dds_certificate):
        dds_certificate_bytes = dds_certificate.public_bytes(
                encoding=serialization.Encoding.PEM)
        return dds_certificate_bytes

class AsymmetricHelper:
    """Help build key into artifacts."""

    def __init__(self):
        pass


class DDSAsymmetricHelper(AsymmetricHelper):
    """Help build asymmetric keys into artifacts."""

    def serialize(self, context, key, dds_key):
        encryption_algorithm = key.find('encryption_algorithm').text
        if encryption_algorithm == 'NoEncryption':
            encryption_algorithm = serialization.NoEncryption()
        else:
            password = bytes(os.environ[key.find('password_env').text], 'utf-8')
            encryption_algorithm = getattr(serialization, encryption_algorithm)(password)

        dds_key_bytes = dds_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=encryption_algorithm)
        return dds_key_bytes

    def rsa(self, context, asymmetric_type):
        dds_key = asymmetric.rsa.generate_private_key(
            public_exponent=65537,
            key_size=int(asymmetric_type.find('key_size').text),
            backend=default_backend())
        return dds_key

    def dsa(self, context, asymmetric_type):
        dds_key = asymmetric.dsa.generate_private_key(
            key_size=int(asymmetric_type.find('key_size').text),
            backend=default_backend())
        return dds_key

    def ec(self, context, asymmetric_type):
        dds_key = asymmetric.ec.generate_private_key(
            curve=getattr(asymmetric.ec, asymmetric_type.find('curve').text)(),
            backend=default_backend())
        return dds_key


class IdentitiesHelper:
    """Help build identities into artifacts."""

    def __init__(self):
        pass

    def build(self, context):
        raise NotImplementedError


class DDSIdentitiesHelper(IdentitiesHelper):
    """Help build identities into artifacts."""

    def __init__(self):
        self.dds_asymmetric_helper = DDSAsymmetricHelper()
        self.dds_certificate_helper = DDSCertificateHelper()

    def _build_key(self, context, key):
        asymmetric_types = key.find('asymmetric_type')
        asymmetric_type = asymmetric_types.getchildren()[0]
        generator = getattr(self.dds_asymmetric_helper, asymmetric_type.tag)
        dds_key = generator(context, asymmetric_type)
        return dds_key

    def _build_csr(self, context, csr, dds_key):
        dds_csr = self.dds_certificate_helper.build_csr(context, csr, dds_key)
        return dds_csr

    def _build_identity(self, context, identity):

        dds_identity = {}
        dds_identity['name'] = identity.get('name')

        key = identity.find('key')
        dds_key = self._build_key(context, key)
        dds_key_bytes = self.dds_asymmetric_helper.serialize(context, key, dds_key)

        csr = identity.find('cert')
        dds_csr = self._build_csr(context, csr, dds_key)
        dds_csr_bytes = self.dds_certificate_helper.serialize(context, csr, dds_csr)

        dds_identity['dds_key'] = {'object': dds_key, 'bytes': dds_key_bytes}
        dds_identity['dds_csr'] = {'object': dds_csr, 'bytes': dds_csr_bytes}

        return dds_identity

    def build(self, context):
        identities = deepcopy(context.package_manifest.identities)
        dds_identities = []

        for identity in identities.findall('identity'):
            dds_identity = self._build_identity(context, identity)
            dds_identities.append(dds_identity)

        return dds_identities

    # def test(self, dds_root_str, filename):
    #     permissions_xsd_path = get_dds_template_path('permissions.xsd')
    #     permissions_schema = xmlschema.XMLSchema(permissions_xsd_path)
    #     if not permissions_schema.is_valid(dds_root_str):
    #         try:
    #             permissions_schema.validate(dds_root_str)
    #         except Exception as ex:
    #             if filename is not None:
    #                 msg = "The permissions file '%s' contains invalid XML:\n" % filename
    #             else:
    #                 msg = 'The permissions file contains invalid XML:\n'
    #             raise InvalidPermissionsXML(msg + str(ex))
