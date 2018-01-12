from ipaserver.plugins.idviews import (
        idoverrideuser, baseidoverride,
        resolve_object_to_anchor,
        DEFAULT_TRUST_VIEW_NAME,
        ANCHOR_REGEX,
        SID_ANCHOR_PREFIX)
from ipaserver.plugins.group import group, group_add_member
from ipalib.parameters import Str
from ipalib.text import _
from ipaserver.plugins.baseldap import add_missing_object_class
from ipapython.dn import DN

# First, allow objects of idoverrideuser type to be members of IPA groups
group.attribute_members['member'].append('idoverrideuser')
group.attribute_members['memberindirect'].append('idoverrideuser')

# Second, allow idoverrideuser objects to have nsMemberOf object class
# and to allow reading memberOf if it is there
idoverrideuser.possible_objectclasses.append('nsmemberof')
permission = idoverrideuser.managed_permissions['System: Read User ID Overrides']
permission['ipapermdefaultattr'].add('memberof')

# Third, allow adding nsMemberOf object class back to idoverrideuser objects
# in case they miss them to allow memberof plugin to propagate group membership
def idoverrideuser_pre_callback(self, ldap, dn, found, not_found,
                                *keys, **options):
    assert isinstance(dn, DN)
    if 'idoverrideuser' in options:
        for id in found['member']['idoverrideuser']:
            # new_dn = self.api.Object.idoverrideuser.get_dn(id, o)
            try:
                e = ldap.get_entry(id, ['*'])
            except errors.NotFound:
                # We are not adding an object here, only modifying existing one
                continue
            e = add_missing_object_class(ldap, 'nsmemberof',
                                         id, entry_attrs=e, update=True)
    return dn

# Fourth, register our pre-callback with group_add_member command
group_add_member.register_pre_callback(idoverrideuser_pre_callback)

# Finally, the most complex part: in a case we are dealing with a broken
# baseidoverride.get_dn() implementation, replace it with a correct version
# See https://pagure.io/freeipa/issue/7255 for details
# The code here relies on C Python code objects interface which should work
# for both Python 2.7 and Python 3
_co_names = baseidoverride.get_dn.__code__.co_names
if 'DEFAULT_TRUST_VIEW_NAME' not in _co_names:
    # baseidoverride.get_dn() cannot handle keys array with a single argument
    # so we have to replace it with a version that defaults
    # to DEFAULT_TRUST_VIEW_NAME as its ID View
    def baseidoverride_patched_get_dn(self, *keys, **options):
        # If user passed raw anchor, do not try
        # to translate it.
        if ANCHOR_REGEX.match(keys[-1]):
            anchor = keys[-1]

        # Otherwise, translate object into a
        # legitimate object anchor.
        else:
            anchor = resolve_object_to_anchor(
                self.backend,
                self.override_object,
                keys[-1],
                fallback_to_ldap=options.get('fallback_to_ldap', False)
            )
            if (len(keys[:-1]) == 0 and
                    self.override_object is 'user' and
                    anchor.startswith(SID_ANCHOR_PREFIX)):
                keys = (DEFAULT_TRUST_VIEW_NAME, ) + keys

        keys = keys[:-1] + (anchor, )
        return super(baseidoverride, self).get_dn(*keys, **options)

    baseidoverride.get_dn = baseidoverride_patched_get_dn

