import $ from 'jquery'
import _ from 'lodash'
import Vue from 'vue'

$("#search-page").ready(function () {
    new Vue({
        el: '#search-page',
        data: {

        },
        ready: function () {
            $(window).on('hashchange', this.hashChanged)
            if(!_.isEmpty(window.location.hash)) {
                this.hashChanged()
            }
        },
        methods: {
            hashChanged: function () {
                const url = window.location.hash.substr(1)
                $.ajax(url)
                    .done(function (data) {
                        $('#resource-view').html(data)
                    })
            },
            selectItem: function (event) {
                var url = $(event.target).data('resource')
                window.location.hash = url
            }
        }
    })
})
