/* global Bloodhound */

import $ from 'jquery'
import _ from 'lodash'
import Vue from 'vue'
import 'typeahead.js/dist/typeahead.jquery.js'
import Bloodhound from 'typeahead.js/dist/bloodhound.js'


Vue.component('plant-form', {
    template: '<div><slot></slot></div>',
    data: () => {
        return {}
    },
    ready: function () {
        let accessions = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('accession'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,

            remote: {
                url: '/search.json?q=acc%3D%QUERY%25',
                wildcard: '%QUERY',
                transform: (response) => {
                    return response['accessions']
                }
            }
        })

        $(this.$el).find('#accession').typeahead({
            minLength: 2,
            highlight: true,
        },{
            display: 'str',
            source: accessions
        }).on('typeahead:selected', (event, data) => {
            console.log('data: ', data);
            $('input#accession_id').val(data.id)
        })


        let locations = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('location'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,

            remote: {
                url: '/search.json?q=loc%3D%QUERY%25',
                wildcard: '%QUERY',
                transform: (response) => {
                    return response['locations']
                }
            }
        })

        $(this.$el).find('#location').typeahead({
            minLength: 2,
            highlight: true,
        },{
            display: 'str',
            source: locations
        }).on('typeahead:selected', (event, data) => {
            console.log('data: ', data);
            $('input#location_id').val(data.id)
        })
    },
})
