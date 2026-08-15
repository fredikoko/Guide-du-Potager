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

class GuidePotagerApp(App):
    sm = ObjectProperty(None)

    def build(self):
        self.title = "Guide du Potager"
        self.auth_service = AuthService()
        self.sm = ScreenManager(transition=FadeTransition())

        # Register all application screens
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(ChapterScreen(name='chapter'))
        self.sm.add_widget(ToolsScreen(name='tools'))
        self.sm.add_widget(FamiliesScreen(name='families'))
        self.sm.add_widget(VegetablesScreen(name='vegetables'))
        self.sm.add_widget(DiseasesScreen(name='diseases'))
        self.sm.add_widget(InsectsScreen(name='insects'))
        self.sm.add_widget(ProfileScreen(name='profile'))
        self.sm.add_widget(SubscriptionScreen(name='subscription'))

        # Check authentication on app startup
        if self.auth_service.is_authenticated():
            self.sm.current = 'home'
        else:
            self.sm.current = 'login'

        return self.sm
