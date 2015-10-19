'use strict';

angular.module('bauble-app')
    .directive('loadingSpinner', function () {
        return {
            template: '<i class="loading-spinner fa fa-spin fa-spinner" ng-show="show"></i><span ng-transclude></span>',
            transclude: true,
            scope: {
                loadingSpinner: '='
            },
            restrict: 'A',
            link: function(scope, element, attrs) {
                scope.$watch('loadingSpinner', function(loading) {
                    scope.show = !!loading;
                });
            }
        };
    });
