const $ = window.$ = window.jQuery = require('jquery')
const bootstrap = require('bootstrap-sass')

import Vue from 'vue'

import './search'
import './genus'
import './taxon'
import './accession'
import './plant'
import './location'
import './taxon-form'

import Tabset from './components/tabset.vue'
import Tab from './components/tab.vue'
import BatchForm from './components/batch-form.vue'

import App from './app.vue'
// import TaxonForm from './taxon-form.vue'
// import VernacularName from './vernacular-name.vue'

Vue.config.debug = true
Vue.config.delimiters = ['[[', ']]']

new Vue({
    el: 'body',
    components: {
        App,
        BatchForm,
        Tab,
        Tabset,

        // TaxonForm,
        // VernacularName,
        // TODO: i don't wnat to have to define every component,
        // how come we don't have to define taxon-form
    }
})

///
