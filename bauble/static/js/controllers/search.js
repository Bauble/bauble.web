import _ from 'lodash'

const app = angular.module('bauble-app')

app.controller('SearchCtrl', function ($scope, $location, $state, Search, ViewMeta) {
    console.log('SearchCtrl')
    $scope.viewMeta = null;
    $scope.selected = null;
    $scope.results = null; // the results of the search
    $scope.$location = $location;  // so we can $watch it later;
    $scope.loading = false;

    $scope.capitalize = function(str) {
        return str.slice(0,1).toUpperCase() + str.slice(1,str.length);
    };

    // update the search whenever the q param changes
    $scope.$watch('$location.search().q', function(q) {
        $scope.viewMeta = null;
        $scope.query = q;
        $scope.search(q);
    });


    // query the server for search results
    $scope.search = function(query) {
        $scope.results = [];

        if(!query) {
            $scope.message = "Please enter a search query";
            return;
        }

        $scope.loading = true;
        $location.search('q', query);

        $scope.message = "Searching....";
        $scope.selected = $scope.viewMeta = $scope.results = null;

        Search.query(query)
            .success(function(data, status, headers, config) {
                $scope.results = data;
                // if($scope.results.length===0) {
                //     $scope.alert = "No results for your search query";
                // }
                $scope.message = "";
                if(_.size($scope.results) === 0) {
                    $scope.message = "Nothing found.";
                }

                if(_.size($scope.results) === 1) {
                    $scope.isOpen = true;
                    var key = _.keys($scope.results)[0];
                    if(_.size($scope.results[key]) === 1) {
                        $scope.itemSelected(key, $scope.results[key][0]);
                    }
                } else {
                    $scope.isOpen = false;
                }

                $scope.loading = false;
            })
            .error(function(data, status, headers, config) {
                $scope.message = "";
                $scope.loading = false;
            });
    };


    // update the view and current selection whenever a result is selected
    $scope.itemSelected = function(resource, selected) {
        $scope.viewMeta = ViewMeta.getView(resource, selected);
        $scope.selected = selected;
    };
});
