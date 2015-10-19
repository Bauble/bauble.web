'use strict';

angular.module('bauble-app')
    .directive('synonymsForm', function () {
        return {
            templateUrl: '/static/partials/synonyms-form.html',
            restrict: 'E',
            scope: {
                model: '=model',
                placeholder: '@',
                query: '&',
                onSelect: '&'
            },
            link: function postLink(scope, element, attrs) {

                scope.data = {
                    selectedSynonym: null,
                    newSynonym: null
                };

                // if there is a click outside the synonyms form then nullify
                // the selected synonym
                var bodyClick = function() {
                    scope.$apply(function() {
                        scope.data.selectedSynonym = null;
                    });
                };

                var body = document.getElementsByTagName('body');
                angular.element(body).on('click', bodyClick);

                scope.onClick = function($event, $index) {
                    scope.data.selectedSynonym=$index;
                    $event.stopPropagation();
                    $event.preventDefault();
                };

                scope.$on("$destroy", function() {
                    var body = document.getElementsByTagName('body');
                    angular.element(body).off('click', bodyClick);
                });
            }
        };
    });
