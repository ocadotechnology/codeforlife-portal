from aimmo.models import Game
from common.models import Class
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.forms import ModelChoiceField, ModelForm, Select


class AddGameForm(ModelForm):
    def __init__(self, classes: QuerySet, *args, **kwargs):
        super(AddGameForm, self).__init__(*args, **kwargs)
        self.fields["game_class"].queryset = classes

    game_class = ModelChoiceField(
        queryset=None, widget=Select, label="Class", required=True
    )

    class Meta:
        model = Game
        fields = [
            "game_class",
        ]

    def clean(self):
        super(AddGameForm, self).clean()
        game_class: Class = self.cleaned_data.get("game_class")

        if not game_class:
            raise ValidationError("An invalid class was entered")

        if Game.objects.filter(game_class=game_class, is_archived=False).exists():
            raise ValidationError("An active game already exists for this class")

        return self.cleaned_data
