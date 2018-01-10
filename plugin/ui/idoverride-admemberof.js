define([
        'freeipa/phases',
        'freeipa/ipa',
        'freeipa/app_container'],
        function(phases, IPA, app) {
var admemberof_plugin = {};

admemberof_plugin.replace_is_selfservice = function() {
    // Advanced version of AD user self-service page that
    // checks memberOf attribute in the ID overrides
    old_selfservice = app.app.is_selfservice;
    app.app.is_selfservice = function() {
            // Use old method first to find out 
	    // whether we already deal with admins
	    if (!old_selfservice()) {
		    return false;
	    }

            var whoami = IPA.whoami.data;
            var self_service = IPA.whoami.metadata.object === 'idoverrideuser';

            if (self_service && whoami.hasOwnProperty('memberof')) {
		var i = 0;
		var suffix = whoami.dn.substr(whoami.dn.lastIndexOf(',cn=accounts,') + 13);
		// If ID Override is a member of any privilege, role, or permission,
		// assume the user is granted with administrative rights and thus
		// should not be in a self service mode.
		for (i = 0; i < whoami.memberof.length; i++) {
		    if (whoami.memberof[i].includes(',cn=pbac,' + suffix)) {
			self_service = false;
		    }
		}
	    }

            IPA.is_selfservice = self_service;

            return self_service;
        };
    return true;
};

phases.on('metadata', admemberof_plugin.replace_is_selfservice);

return admemberof_plugin;
});

