import _ from 'lodash'
import {InstrumentedArray} from '../../utils'

export default function GenusEditController ($scope, $q, $location, $stateParams,
                                             locationStack, Alert, Family, Genus, overlay) {

    $scope.data = {
        genus: {
            family_id: $location.search().family,
        },
        family: {},
        synonyms: new InstrumentedArray(),
        notes: new InstrumentedArray()
    };

    // make sure we have the family details
    if($stateParams.id) {
        overlay('loading...');
        Genus.get($stateParams.id, {embed: ['family', 'notes', 'synonyms']})
            .success(function(data, status, headers, config) {
                $scope.data.genus = data;
                $scope.data.family = data.family;
                // pull out the notes and synonyms so we don't resubmit them
                // back on save
                $scope.data.notes = new InstrumentedArray($scope.data.genus.notes || []);
                $scope.data.synonyms = new InstrumentedArray($scope.data.genus.synonyms || []);
                delete $scope.data.genus.family;
                delete $scope.data.genus.synonyms;
                delete $scope.data.genus.notes;
            })
            .error(function(data, status, headers, config) {
                var defaultMessage = "Could not get genus details.";
                Alert.onErrorResponse(data, defaultMessage);
            })
            .finally(function() {
                overlay.clear();
            });
    } else if($scope.data.genus.family_id) {
        Family.get($scope.data.genus.family_id, {
            pick: ['id', 'str']
        }).success(function(data, status, headers, config) {
            $scope.data.family = data;
        }).error(function(data, status, headers, config) {
            var defaultMessage = "Could not get family details.";
            Alert.onErrorResponse(data, defaultMessage);
        })
            .finally(function() {
                overlay.clear();
            });
    }

    //$scope.families = []; // the list of completions
    $scope.activeTab = "general";

    $scope.formatInput = function() {
        console.log('$scope.data.family: ', $scope.data.family);
        var s = $scope.data.family ? $scope.data.family.str : '';
        console.log('s: ', s);
        return s;
    };

    $scope.getFamilies = function($viewValue) {
        return Family.list({filter: {family: $viewValue + '%'}})
            .then(function(result) {
                return result.data;
            });
    };

    $scope.getSynonyms = function($viewValue) {
        return Genus.list({filter: {genus: $viewValue + '%'}})
            .then(function(response) {
                return response.data;
            });
    };

    $scope.cancel = function() {
        locationStack.pop();
    };

    // called when the save button is clicked on the editor
    $scope.save = function(addTaxon) {
        // TODO: we need a way to determine if this is a save on a new or existing
        // object an whether we whould be calling save or edit
        // TODO: we should probably also update the selected result to reflect
        // any changes in the search result
        //$scope.data.genus.notes = $scope.notes;
        Genus.save($scope.data.genus)
            .success(function(data, status, headers, config) {

                $scope.data.genus = data;

                // update the synonyms
                $q.all(_.flatten(
                    _.map($scope.data.synonyms.added, function(synonym) {
                        return Genus.addSynonym($scope.data.genus, synonym);
                    }),
                    _.map($scope.data.synonyms.removed, function(synonym) {
                        return Genus.removeSynonym($scope.data.genus, synonym);
                    }))).then(function(result) {
                        if(addTaxon) {
                            $location.path('/taxon/add').search({'genus': $scope.data.genus.id});
                        } else {
                            locationStack.pop();
                        }
                    }).catch(function(result) {
                        var defaultMessage = "Some synonyms could not be saved.";
                        Alert.onErrorResponse(result.data, defaultMessage);
                    });

            })
            .error(function(data, status, headers, config) {
                var defaultMessage = "The genus could not be saved.";
                Alert.onErrorResponse(data, defaultMessage);
            });

        _.each($scope.newNote, function(note) {
        });

        _.each($scope.removedNote, function(note) {
        });
    };
}
