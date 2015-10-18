'use strict';

angular.module('BaubleApp', [
    'ui.bootstrap',
    'ui.router',
    'ngAnimate'
])

  .config(['$stateProvider', '$urlRouterProvider',
    function ($stateProvider, $urlRouterProvider) {

        $stateProvider
            .state('main', {
                abstract: true,
                templateUrl: 'views/main.html',
                controller: 'MainCtrl'
            })
            .state('main.dashboard', {
                url: '/dashboard',
                templateUrl: 'views/dashboard.html',
                controller: 'DashboardCtrl'
            })
            .state('main.search', {
                url: '/search?q',
                templateUrl: 'views/search.html',
                controller: 'SearchCtrl',
            })

            .state('main.settings', {
                url: '/settings',
                templateUrl: 'views/settings.html',
                controller: 'SettingsCtrl',
            })

            .state('login', {
                url: '/login',
                templateUrl: 'views/login.html',
                controller: 'LoginCtrl'
            })

            .state('logout', {
                url: '/logout',
                templateUrl: 'views/logout.html',
                controller: 'LogoutCtrl'
            })

            .state('main.resource-edit', {
                url: '/:resource/:id/edit',
                templateUrl: function($stateParams) {
                    return 'views/' + $stateParams.resource.toLowerCase() + "-edit.html";
                },
                controllerProvider: ['$stateParams', function($stateParams) {
                    var resource = $stateParams.resource;
                    resource = resource.slice(0,1).toUpperCase() + resource.slice(1, resource.length);
                    return resource + "EditCtrl";
                }]

            })

            .state('main.resource-add', {
                url: '/:resource/add',
                templateUrl: function($stateParams) {
                    return 'views/' + $stateParams.resource.toLowerCase()+ "-edit.html";
                },
                controllerProvider: ['$stateParams', function($stateParams) {
                    var resource = $stateParams.resource;
                    resource = resource.slice(0,1).toUpperCase() + resource.slice(1, resource.length);
                    return resource + "EditCtrl";
                }]
            })

            .state('signup', {
                url: '/signup',
                templateUrl: 'views/signup.html',
                controller: 'SignupCtrl'
            })

            .state('main.reset-password', {
                url: '/reset-password/:token',
                templateUrl: 'views/reset-password.html',
                controller: 'ResetPasswordCtrl'
            })

            .state('main.forgot-password', {
                url: '/forgot_password',
                templateUrl: 'views/forgot-password.html',
                controller: 'ForgotPasswordCtrl'
            })

            .state('main.accept-invitation', {
                url: '/accept-invitation/:token',
                templateUrl: 'views/accept-invitation.html',
                controller: 'AcceptInvitationCtrl'
            })

            .state('main.organization-new', {
                url: '/organization/new',
                templateUrl: 'views/org-edit.html',
                controller: 'OrgEditCtrl'
            })

            .state('main.report-new', {
                url: '/report',
                templateUrl: 'views/report.html',
                controller: 'ReportCtrl'
            })

            .state('main.report-edit', {
                url: '/report/:id',
                templateUrl: 'views/report.html',
                controller: 'ReportCtrl'
            });



        // .when('/admin', {
        //     templateUrl: 'views/admin.html',
        //     controller: 'AdminCtrl'
        // })



        // .when('/docs', {
        //     templateUrl: 'views/docs.html'
        // })



        $urlRouterProvider.otherwise('/dashboard');
    }]);
