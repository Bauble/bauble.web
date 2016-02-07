import _ from 'lodash'
import {InstrumentedArray} from '../../utils'

export default function TaxonEditController ($scope, $location, $q, $http, $timeout,
                                             $stateParams, $window, Alert, Genus, Taxon,
                                             overlay) {

    $scope.activeTab = "general";
    $scope.qualifiers = ["agg.", "s. lat.", "s. str."];
    $scope.ranks = ["cv.", "f.", "subf.", "subsp.", "subvar.", "var."];

    $scope.data = {
        taxon: {
            genus_id: $location.search().genus,
        },
        genus: {},
        synonyms: new InstrumentedArray(),
        names: new InstrumentedArray(),
        notes: new InstrumentedArray(),
        distribution: new InstrumentedArray(),
        selectedDistItem: null,
        deletingItem: null,
    };

    // $http.get('/data/geography.json')
    $http.get('/api/geographies')
        .success(function(data, status, headers, config) {
            $scope.geography = data;
            console.log('data: ', data);
        })
        .error(function(data, status, headers, config) {
            var defaultMessage = 'Could not get data for distribution menu.';
            Alert.onErrorResponse(data, defaultMessage);
        });

    // make sure we have the taxon details
    if($stateParams.id) {
        overlay('loading...');
        Taxon.get($stateParams.id, {embed: ['genus', 'vernacular_names', 'synonyms', 'distribution']})
            .success(function(data, status, headers, config) {
                $scope.data.taxon = data;
                $scope.data.genus = data.genus;
                $scope.data.notes = new InstrumentedArray($scope.data.taxon.notes || []);
                $scope.data.distribution = new InstrumentedArray(_.sortBy($scope.data.taxon.distribution, 'id') || []);
                $scope.data.names = new InstrumentedArray($scope.data.taxon.vernacular_names || [{}]);
                $scope.data.synonyms = new InstrumentedArray($scope.data.taxon.synonyms || []);
                // delete the embedded properties so we don't resubmit them
                delete $scope.data.taxon.genus;
                delete $scope.data.taxon.synonyms;
                delete $scope.data.taxon.vernacular_names;
                delete $scope.data.taxon.notes;
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = "Could not get taxon details.";
                Alert.onErrorResponse(data, defaultMessage);
            })
            .finally(function() {
                overlay.clear();
            });
    } else if($scope.data.taxon.genus_id) {
        overlay('loading...');
        Genus.get($scope.data.taxon.genus_id)
            .success(function(data, status, headers, config) {
                $scope.data.genus = data;
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = "Could not get genus details.";
                Alert.onErrorResponse(data, defaultMessage);
            })
            .finally(function() {
                overlay.clear();
            });
    }

    // get genera for the genus completions
    $scope.getGenera = function($viewValue) {
        return Genus.list({filter: {genus: $viewValue + '%'}})
            .then(function(result) {
                return result.data;
            });
    };

    // get the taxa for the synonyms completion
    $scope.getSynonyms = function($viewValue) {
        // TODO: do we need to match on more than just the genus for genera
        // with lots of taxa...we could probably do further filtering using
        // angular and filtering on the taxon.str property
        return Taxon.list({filter: {genus: $viewValue + '%'}})
            .then(function(result) {
                return result.data;
            });
    };

    $scope.cancel = function() {
        $window.history.back()
    };


    $scope.clickDistItem = function($event, $index, geo) {
        $event.preventDefault();
        $event.stopPropagation();

        if($scope.data.selectedDistItem === $index) {
            // we use deletingItem to hide the item to be removed and then
            // do the actual removal in a timeout because for some reason
            // the removal seems to trigger the animation and makes the
            // visual removal of the item in the ng-repeat appear slow
            $scope.data.deletingItem = $index;
            $scope.data.selectedDistItem = null;
            $timeout(function() {
                $scope.data.distribution.remove(geo);
                $scope.data.deletingItem = null;
            }, 0);
        } else {
            $scope.data.selectedDistItem = $index;
        }
    };


    // disable the selectedDistItem when the body is clicked
    var bodyClick = function() {
        $scope.$apply(function() {
            $scope.data.selectedDistItem = null;
        });
    };

    var body = document.getElementsByTagName('body');
    angular.element(body).on('click', bodyClick);

    $scope.$on("$destroy", function() {
        // cleanup body click
        var body = document.getElementsByTagName('body');
        angular.element(body).off('click', bodyClick);
    });

    // called when the save button is clicked on the editor
    $scope.save = function(addAccession) {
        console.log('$scope.data.genus: ', $scope.data.genus);

        // remove any notes without a note
        // angular.forEach($scope.notes, function(note, key) {
        //     if(note.note){
        //         $scope.taxon.notes.push(note);
        //     }
        // });

        function saveNames() {
            return $q.all(_.flatten(
                _.map($scope.data.names.added, function(name) {
                    return Taxon.saveName($scope.data.taxon, name);
                }),
                _.map($scope.data.names.removed, function(name) {
                    return Taxon.removeName($scope.data.taxon, name);
                })))
                .catch(function(result) {
                    var defaultMessage = "Some names could not be saved.";
                    Alert.onErrorResponse(result.data, defaultMessage);
                    $q.reject(result);
                });
        }

        function saveSynonyms() {
            return $q.all(_.flatten(
                _.map($scope.data.synonyms.added, function(synonym) {
                    return Taxon.addSynonym($scope.data.taxon, synonym);
                }),
                _.map($scope.data.synonyms.removed, function(synonym) {
                    return Taxon.removeSynonym($scope.data.taxon, synonym);
                })))
                .catch(function(result) {
                    var defaultMessage = "Some synonyms could not be saved.";
                    Alert.onErrorResponse(result.data, defaultMessage);
                    $q.reject(result);
                });
        }

        function saveDistributions() {
            return $q.all(_.flatten(
                _.map($scope.data.distribution.added, function(distribution) {
                    return Taxon.addDistribution($scope.data.taxon, distribution);
                }),
                _.map($scope.data.distribution.removed, function(distribution) {
                    return Taxon.removeDistribution($scope.data.taxon, distribution);
                })))
                .catch(function(result) {
                    var defaultMessage = "Some distributions could not be saved.";
                    Alert.onErrorResponse(result.data, defaultMessage);
                    $q.reject(result);
                });

        }

        Taxon.save($scope.data.taxon)
            .success(function(data, status, headers, config) {

                $scope.data.taxon = data;

                $q.all(saveSynonyms(),
                       saveNames(),
                       saveDistributions())
                    .then(function(results) {
                        if(addAccession) {
                            $location.path('/accession/add').search({'taxon': $scope.data.taxon.id});
                        } else {
                            $window.history.back()
                        }
                        //return results;
                    });
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = "The taxon could not be saved.";
                Alert.onErrorResponse(data, defaultMessage);
            });
    };
}
