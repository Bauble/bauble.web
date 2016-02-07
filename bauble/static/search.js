import $ from 'jquery'
import _ from 'lodash'
import Vue from 'vue'

$("#search-page").ready(function () {
    new Vue({
        el: '#search-page',
        data: {
            loading: false
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
                const self = this;
                self.loading = true
                $.ajax(url)
                    .done((data) => {
                        $('#resource-view').html(data)
                    })
                    .always(() => {
                        self.loading = false
                    })
            },
            selectItem: function (event) {
                var url = $(event.target).data('resource')
                window.location.hash = url
            }
        }
    })
})
