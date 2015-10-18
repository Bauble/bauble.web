'use strict';

angular.module('BaubleApp')
    .controller('PropagationEditorCtrl', function ($scope) {

        // the $scope.propagation property should be inherited from the parent scope since
        // this is a "sub-editor"

        $scope.propagation_views = {
            "Seed": "views/propagation-edit-seed.html",
            "UnrootedCutting": "views/propagation-edit-cutting.html",
            "Other": null
        };
    });
