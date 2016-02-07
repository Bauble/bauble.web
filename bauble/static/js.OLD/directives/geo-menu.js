'use strict';

angular.module('bauble-app')
    .directive('geographyMenu', function ($http, $compile, $location, Alert) {
        return {
            template: '<span class="geo-menu dropdown">' +
                '<a class="dropdown-toggle" ng-transclude></a>' +
                '</span>',
            restrict: 'EA',
            transclude: true,
            replace: true,
            scope: {
                onClick: '&',
            },
            link: function postLink(scope, element, attrs) {

                var $ = angular.element;
                scope.data = [];
                scope.indexedData = {};

                scope.onSelected = function($event, id) {
                    $event.preventDefault();
                    $event.stopPropagation();

                    // close the menu
                    element.removeClass('open');

                    scope.onClick({geo: scope.indexedData[id]});
                    return false;
                };

                scope.catchClick = function($event) {
                    // catch the click so it doesn't propagate to the dropdown-toggle directive
                    // and close hte menu
                    $event.preventDefault();
                    $event.stopPropagation();
                    return false;
                };

                scope.buildMenu = function(rows) {
                    var li, row, a, ul;
                    var items = [];
                    for(var i=0; i<rows.length; i++) {
                        row = rows[i];
                        a = $('<a ng-click="catchClick($event)"></a>').text(row.name);
                        li = $('<li></li>').append(a);
                        if(row.children && row.children.length > 0) {
                            li.addClass('dropdown-submenu');
                            a.append('<i class="pull-right fa fa-angle-right"></i>');
                            ul = $('<ul class="dropdown-menu"></ul>');
                            a = $('<a ng-click="catchClick($event)"></a>').text(row.name);
                            ul.append($('<li></li>').append(a));
                            ul.append($('<li class="divider"></li>'));

                            // ** jqLite doesn't support appending arrays of items
                            //li.append(ul.append(scope.buildMenu(row.children)));
                            /* jshint loopfunc: true */
                            scope.buildMenu(row.children).forEach(function(item){
                                ul.append(item);
                            });
                            li.append(ul);

                        }
                        a.attr('ng-click', 'onSelected($event,'+row.id+')');
                        items.push(li);
                    }

                    // return an array of li elements
                    return items;
                };

                scope.$watch('data', function(data){
                    element.find('.dropdown-menu').remove();  // remove the old menus

                    if(!data || data.length === 0) {
                        return;
                    }
                    // ** jqLite doesn't support appending arrays of items
                    // var items = scope.buildMenu(data);
                    // var ul = $('<ul class="dropdown-menu"></ul>').append(items);
                    var ul = $('<ul class="dropdown-menu"></ul>');
                    scope.buildMenu(data).forEach(function(item){
                        ul.append(item);
                    });

                    var compiled = $compile(ul)(scope);
                    element.find('.dropdown-toggle').after(compiled);
                });


                function flatten(items) {
                    // turn the items and it's nested children into an array
                    var item;
                    for(var i=items.length-1; i>=0; i--) {
                        item = items[i];
                        if(item.children && item.children.length > 0) {
                            items = items.concat(flatten(item.children));
                        }
                    }
                    return items;
                }

                $http.get('/data/geography.js')
                    .success(function(data, status, headers, config) {
                        scope.data = data;
                        var flat = flatten(data);
                        scope.indexedData = _.indexBy(flat, 'id');
                    })
                    .error(function(data, status, headers, config) {
                        var defaultMessage = 'Could not get data for distribution menu.';
                        Alert.onErrorResponse(data, defaultMessage);
                    });
            }
        };
    });
