import os

os.environ['DISPLAY'] = ":0.0"
os.environ['KIVY_WINDOW'] = 'egl_rpi'
from time import sleep

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider
from kivy.animation import Animation

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton
from pidev.kivy.selfupdatinglabel import SelfUpdatingLabel
from pidev.stepper import stepper
from pidev.Joystick import Joystick
from threading import Thread
from time import sleep
from datetime import datetime


time = datetime

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
ADMIN_SCREEN_NAME = 'admin'

class ProjectNameGUI(App):
    def build(self):
        return SCREEN_MANAGER

Window.clearcolor = (1, 1, 1, 1)  # White

class MainScreen(Screen):
    count1 = 0
    count2 = 0

    def pressed(self):
        print("Callback from MainScreen.pressed()")

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'

    def pressed2(self):
        if self.first_button.text == "On":
            self.first_button.text = "Off"
        else:
            self.first_button.text = "On"

    def counter(self):
        self.count1 = self.count1 + 1
        self.counter_button.text = str(self.count1)

    def motor(self):
        if self.motor_responder.text == "On":
            self.motor_responder.text = "Off"
        else:
            self.motor_responder.text = "On"

    def move(self):
        if self.count2 == 0:
            anim = Animation(x=200, y=200, duration=1)
            anim &= Animation(size=(400, 400), duration=1)
            anim.start(self.image)
            self.count2 += 1
        else:
            SCREEN_MANAGER.current = "JoystickScreen"

class secondScreen(Screen):
    count = 0
    def animation(self):
        anim = Animation(x=200, y=200)
        anim.start(self.image)
    def moveback(self):
        if self.count == 0:
            anim = Animation(x=400, y=300, duration=2)
            anim &= Animation(size=(200,200), duration=2)
            anim.start(self.second_image)
            self.count += 1
        else:
            SCREEN_MANAGER.current = MAIN_SCREEN_NAME

class JoystickScreen(Screen):
    joystick1 = Joystick(0, False)
    def start_joy_thread(self):
        Thread(target=self.joy_update).start()
    def joy_update(self):
        while True:
            if self.joystick1.get_button_state(2) == 1:
                self.joystick_pressed.text = "pressed"
                sleep(.1)
            else:
                self.joystick_pressed.text = "not pressed"
                sleep(.1)
            self.joystick_x.text = str(self.joystick1.get_axis('x'))
            self.joystick_y.text = str(-1*(self.joystick1.get_axis('y')))
            self.joystick_x.center_x += 10*(self.joystick1.get_axis("x"))
            self.joystick_y.center_y -= 10*(self.joystick1.get_axis("y"))
            sleep(.05)

class AdminScreen(Screen):
    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()


Builder.load_file('main.kv')
Builder.load_file('secondScreen.kv')
Builder.load_file('JoystickScreen.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(secondScreen(name="secondScreen"))
SCREEN_MANAGER.add_widget(JoystickScreen(name="JoystickScreen"))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))

def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()

if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()