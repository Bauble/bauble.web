/* global Bloodhound */

// import $ from 'jquery'
// import Vue from 'vue'
// import 'typeahead.js/dist/typeahead.jquery.js'
// import Bloodhound from 'typeahead.js/dist/bloodhound.js'
// import VernacularNames from './vernacular-names.vue'

// console.log('VernacularNames: ', VernacularNames);

// Vue.component('taxon-form', {
//     template: '<div><slot></slot></div>',
//     components: { VernacularNames },
//     // components: {
//     //     'vernacular-names': VernacularNames
//     // },
//     data() {
//         return {}
//     },
//     ready() {
//         console.log('this: ', this);
//         console.log('this.components: ', this.components);
//         const genera = new Bloodhound({
//             datumTokenizer: Bloodhound.tokenizers.obj.whitespace('genera'),
//             queryTokenizer: Bloodhound.tokenizers.whitespace,

//             remote: {
//                 url: '/search.json?q=genus%3D%QUERY%25',
//                 wildcard: '%QUERY',
//                 transform: (response) => response.genera
//             }
//         })

//         $(this.$el).find('.typeahead').typeahead({
//             minLength: 2,
//             highlight: true,
//         }, {
//             display: 'str',
//             source: genera
//         }).on('typeahead:selected', (event, data) => {
//             console.log('data: ', data);
//             $('input#genus_id').val(data.id)
//         })
//     },
//     methods: {
//     }
// })
