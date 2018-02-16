<?xml version="1.0" encoding="UTF-8"?>
<package xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="http://example.com/ns/collection/keyage.xsd"
    format="1">
    <name>@pkg_name</name>
    <permissions format="@package_type">
        <issuer_name>permissions_ca</issuer_name>
        <permission>
          <permission_path>permissions.xml</permission_path>
          <defaults_path>package.defaults/permissions.xml</defaults_path>
        </permission>
    </permissions>
    <governances format="@package_type">
        <issuer_name>permissions_ca</issuer_name>
        <governance>
          <governance_path>governance.xml</governance_path>
          <defaults_path>package.defaults/governance.xml</defaults_path>
        </governance>
    </governances>
    <identities format="@package_type">
        <identity>
          <identity_path>identities.xml</identity_path>
          <defaults_path>package.defaults/identities.xml</defaults_path>
        </identity>
    </identities>
    <export>
        <build_type>@package_type</build_type>
    </export>
</package>
