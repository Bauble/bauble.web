// 'use strict';

// angular.module('bauble-app')
//     .factory('apiRoot', ['$location', function($location) {
//         // AngularJS will instantiate a singleton by calling "new" on this function

//         var stagingHosts = ['app-staging.bauble.io'];
//         var productionHosts = ['app.bauble.io'];

//         var host = $location.host();

//         if(stagingHosts.indexOf(host) !== -1) {
//             return 'https://api-staging.bauble.io/v1';
//         }

//         if(productionHosts.indexOf(host) !== -1) {
//             return 'https://api.bauble.io/v1';
//         }

//         return 'http://localhost:8088/v1';
//     }]);
