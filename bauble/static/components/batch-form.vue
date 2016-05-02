<template>
    <form @submit.prevent="submit($event)">
        <slot></slot>
    </form>
</template>

<script type="text/babel">
    export default {
        data() {
            return {
                requests: []
            }
        },
        methods: {
            appendRequest(method, url, body) {
                console.log(method.toUpperCase(), url, body)
                this.requests.push({method: method, url: url, body: body})
            },
            submit() {
                this.$broadcast('batch-form:submit', this)
                if (this.requests.length === 0) {
                    return
                }
                return $.ajax('/batch', {
                    method: 'POST',
                    data: JSON.stringify(this.requests),
                    contentType: 'application/json; charset=utf-8',
                    dataType: 'json'
                })
            }
        }
    }
</script>
