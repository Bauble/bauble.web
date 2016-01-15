window.$ = window.jQuery = require('jquery');
const bootstrap = require('bootstrap-sass');

import Vue from 'vue'

import './search'
import './genus'
import './taxon'

$(document).ready(function () {
    Vue.config.debug = true
    Vue.config.delimiters = ['[[', ']]']
})

///
