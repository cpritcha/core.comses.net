import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import PeerReview, PeerReviewerFeedback, PeerReviewInvitation, PeerReviewEventLog

logger = logging.getLogger(__name__)


class PeerReviewInvitationForm(forms.ModelForm):
    def save(self, commit=True):
        invitation = super().save(commit)
        invitation.send_email()
        return invitation

    class Meta:
        model = PeerReviewInvitation
        fields = [
            'review',
            'editor',
            'candidate_reviewer',
        ]


class PeerReviewInvitationReplyForm(forms.ModelForm):
    def clean_accepted(self):
        data = self.cleaned_data['accepted']
        if data is None:
            raise forms.ValidationError('Must accept or decline invitation')
        return data

    def save(self, commit=True):
        accepted = self.instance.accepted
        invitation = super().save(commit)

        if invitation.accepted:
            invitation.accept()
        else:
            invitation.decline()

        if invitation.accepted and accepted is None:
            invitation.create_feedback()
        return invitation

    class Meta:
        model = PeerReviewInvitation
        fields = ['accepted']


class CheckCharFieldLengthMixin:
    def _check_char_field_has_content(self, field_name, min_length=10):
        content = self.cleaned_data[field_name]
        if len(content) < min_length:
            raise forms.ValidationError('Field {} must have at least {} characters'.format(
                PeerReviewerFeedback._meta.get_field(field_name).verbose_name, min_length))
        return content


class PeerReviewerFeedbackReviewerForm(CheckCharFieldLengthMixin, forms.ModelForm):
    def clean_recommendation(self):
        recommendation = self.cleaned_data['recommendation']
        if not recommendation:
            raise forms.ValidationError('Recommendation must be selected')
        return recommendation

    def clean_private_reviewer_notes(self):
        return self._check_char_field_has_content(field_name='private_reviewer_notes')

    def clean_narrative_documentation_comments(self):
        return self._check_char_field_has_content(field_name='narrative_documentation_comments')

    def clean_clean_code_comments(self):
        return self._check_char_field_has_content(field_name='clean_code_comments')

    def clean_runnable_comments(self):
        return self._check_char_field_has_content(field_name='runnable_comments')

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.invitation.review.is_complete:
            raise forms.ValidationError('Feedback cannot be updated on a complete review')

        if cleaned_data['reviewer_submitted'] and cleaned_data['recommendation']:
            has_narrative_documentation = cleaned_data['has_narrative_documentation']
            has_clean_code = cleaned_data['has_clean_code']
            is_runnable = cleaned_data['is_runnable']

            checklist_errors = []
            if not has_narrative_documentation:
                checklist_errors.append(_('Recommended releases must have narrative documentation'))
            if not has_clean_code:
                checklist_errors.append(_('Recommended releases must have clean code'))
            if not is_runnable:
                checklist_errors.append(_('Recommended releases must have runnable code'))

            if checklist_errors:
                raise forms.ValidationError([forms.ValidationError(e) for e in checklist_errors])
        return cleaned_data

    def save(self, commit=True):
        feedback = super().save(commit)
        if feedback.reviewer_submitted:
            feedback.reviewer_gave_feedback()
        return feedback

    class Meta:
        model = PeerReviewerFeedback
        fields = [
            'has_narrative_documentation',
            'narrative_documentation_comments',
            'has_clean_code',
            'clean_code_comments',
            'is_runnable',
            'runnable_comments',
            'private_reviewer_notes',
            'reviewer_submitted',
            'recommendation',
        ]
        widgets = {
            'reviewer_submitted': forms.HiddenInput()
        }


class PeerReviewerFeedbackReviewerSaveForm(forms.ModelForm):
    class Meta:
        model = PeerReviewerFeedback
        fields = PeerReviewerFeedbackReviewerForm.Meta.fields
        widgets = PeerReviewerFeedbackReviewerForm.Meta.widgets


class PeerReviewerFeedbackEditorForm(CheckCharFieldLengthMixin, forms.ModelForm):
    def __init__(self, **kwargs):
        if 'instance' in kwargs:
            feedback = kwargs['instance']
            kwargs['initial']['accept'] = feedback.invitation.review.is_complete
        super().__init__(**kwargs)

    accept = forms.BooleanField(label='Accept?')

    def clean_notes_to_author(self):
        return self._check_char_field_has_content('notes_to_author')

    def save(self, commit=True):
        feedback = super().save(commit)
        if self.cleaned_data['accept']:
            feedback.invitation.review.set_complete_status(editor=feedback.invitation.editor)
        else:
            feedback.editor_called_for_revisions()
        return feedback

    class Meta:
        model = PeerReviewerFeedback
        fields = [
            'private_editor_notes',
            'notes_to_author',
            'accept'
        ]
