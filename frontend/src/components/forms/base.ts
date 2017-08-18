import * as Vue from 'vue'
import { Component, Prop } from 'vue-property-decorator'
import * as _ from 'lodash'

@Component
class BaseControl extends Vue {
    @Prop
    value;

    @Prop
    name;

    @Prop({ default: () => [] })
    errorMsgs: Array<string>;

    get isInvalid() {
        return this.errorMsgs.length > 0;
    }

    get errorMessage() {
        return this.errorMsgs.join(', ');
    }

    updateValue(value: any) {
        this.$emit('input', value);
    }
}

export default BaseControl;