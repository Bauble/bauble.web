'use strict';

angular.module('BaubleApp')
    .directive('locationPush', function ($location, locationStack) {
        return {
            restrict: 'A',
            scope: {
                locationPush: '='
            },
            link: function postLink(scope, element, attrs) {
                element.bind('click', function() {
                    locationStack.push($location, false);
                });

                scope.$on('$destroy', function() {
                    element.unbind('click');
                });
            }
        };
    });
