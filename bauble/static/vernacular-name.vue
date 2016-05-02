<template>
    <div class="vn-row row">
        <input type="hidden" v-model="id">
        <div class="col-md-3">
            <input type="text" v-model="name" class="form-control"
                   @change="dirty=true"/>
        </div>

        <div class="col-md-3">
            <input type="text" v-model="language" class="form-control"
                   @change="dirty=true"/>
        </div>

        <div class="col-md-1">
            <div class="checkbox">
                <!-- <label> -->
                <input type="checkbox" class="vn-default-check input-lg"
                       ng-model="default" @change="dirty=true">
                <!-- </label> -->
            </div>
        </div>

        <div class="text-center col-md-2">
            <button class="trash-btn btn" type="button" @click="remove">
                <i class="fa fa-trash-o"></i>
            </button>
        </div>
    </div>
</template>

<script type="text/babel">
    export default {
        props: {
            taxonId: {
                type: Number,
                /* required: true */
            },
            id: {
                type: Number,
                default: null
            },
            name: {
                type: String,
                default: ''
            },
            language: {
                type: String,
                default: ''
            },
            default: {
                type: Boolean,
                default: false
            }
        },
        data() {
            return {
                /* taxonId: null, */
                dirty: false
            }
        },
        ready() {
            console.log('vernacular name: ', this)
            console.log('taxonId: ', this.taxonId)
        },
        watch: {
            name: (name) => {
                console.log('name: ', name)
            }
        },
        events: {
            'batch-form:submit': function(batchForm) {
                if (this.dirty === false) {
                    return
                }
                const body = JSON.stringify({
                    name: this.name,
                    language: this.language,
                    default: this.default
                })
                const baseUrl = `/taxon/${this.taxonId}/vernacular_name`
                if (this.id === null) {
                    batchForm.appendRequest('POST', baseUrl, body)
                } else {
                    batchForm.appendRequest('PATCH', `${baseUrl}/${this.id}`, body)
                }
            }
        },
        methods: {
            add() {

            },
            remove() {
                console.log('remove vernacular name')
                this.$dispatch('remove')
                /* this.$emit('remove') */
                /* this.$broadcast('remove') */
            },
            update() {
                console.log('update verncular name')
            }
        }

    }
</script>
