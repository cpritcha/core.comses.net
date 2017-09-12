import * as Vue from 'vue'
import {Component, Prop} from 'vue-property-decorator'
import {codebaseAPI} from "api/index";
import Checkbox from 'components/forms/checkbox'
import Input from 'components/forms/input'
import Tagger from 'components/tagger'
import MarkdownEditor from 'components/forms/markdown'
import {createFormValidator} from "pages/form";
import * as yup from 'yup'

export const schema = yup.object().shape({
    title: yup.string().required(),
    description: yup.string().required(),
    live: yup.bool(),
    is_replication: yup.bool(),
    tags: yup.array().of(yup.object().shape({name: yup.string().required()})).min(1),
    repository_url: yup.string().url()
});

@Component(<any>{
    template: `<div>
        <p>
        Archiving the software that your research depends on can be tricky. We'll walk you through a submission workflow that
        guides you through the steps needed to generate a citable software archive that broadly follows recommended practices
        for <a href='https://www.force11.org/software-citation-principles'>software citation</a>.
        </p>
        <p>
        First, let's figure out what you'd like to call this thing.
        </p>
        <c-input v-model="title" name="title" :errorMsgs="errors.title" label="Title"
            help="A short title describing the codebase">
        </c-input>
        <c-markdown v-model="description" :errorMsgs="errors.description" name="description" rows="3" label="Description">
        </c-markdown>
        <c-checkbox v-model="live" name="live" :errorMsgs="errors.live" label="Published?"
            help="Published models are visible to everyone. Unpublished models are visible only to you">
        </c-checkbox>
        <c-checkbox v-model="is_replication" :errorMsgs="errors.is_replication" name="replication" label="Is a replication?">
        </c-checkbox>
        <c-tagger v-model="tags" name="tags" :errorMsgs="errors.tags" label="Tags">
        </c-tagger>
        <c-input v-model="repository_url" :errorMsgs="errors.repository_url" name="repository_url" label="Repository URL"
            help="A link to the source repository (on GitHub, BitBucket etcetera). A source repository makes it easier for others collaberate with you on model development.">
        </c-input>
        <button class="btn btn-primary" type="button" @click="save()">Save</button>
    </div>`,
    components: {
        'c-checkbox': Checkbox,
        'c-input': Input,
        'c-markdown': MarkdownEditor,
        'c-tagger': Tagger,
    },
    mixins: [
        createFormValidator(schema)
    ]
})
export default class Description extends Vue {
    @Prop()
    identifier: string;

    async initializeForm() {
        if (this.identifier) {
            const response = await codebaseAPI.retrieve(this.identifier);
            (<any>this).state = response.data;
        }
    }

    created() {
        this.initializeForm();
    }

    createOrUpdate() {
        const self: any = this;
        if (this.identifier === null) {
            return codebaseAPI.create(self.state);
        } else {
            return codebaseAPI.update(self.state);
        }
    }

    async save() {
        let self: any = this;
        await self.validate();
        return this.createOrUpdate();
    }
}