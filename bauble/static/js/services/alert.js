'use strict';

angular.module('bauble-app')
    .service('Alert', [function () {
        // AngularJS will instantiate a singleton by calling "new" on this function
        return {
            add: function(message, level) {
                level = level || 'success'; // if no level then assume its a good message
                this.alerts.push({message: message,  level: level});
            },

            remove: function(index) {
                this.alerts.splice(index, 1);
            },

            clear: function() {
                this.alerts.splice(0, this.alerts.length);
            },

            onErrorResponse: function(responseData, defaultMessage) {
                var me = this;
                // TODO: handle standard API errors
                this.add(defaultMessage, 'danger');
            },

            alerts: []
        };
    }]);
