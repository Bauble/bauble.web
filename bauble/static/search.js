import $ from 'jquery'
import _ from 'lodash'
import Vue from 'vue'

Vue.component('search-page', {
    data: () => {
        return {
            loading: false
        }
    },
    beforeCompile: () => {
       console.log('before ocmpile');

    },
    ready: function () {
        console.log('search page ready')
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
            // get the partial for the selected item
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
