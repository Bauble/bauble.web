/* global Bloodhound */

import $ from 'jquery'
import _ from 'lodash'
import Vue from 'vue'
import 'typeahead.js/dist/typeahead.jquery.js'
import Bloodhound from 'typeahead.js/dist/bloodhound.js'

$('#accession-form').ready(function () {

    new Vue({
        el: '#accession-form',
        data: {

        },
        ready: function () {
            let taxa = new Bloodhound({
                datumTokenizer: Bloodhound.tokenizers.obj.whitespace('taxa'),
                queryTokenizer: Bloodhound.tokenizers.whitespace,

                remote: {
                    url: '/search.json?q=taxon%3D%QUERY%25',
                    wildcard: '%QUERY',
                    transform: (response) => {
                        return response['taxa']
                    }
                }
            })

            $(this.$el).find('#taxon').typeahead({
                minLength: 2,
                highlight: true,
            },{
                display: 'str',
                source: taxa
            }).on('typeahead:selected', (event, data) => {
                console.log('data: ', data);
                $('input#taxon_id').val(data.id)
            })
        },
    })
})
