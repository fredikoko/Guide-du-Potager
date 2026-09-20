from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.properties import ObjectProperty
from .services.auth_service import AuthService
from .screens.login_screen import LoginScreen
from .screens.register_screen import RegisterScreen
from .screens.home_screen import HomeScreen
from .screens.chapter_screen import ChapterScreen
from .screens.tools_screen import ToolsScreen
from .screens.families_screen import FamiliesScreen
from .screens.vegetables_screen import VegetablesScreen
from .screens.diseases_screen import DiseasesScreen
from .screens.insects_screen import InsectsScreen
from .screens.profile_screen import ProfileScreen
from .screens.subscription_screen import SubscriptionScreen
from .screens.calendar_screen import CalendarScreen
from .screens.blog_screen import BlogScreen
from .screens.post_detail_screen import PostDetailScreen
from .screens.about_screen import AboutScreen

from kivy.core.window import Window

class GuidePotagerTropicalApp(App):
    sm = ObjectProperty(None)

    def build(self):
        self.title = "Guide du Potager Tropical"
        self.auth_service = AuthService()
        self.sm = ScreenManager(transition=FadeTransition())

        # Register all application screens
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(ChapterScreen(name='chapter'))
        self.sm.add_widget(CalendarScreen(name='calendar'))
        self.sm.add_widget(BlogScreen(name='blog'))
        self.sm.add_widget(PostDetailScreen(name='post_detail'))
        self.sm.add_widget(ToolsScreen(name='tools'))
        self.sm.add_widget(FamiliesScreen(name='families'))
        self.sm.add_widget(VegetablesScreen(name='vegetables'))
        self.sm.add_widget(DiseasesScreen(name='diseases'))
        self.sm.add_widget(InsectsScreen(name='insects'))
        self.sm.add_widget(ProfileScreen(name='profile'))
        self.sm.add_widget(SubscriptionScreen(name='subscription'))
        self.sm.add_widget(AboutScreen(name='about'))

        # Check authentication on app startup
        if self.auth_service.is_authenticated():
            self.sm.current = 'home'
        else:
            self.sm.current = 'login'

        # Interception du bouton Retour matériel Android (Code 27)
        Window.bind(on_keyboard=self._on_keyboard)

        return self.sm

    def _on_keyboard(self, window, key, *args):
        # 27 correspond à la touche 'Retour' sous Android et Échap sur Desktop
        if key == 27:
            if self.sm and self.sm.current not in ['home', 'login']:
                if self.sm.current == 'register':
                    self.sm.current = 'login'
                elif self.sm.current == 'post_detail':
                    self.sm.current = 'blog'
                elif self.sm.current == 'vegetables':
                    veg_screen = self.sm.get_screen('vegetables')
                    if getattr(veg_screen, 'current_family_id', None) is not None:
                        veg_screen.current_family_id = None
                        veg_screen.current_family_name = None
                        self.sm.current = 'families'
                    else:
                        self.sm.current = 'home'
                else:
                    self.sm.current = 'home'
                return True  # Événement consommé, empêche la fermeture de l'application
        return False

# Alias de compatibilité
GuidePotagerApp = GuidePotagerTropicalApp
