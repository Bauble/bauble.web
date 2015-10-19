'use strict';

angular.module('bauble-app')
    .controller('PropagationEditorCtrl', function ($scope) {

        // the $scope.propagation property should be inherited from the parent scope since
        // this is a "sub-editor"

        $scope.propagation_views = {
            "Seed": "/static/partials/propagation-edit-seed.html",
            "UnrootedCutting": "/static/partials/propagation-edit-cutting.html",
            "Other": null
        };
    });
