from django import forms
from django_json_widget.widgets import JSONEditorWidget

from compyle.proxy import models


class TraceForm(forms.ModelForm):
    """Form for :class:`compyle.proxy.models.Trace`."""

    class Meta:
        model = models.Trace
        fields = [
            "params",
            "headers",
            "payload",
            "authentication",
        ]
        widgets = {
            "params": JSONEditorWidget(width="100%"),
            "headers": JSONEditorWidget(width="100%"),
            "payload": JSONEditorWidget(width="100%"),
        }

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)

        self.fields["params"].initial = {}
        self.fields["headers"].initial = {}
        self.fields["payload"].initial = {}
