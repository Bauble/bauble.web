'use strict';

angular.module('BaubleApp')
    .factory('overlay', function () {

        var data = {
            message: ""
        };

        var service = function(msg){
            if(typeof msg !== "undefined") {
                data.message = msg;
            }
            return data.message;
        };

        service.clear = function() {
            service(null);
        };

        return service;
    });
