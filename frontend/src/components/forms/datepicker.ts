
import {Component, Prop} from 'vue-property-decorator'
import BaseControl from './base'
import * as Datepicker from 'vuejs-datepicker'

@Component({
    template: `<div :class="['form-group', {'has-danger': hasDanger}]">
        <slot name="label"></slot>
        <datepicker :value="value" @input="updateValue" wrapper-class="input-group"
                    :input-class="datepickerInputClass" :clear-button="clearButton" @cleared="cleared">
        </datepicker>
        <div v-if="hasDanger" class="form-control-feedback">{{ errorMessage }}</div>
        <slot name="help"></slot>
    </div>`,
    components: {
        'datepicker': Datepicker
    }
})
export default class InputDatepicker extends BaseControl {
    @Prop({default: false})
    clearButton: boolean;

    get datepickerInputClass() {
        return this.hasDanger ? 'form-control form-control-danger' : 'form-control';
    }

    cleared() {
        this.updateValue(null);
    }
}