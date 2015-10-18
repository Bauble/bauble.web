'use strict';

angular.module('BaubleApp')
  .controller('OrgInviteModalCtrl', ['$scope', '$modalInstance', 'Organization', 'Alert', 'organization',
    function ($scope, $modalInstance, Organization, Alert, organization) {

        console.log('organization: ', organization);

        $scope.send = function(email, message) {
            Organization.invite(organization, email, message)
                .success(function(data, status, headers, config) {
                    $modalInstance.close('saved');
                })
                .error(function(data, status, headers, config) {
                    if(status === 409) {
                        Alert.add("Could not send invitation.  A user with email address already has a Bauble account.", 'danger');
                    } else {
                        Alert.add("Could not send invitation.  Unknown error", "danger");
                    }
                    $modalInstance.dismiss('cancel');
                });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };
    }]);
