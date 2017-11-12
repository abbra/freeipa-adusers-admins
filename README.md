# A proof-of-concept plugin to support Active Directory users as members of FreeIPA groups

This plugin for FreeIPA allows to add Active Directory users as members of
FreeIPA groups.  As result, Active Directory users can manage FreeIPA resources
if these groups are part of appropriate roles. For example, adding an Active
Directory user as a member of 'admins' group would make it equivalent to
built-in FreeIPA 'admin' user.

The plugin works by allowing user ID overrides from the `Default Trust View` in FreeIPA
to be members of IdM groups. User ID overrides in the `Default Trust View` can only be
created for Active Directory users. When Active Directory user authenticates
with GSSAPI against the FreeIPA LDAP server, its Kerberos principal is
automatically mapped to the user's ID override in the `Default Trust View`.
LDAP server's access control plugin uses membership information of the
corresponding LDAP entry to decide how access can be allowed.

Note that we consider this approach as an interim solution. A proper solution
is to make sure actual group membership of a user from its Kerberos ticket is
used to consider membership in the LDAP groups.  This approach requires a
number of changes, in 389-ds LDAP server and in Cyrus-SASL library, to allow
dynamic discovery of the group information as supplied by a KDC in MS-PAC
structure (part of a Kerberos ticket). These changes are particularly invasive
but allow to re-use so-called `external groups` and external group members
already defined in FreeIPA.

[See plugin/Feature.mediawiki](plugin/Feature.mediawiki) for detailed explanation.

