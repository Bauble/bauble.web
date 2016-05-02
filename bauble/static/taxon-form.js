import $ from 'jquery'
import Vue from 'vue'
import 'typeahead.js/dist/typeahead.jquery.js'
import Bloodhound from 'typeahead.js/dist/bloodhound.js'
import BatchForm from './components/batch-form.vue'
import VernacularName from './vernacular-name.vue'

Vue.component('taxon-form', {
    components: {
        BatchForm,
        VernacularName
    },
    props: ['taxon-id'],
    data() {
        return {}
    },
    ready() {
        const genera = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('genera'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,

            remote: {
                url: '/search.json?q=genus%3D%QUERY%25',
                wildcard: '%QUERY',
                transform: (response) => response.genera
            }
        })

        $(this.$el).find('.typeahead').typeahead({
            minLength: 2,
            highlight: true,
        }, {
            display: 'str',
            source: genera
        }).on('typeahead:selected', (event, data) => {
            $('input#genus_id').val(data.id)
        })
    },
    events: {
        remove() {
            console.log('vn_remove event')
        }
    },
    methods: {
        addVernacularName() {
            // TODO: a vernacular name can not be added until the form is saved
            // because we don't know the taxon id...we can either force the
            // use to save first or we allow the create route to accept
            // vernacular ids since we know all the vernacular ids will be
            // new
            const el = document.createElement('div') // wrapper element
            // create a vernacular-name component and set the parent to
            // batchForm so it can listen for the forms submit event
            console.log('taxon-id: ', this.taxonId)
            const vn = new (Vue.extend(VernacularName))({
                el,
                parent: this.$refs.batchForm,
                data: { taxonId: this.taxonId },
                taxonId: this.taxonId
            })
            vn.$on('remove', this.removeVernacularName)
            vn.$appendTo('#vernacular-names')
        },
        changeVernacularName() {
        },
        removeVernacularName(id) {
            const batchForm = this.$refs.batchForm
            batchForm.appendRequest({ url: `${this.taxonId}/vernacular_names/${id}`,
                                      method: 'DELETE' })
        }
    }
})
