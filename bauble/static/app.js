window.$ = window.jQuery = require('jquery');
const bootstrap = require('bootstrap-sass');

import Vue from 'vue'

import './search'
import './genus'
import './taxon'
import './accession'
import './plant'
import './location'
import Tabset from './components/tabset.vue'
import Tab from './components/tab.vue'


$(document).ready(function () {
    Vue.config.debug = true
    Vue.config.delimiters = ['[[', ']]']
    new Vue({
        el: 'body',
        components: {
            tabset: Tabset,
            tab: Tab
        }
    })
})

///
