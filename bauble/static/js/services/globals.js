'use strict';

angular.module('BaubleApp')
    .factory('globals', function () {

        return {
            alerts: [],

            addAlert: function(message, type){
                type = type || "success";
                this.alerts.push({ msg: message, type: type});
            },

            getAuthHeader: function() {
                var credentials = sessionStorage.getItem("credentials");
                return { "Authorization": "Basic " + credentials };
            },

            setSelected: function(selected) {
                sessionStorage.setItem("selected", JSON.stringify(selected));
            },

            getSelected: function() {
                return JSON.parse(sessionStorage.getItem('selected'));
            }
        };
    });
