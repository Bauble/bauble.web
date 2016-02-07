'use strict';

angular.module('bauble-app')
  .controller('SettingsCtrl', ['$scope', '$modal', 'User', 'Organization', 'Alert',
    function ($scope, $modal, User, Organization, Alert) {
        $scope.user = User.local();
        $scope.alerts = Alert.alerts;

        $scope.model = {
            password1: '',
            password2: '',
            changedPasswordSuccess: null
        };

        Organization.get($scope.user.organization_id, {embed: 'users'})
            .success(function(data, status, headers, config) {
                $scope.organization = data;
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = "Could not get organization details.";
                Alert.onErrorResponse(data, defaultMessage);
            });


        $scope.changePassword = function(password) {
            // send request with password from form instead of
            // stored auth token
            $scope.user.save({id: $scope.user.id, password: password})
                .success(function(data, status, headers, config) {
                    $scope.changePasswordSuccess = true;
                    $scope.model.password1 = '';
                    $scope.model.password2 = '';
                })
                .error(function(data, status, headers, config) {
                    $scope.changePasswordSuccess = false;
                });

        };


        $scope.editOrg = function() {
            var modalInstance = $modal.open({
                templateUrl: '/static/partials/org-edit-modal.html',
                controller: function($scope, $modalInstance, organization){

                    $scope.org = organization;

                    $scope.save = function(org) {
                        Organization.save(org)
                            .success(function(data, status, headers, config) {
                                $modalInstance.close(data);
                            })
                            .error(function(data, status, headers, config) {
                                var defaultMessage = "Could not save organization";
                                Alert.onErrorResponse(data, defaultMessage);
                            });

                    };
                    $scope.cancel = function() {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                    organization: function() {
                        return _.clone($scope.organization);
                    }
                }
            });

            modalInstance.result.then(function close(org){
                var users = $scope.organization.users;
                _.assign($scope.organization, org);
                $scope.organization.users = users;
            }, function dismiss() {
                // TODO: canceled
            });
        };


        $scope.invite = function() {
            var modalInstance = $modal.open({
                templateUrl: '/static/partials/org-invite-modal.html',
                controller: 'OrgInviteModalCtrl',
                resolve: {
                    organization: function() {
                        return _.clone($scope.organization);
                    }
                }
            });
        };

    }]);
