/* global Bloodhound */

import $ from 'jquery'
import _ from 'lodash'
import Vue from 'vue'
import 'typeahead.js/dist/typeahead.jquery.js'
import Bloodhound from 'typeahead.js/dist/bloodhound.js'

$('#taxon-form').ready(function () {

    new Vue({
        el: '#taxon-form',
        data: {

        },
        ready: function () {
            let genera = new Bloodhound({
                datumTokenizer: Bloodhound.tokenizers.obj.whitespace('genera'),
                queryTokenizer: Bloodhound.tokenizers.whitespace,

                remote: {
                    url: '/search.json?q=genus=%QUERY%',
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
        },
    })
})
