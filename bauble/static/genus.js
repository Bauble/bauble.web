/* global Bloodhound */

import $ from 'jquery'
import _ from 'lodash'
import Vue from 'vue'
import 'typeahead.js/dist/typeahead.jquery.js'
import Bloodhound from 'typeahead.js/dist/bloodhound.js'

Vue.component('genus-form', {
    template: '<div><slot></slot></div>',
    data: () => {
        return {}
    },
    ready: function () {
        let families = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('families'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,

            remote: {
                url: '/search.json?q=family%3D%QUERY%25',
                wildcard: '%QUERY',
                transform: (response) => {
                    return response['families']
                }
            }
        })

        $(this.$el).find('.typeahead').typeahead({
            minLength: 2,
            highlight: true,
        },{
            display: 'str',
            source: families
        }).on('typeahead:selected', (event, data) => {
            console.log('data: ', data);
            $('input#family_id').val(data.id)
        })
    },
})
