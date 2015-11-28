import angular from 'angular'
import angularUIBootstrap from 'angular-ui-bootstrap'
import angularUIRouter from 'angular-ui-router'
import angularAnimate from 'angular-animate'
import _ from 'lodash'

import * as shared from './shared/index'
import * as dashboard from './components/dashboard/index'
import * as search from './components/search/index'
import * as family from './components/family/index'
import * as genus from './components/genus/index'
import * as taxon from './components/taxon/index'
import * as accession from './components/accession/index'
import * as plant from './components/plant/index'
import * as location from './components/location/index'

import utils from './utils'

const app = angular.module('bauble-app', [
    angularUIBootstrap,
    angularUIRouter,
    angularAnimate
])

app.config(function($locationProvider) {
    $locationProvider.html5Mode(true);
})

app.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
        .state('dashboard', {
            url: '/',
            templateUrl: '/static/partials/dashboard.html',
            controller: 'DashboardCtrl'
        })
        .state('search', {
            url: '/search',
            templateUrl: '/static/components/search/search.html',
            controller: 'SearchCtrl',
        })

        // .state('settings', {
        //     url: '/settings',
        //     templateUrl: '/static/partials/settings.html',
        //     controller: 'SettingsCtrl',
        // })

        // .state('login', {
        //     url: '/login',
        //     templateUrl: '/static/partials/login.html',
        //     controller: 'LoginCtrl'
        // })

        // .state('logout', {
        //     url: '/logout',
        //     templateUrl: '/static/partials/logout.html',
        //     controller: 'LogoutCtrl'
        // })

        .state('resource-edit', {
            url: '/:resource/:id/edit',
            templateUrl: function($stateParams) {
                const resource = $stateParams.resource.toLowerCase()
                return `/static/components/${resource}/edit.html`
            },
            controllerProvider: ['$stateParams', function($stateParams) {
                var resource = $stateParams.resource;
                resource = resource.slice(0,1).toUpperCase() + resource.slice(1, resource.length);
                return `${resource}EditController`
            }]
        })

        .state('resource-add', {
            url: '/:resource/add',
            templateUrl: function($stateParams) {
                const resource = $stateParams.resource.toLowerCase()
                return `/static/components/${resource}/edit.html`
            },
            controllerProvider: ['$stateParams', function($stateParams) {
                var resource = $stateParams.resource;
                resource = resource.slice(0,1).toUpperCase() + resource.slice(1, resource.length);
                return `${resource}EditController`
            }]
        })

        // .state('signup', {
        //     url: '/signup',
        //     templateUrl: '/static/partials/signup.html',
        //     controller: 'SignupCtrl'
        // })

        // .state('main.reset-password', {
        //     url: '/reset-password/:token',
        //     templateUrl: '/static/partials/reset-password.html',
        //     controller: 'ResetPasswordCtrl'
        // })

        // .state('main.forgot-password', {
        //     url: '/forgot_password',
        //     templateUrl: '/static/partials/forgot-password.html',
        //     controller: 'ForgotPasswordCtrl'
        // })

        // .state('main.accept-invitation', {
        //     url: '/accept-invitation/:token',
        //     templateUrl: '/static/partials/accept-invitation.html',
        //     controller: 'AcceptInvitationCtrl'
        // })

        // .state('main.organization-new', {
        //     url: '/organization/new',
        //     templateUrl: '/static/partials/org-edit.html',
        //     controller: 'OrgEditCtrl'
        // })

        // .state('main.report-new', {
        //     url: '/report',
        //     templateUrl: '/static/partials/report.html',
        //     controller: 'ReportCtrl'
        // })

        // .state('main.report-edit', {
        //     url: '/report/:id',
        //     templateUrl: '/static/partials/report.html',
        //     controller: 'ReportCtrl'
        // });

    $urlRouterProvider.otherwise('/')
})

shared.init(app)
dashboard.init(app)
search.init(app)
family.init(app)
genus.init(app)
taxon.init(app)
accession.init(app)
plant.init(app)
location.init(app)

///
