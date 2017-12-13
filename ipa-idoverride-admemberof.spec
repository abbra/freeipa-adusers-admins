%global debug_package %{nil}
%define plugin_name idoverride-admemberof

Name:           ipa-%{plugin_name}-plugin
Version:        0.0.1
Release:        1%{?dist}
Summary:        RHEL IdM plugin to allow AD users to be members of IdM groups for management purposes

License:        GPL
URL:            https://github.com/abbra/freeipa-userstatus-plugin
Source0:        %{name}-%{version}.tar.gz

%if 0%{?fedora} > 26 || 0%{?rhel} > 7
BuildRequires: python3-devel
%else
BuildRequires:  python2-devel
%endif

Requires:       ipa-server-common >= 4.5
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
BuildRequires: python3-ipaserver >= 4.6.0
%else
BuildRequires:  python2-ipaserver >= 4.5
%endif

%description
This plugin adds an experimental support to RHEL IdM to allow
Active Directory users to be members of IdM groups. As result,
AD users can manage IdM resources if they are allowed to do so
by roles their groups are part of.

%prep
%autosetup

%build
touch debugfiles.list

%install
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
ipa_python_sitelib=%{python3_sitelib}
%else
ipa_python_sitelib=%{python2_sitelib}
%endif

rm -rf $RPM_BUILD_ROOT
#%%__mkdir_p %buildroot/%{ipa_python_sitelib}/ipaclient/plugins
%__mkdir_p %buildroot/%{ipa_python_sitelib}/ipaserver/plugins
%__mkdir_p %buildroot/%_datadir/ipa/schema.d
%__mkdir_p %buildroot/%_datadir/ipa/updates
%__mkdir_p %buildroot/%_datadir/ipa/ui/js/plugins/%{plugin_name}

for i in ipaserver ; do
	for j in $(find plugin/$i/plugins -name '*.py') ; do
		%__cp $j %buildroot/%{ipa_python_sitelib}/$i/plugins
	done
done

for j in $(find plugin/schema.d -name '*.ldif') ; do
	%__cp $j %buildroot/%_datadir/ipa/schema.d
done

for j in $(find plugin/updates -name '*.update') ; do
	%__cp $j %buildroot/%_datadir/ipa/updates
done

for j in $(find plugin/ui/%{plugin_name} -name '*.js') ; do
	%__cp $j %buildroot/%_datadir/ipa/js/plugins/%{plugin_name}
done


%posttrans
%if 0%{?fedora} > 26 || 0%{?rhel} > 7
ipa_interp=python3
%else
ipa_interp=python2
%endif
$ipa_interp -c "import sys; from ipaserver.install import installutils; sys.exit(0 if installutils.is_ipa_configured() else 1);" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    # This must be run in posttrans so that updates from previous
    # execution that may no longer be shipped are not applied.
    /usr/sbin/ipa-server-upgrade --quiet >/dev/null || :

    # Restart IPA processes. This must be also run in postrans so that plugins
    # and software is in consistent state
    # NOTE: systemd specific section

    /bin/systemctl is-enabled ipa.service >/dev/null 2>&1
    if [  $? -eq 0 ]; then
        /bin/systemctl restart ipa.service >/dev/null 2>&1 || :
    fi
fi

%files
%license COPYING
%doc plugin/Feature.mediawiki
#There is no client-side component yet
#%%python2_sitelib/ipaclient/plugins/*
%python2_sitelib/ipaserver/plugins/*
%_datadir/ipa/schema.d/*
%_datadir/ipa/updates/*
%_datadir/ipa/ui/js/plugins/%{plugin_name}/*

%changelog
* Thu Nov  10 2017 Alexander Bokovoy <abokovoy@redhat.com> 0.0.1-1
- Initial release

