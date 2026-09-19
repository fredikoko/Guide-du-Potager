from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from ..styles.themes import Theme

class LoadingSpinner(ModalView):
    def __init__(self, message="Chargement en cours...", **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.7, 0.25)
        self.auto_dismiss = False
        self.background_color = (0, 0, 0, 0.7)

        box = BoxLayout(orientation='vertical', padding=20, spacing=10)
        lbl = Label(
            text=f"[b]{message}[/b]",
            markup=True,
            font_size='16sp',
            color=Theme.TEXT_LIGHT,
            halign='center'
        )
        sub = Label(
            text="Patienter un instant...",
            font_size='13sp',
            color=Theme.PRIMARY_LIGHT,
            halign='center'
        )
        box.add_widget(lbl)
        box.add_widget(sub)
        self.add_widget(box)
