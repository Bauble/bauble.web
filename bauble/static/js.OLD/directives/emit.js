'use strict';

angular.module('bauble-app')
    .directive('emit', function () {
        return {
            restrict: 'A',
            scope: true,
            link: function(scope, elm, attrs, controller) {
                elm.bind('click', function() {
                    scope.$emit(attrs.emit);
                });
            }
        };
    });
