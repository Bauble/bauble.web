'use strict';

angular.module('bauble-app')
    .directive('schemaMenu', function ($compile, Resource) {
        return {
            restrict: 'A',
            replace: true,
            transclude: true,
            scope: {
                resource: '=',
                scalarsOnly: '@',
                onSelect: '&',
                onLoaded: '&',
                selected: '=',
                isOpen: '='
                // label2: '=?' // i think this is only available in ng 1.2
            },
            template: '<div dropdown class="btn-group schema-menu" is-open="isOpen">' +
                '<button type="button" class="btn btn-default dropdown-toggle" ng-class="{disabled: !resource}">' +
                '{{selected}}' +
                  '<span class="caret"></span>' +
                '</button>'+

            '<ul class="dropdown-menu" role="menu" aria-labelledby="dLabel">' +
                '</ul>' +
                '</div>',
            link: function(scope, element, attrs) {
                var baseMenu = '' +
                        '<!-- columns -->' +
                        '<li ng-repeat="(column, value) in schema.columns" ng-click="onItemClicked(this, $event, column)">' +
                          '<a tabindex="-1">{{column}}</a>' +
                        '</li>' +

                        '<!-- relations -->' +
                        '<li ng-repeat="relation in schema.relations" class="dropdown-submenu">' +
                          '<a ng-mouseover="mouseOver($event, this, relation)">{{relation}}</a>' +
                          '<ul class="dropdown-menu relation-submenu">' +
                          //   '<!-- this is where the submenus list items are added -->' +
                          '</ul>' +
                        '</li>';

                // TODO: when we move to ng-1.2 use the =? scope value for
                // label so we can make it optional
                if(!scope.label) {
                    scope.label = 'Select a field';
                }

                scope.onItemClicked = function(itemScope, event, column) {

                    scope.isOpen = false;

                    // set the text on the btn to the selected item
                    var resourceParts = itemScope.resource.split("/");
                    resourceParts.push(itemScope.column);
                    resourceParts = resourceParts.splice(2); // remove the empty string and table
                    scope.selected = resourceParts.join('.');
                    if(scope.onSelect){
                        scope.onSelect({$event: event, column: column,
                                        selected: scope.selected});
                    }
                };

                //
                // watch selected for changes and set the value on the button
                //
                scope.$watch('selected', function(selected){
                    console.log('scope.selected: ', scope.selected);
                    element.attr("data-selected", scope.selected);
                });


                // create a menu and append it to parentElement
                function buildMenu(resource, callback) {
                    // get the schema for a resource
                    Resource(resource).getSchema(scope.scalarsOnly)
                        .success(function(data, status, headers, config) {
                            // create a new scope for the new menu
                            var newScope = scope.$new();
                            newScope.schema = data;
                            newScope.resource = resource;

                            // compile the menu snippet and set the new scope
                            var newMenu = $compile(baseMenu)(newScope);
                            callback(newMenu);
                        })
                        .error(function(data, status, headers, config) {
                            // do something
                            /* jshint -W015 */
                        });
                }

                scope.mouseOver = function(event, scope, relation) {
                    // if no menu has been added to this one then fetch the schema
                    // and build the sub menu
                    var submenu = $(event.target).parent('.dropdown-submenu').first();
                    if(submenu.children('.dropdown-menu').first().children().length === 0) {
                        // TODO: first add a "loading spinner" and remove it
                        // when buildMenu completes

                        // walk up the menus getting the full relation string
                        // for this menu item
                        var parentMenu = submenu,
                            relationUrl = scope.resource;
                        while(parentMenu.length !== 0) {
                            relationUrl += "/" + parentMenu.children('a').text();
                            parentMenu = parentMenu.parent('.dropdown-submenu');
                        }

                        //get the resource for the relation
                        buildMenu(relationUrl, function(menu) {
                            submenu.children('.dropdown-menu').first().append(menu);
                        });
                    }
                };

                //
                // rebuild the schema menu when the resource changes
                //
                scope.$watch('resource', function(resource) {
                    if(!resource) {
                        return;
                    }
                    // build the menu for this resource
                    if(typeof resource !== 'undefined') {
                        buildMenu(resource, function(menu) {
                            // TODO: can this be dont with one called like
                            // replaceWith() instead of first emptying and then
                            // appending
                            element.children('.dropdown-menu').first().empty()
                                .append(menu);
                        });
                    }
                });
            }
        };
    });
