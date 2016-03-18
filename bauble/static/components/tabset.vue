<template>
    <div class="tabset clearfix">
        <!-- Nav tabs -->
        <ul class="nav nav-tabs" role="tablist">
            <li role="presentation" v-for="tab in tabs"
                :class="{ active: tab.active, disabled: tab.disabled }" >
                <a href="#{{ $index }}" aria-controls="{{{ tab.header }}}" role="tab"
                   data-toggle="tab"
                   @click.stop.prevent="activateTab($index)">{{{ tab.header }}}</a>
            </li>
        </ul>

        <!-- Tab panes -->
        <div class="tab-content">
            <slot></slot>
        </div>
    </div>
</template>

<!-- <style lang="sass" src="./tabs.scss"></style> -->

<script type="text/babel">
    export default {
        data: function() {
            return {
                tabs: []
            };
        },
        methods: {
            activateTab: function(index) {
                var tab = this.tabs[index];

                if(tab && !tab.disabled) {
                    if(index == 'first') {
                        index = 0;
                    }
                    else if(index == 'last') {
                        index = this.tabs.length - 1;
                    } // end if

                    this.tabs.forEach(function(tab, idx) {
                        tab.active = idx === index;
                    });
                } // end if
            },
            registerTab: function(tab) {
                tab.id = this.tabs.length;
                tab.active = this.tabs.length === 0;
                this.tabs.push(tab);
            }
        }
    }
</script>
