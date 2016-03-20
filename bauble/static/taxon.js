/* global Bloodhound */

import $ from 'jquery'
import _ from 'lodash'
import Vue from 'vue'
import 'typeahead.js/dist/typeahead.jquery.js'
import Bloodhound from 'typeahead.js/dist/bloodhound.js'


Vue.component('taxon-form', {
    template: '<div><slot></slot></div>',
    data: () => {
        return {}
    },
    ready: function () {
        let genera = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('genera'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,

            remote: {
                url: '/search.json?q=genus%3D%QUERY%25',
                wildcard: '%QUERY',
                transform: (response) => {
                    return response['genera']
                }
            }
        })

        $(this.$el).find('.typeahead').typeahead({
            minLength: 2,
            highlight: true,
        },{
            display: 'str',
            source: genera
        }).on('typeahead:selected', (event, data) => {
            console.log('data: ', data);
            $('input#genus_id').val(data.id)
        })
    }
})
