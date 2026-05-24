from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "FinalUI.py"

if __name__ == "__main__":
    app.run(debug=True)


from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.carousel import Carousel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.uix.stencilview import StencilView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics.texture import Texture
from kivy.graphics import Color, RoundedRectangle, PushMatrix, PopMatrix, Rotate, Line
from kivy.clock import Clock

import json
import os
import cv2
import time
import re
import mysql.connector
import requests



Window.size = (360, 640)
Window.clearcolor = (0.95, 0.95, 0.95, 1)

ICON_TARGETS = {
    "home.png": "mainpage",
    "calendar.png": "schedule",
    "event.png": "events",
    "file.png": "status",
    "bell.png": "settings",
    "location.png": "location",
    "person.png": "profile",
    "user.png": "status",
    "wallet.png": "wallet",
    "money.png": "payment",
    "inbox.png": "inbox",
    "logout.png": "login",
}



class IconButton(Image):
    def __init__(self, source="", target=None, callback=None, **kwargs):
        super().__init__(**kwargs)

        self.source = source
        self.target = target
        self.callback = callback

        self.allow_stretch = True
        self.keep_ratio = True

        if "size_hint" not in kwargs:
            self.size_hint = (None, None)

        if "size" not in kwargs:
            self.size = (32, 32)

    # DIRECT TOUCH DETECTION
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.opacity = 0.6
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.opacity = 1

            # CALLBACK
            if self.callback:
                self.callback(self)
                return True

            # SCREEN
            if self.target:
                app = App.get_running_app()
                if hasattr(app, "go_screen"):
                    app.go_screen(self.target)

            return True

        return super().on_touch_up(touch)

class ButtonBehaviorBoxLayout(BoxLayout):
    def __init__(self, target=None, callback=None, **kwargs):
        super().__init__(**kwargs)

        self.target = target
        self.callback = callback

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.opacity = 0.7
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.opacity = 1

            # CALLBACK
            if self.callback:
                self.callback(self)
                return True

            # TARGET
            if self.target:
                app = App.get_running_app()
                if hasattr(app, "go_screen"):
                    app.go_screen(self.target)

            return True

        return super().on_touch_up(touch)
    
class TouchBlocker(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sidebar = None

    def on_touch_down(self, touch):
        # Sidebar mode
        if self.sidebar and getattr(self.sidebar, "is_open", False):
            if self.sidebar.collide_point(*touch.pos):
                return self.sidebar.on_touch_down(touch)
            return True  # Block touches outside sidebar

        # Normal mode
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.sidebar and getattr(self.sidebar, "is_open", False):
            if self.sidebar.collide_point(*touch.pos):
                return self.sidebar.on_touch_move(touch)
            return True

        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.sidebar and getattr(self.sidebar, "is_open", False):
            if self.sidebar.collide_point(*touch.pos):
                return self.sidebar.on_touch_up(touch)
            return True

        return super().on_touch_up(touch)

# ================= BUTTON STYLE =================
def blue_button(text):
    return Button(
        text=text,
        size_hint=(1, None),
        height=48,
        background_normal='',
        background_color=(45/255, 108/255, 223/255, 1),
        color=(1, 1, 1, 1)
    )


# ================= ONBOARD PAGE =================
class Page(BoxLayout):
    def __init__(self, title, subtitle, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10)

        self.add_widget(Widget(size_hint=(1, 0.2)))

        shape = Widget(size_hint=(1, 0.35))

        def draw_logo(*args):
            shape.canvas.clear()
            with shape.canvas:
                PushMatrix()
                cx = shape.center_x + 20
                cy = shape.center_y
                Rotate(angle=-20.51, origin=(cx, cy))
                Color(1, 0.5, 0)
                RoundedRectangle(pos=(cx - 60, cy - 60), size=(70, 70), radius=[10])
                Color(0.5, 0.55, 0.8)
                RoundedRectangle(pos=(cx - 30, cy - 90), size=(70, 70), radius=[10])
                PopMatrix()

        shape.bind(pos=draw_logo, size=draw_logo)
        self.add_widget(shape)

        self.add_widget(Label(text=title, font_size='28sp',
                              color=(0.15, 0.15, 0.15, 1)))

        self.add_widget(Label(text=f"[i]{subtitle}[/i]", markup=True,
                              font_size='16sp',
                              color=(0.5, 0.5, 0.5, 1)))

        self.add_widget(Widget(size_hint=(1, 0.2)))


# ================= FACE SCANNER (UNCHANGED WORKING VERSION) =================
class FaceScanScreen(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        self.alert = Label(
            text="",
            size_hint=(1, None),
            height=30,
            color=(0, 0.7, 0, 1)
        )
        self.add_widget(self.alert)

        self.add_widget(Label(
            text="Face ID Scanner",
            font_size='22sp',
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            height=40
        ))

        self.add_widget(Label(
            text="Center your face inside the oval",
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, None),
            height=25
        ))

        self.img = Image()
        self.add_widget(self.img)

        # ================= FACE DETECTION =================
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )

        # ================= CAMERA FIX =================
        self.capture = None

        # Try multiple camera indexes
        for index in [0, 1, 2]:

            cam = cv2.VideoCapture(index, cv2.CAP_MSMF)

            if cam.isOpened():

                ret, frame = cam.read()

                if ret:
                    self.capture = cam
                    print("WORKING CAMERA:", index)
                    break

                cam.release()

        # fallback
        if self.capture is None:

            self.alert.text = "Camera not detected"
            print("NO CAMERA FOUND")
            return

        # CAMERA SETTINGS
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.scanning = False
        self.eyes_open = False

        self.start_btn = Button(
            text="START FACE SCAN",
            size_hint=(1, None),
            height=50,
            background_normal='',
            background_color=(45/255,108/255,223/255,1)
        )

        self.start_btn.bind(on_press=self.start_scan)
        self.add_widget(self.start_btn)

        Clock.schedule_interval(self.update, 1.0 / 30.0)

    # ================= START =================
    def start_scan(self, instance):

        self.scanning = True
        self.alert.text = "Scanning started..."

    # ================= CAMERA UPDATE =================
    def update(self, dt):

        if not self.capture:
            return

        ret, frame = self.capture.read()

        if not ret:
            self.alert.text = "Cannot read camera"
            return

        frame = cv2.flip(frame, 1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(100, 100)
        )

        h, w = frame.shape[:2]

        cx = w // 2
        cy = h // 2

        # OVAL GUIDE
        cv2.ellipse(
            frame,
            (cx, cy),
            (140, 180),
            0,
            0,
            360,
            (255,255,255),
            2
        )

        # ================= FACE PROCESS =================
        if self.scanning:

            for (x, y, fw, fh) in faces:

                fx = x + fw // 2
                fy = y + fh // 2

                inside = (
                    abs(fx - cx) < 140 and
                    abs(fy - cy) < 180
                )

                if inside:

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + fw, y + fh),
                        (0,255,0),
                        2
                    )

                    face_gray = gray[y:y+fh, x:x+fw]

                    eyes = self.eye_cascade.detectMultiScale(
                        face_gray,
                        scaleFactor=1.1,
                        minNeighbors=7
                    )

                    # EYES OPEN
                    if len(eyes) >= 2:

                        self.alert.text = "Blink to verify"

                        self.eyes_open = True

                        for (ex, ey, ew, eh) in eyes:

                            cv2.rectangle(
                                frame,
                                (x+ex, y+ey),
                                (x+ex+ew, y+ey+eh),
                                (255,255,0),
                                1
                            )

                    # BLINK DETECTED
                    elif self.eyes_open:

                        self.alert.text = "Face Verified Successfully"

                        self.scanning = False
                        self.eyes_open = False

                        Clock.schedule_once(self.success, 1)

                else:

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + fw, y + fh),
                        (0,0,255),
                        2
                    )

        # ================= SHOW FRAME =================
        buf = cv2.flip(frame, 0).tobytes()

        texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]),
            colorfmt='bgr'
        )

        texture.blit_buffer(
            buf,
            colorfmt='bgr',
            bufferfmt='ubyte'
        )

        self.img.texture = texture

    # ================= SUCCESS =================
    def success(self, dt):

        popup = Popup(
            title="Success",
            content=Label(text="Successfully Registered"),
            size_hint=(0.7, 0.3)
        )

        popup.open()

        def next_screen(dt):

            popup.dismiss()

            App.get_running_app().go_screen("mainpage")

        Clock.schedule_once(next_screen, 2)

    # ================= CLOSE CAMERA =================
    def on_stop(self):

        if self.capture:
            self.capture.release()


# ================= LOGIN (RESTORED LOGO + COLORS) =================
class LoginScreen(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=30, spacing=15, **kwargs)

        self.alert = Label(
            text="",
            size_hint=(1, None),
            height=30,
            color=(1, 0, 0, 1)
        )
        self.add_widget(self.alert)

        # ================= LOGO (RESTORED) =================
        logo = Widget(size_hint=(1, 0.35))

        def draw_logo(*args):
            logo.canvas.clear()
            with logo.canvas:
                PushMatrix()

                cx = logo.center_x
                cy = logo.center_y

                Rotate(angle=-20, origin=(cx, cy))

                # orange square
                Color(1, 0.5, 0)
                RoundedRectangle(
                    pos=(cx - 40, cy - 30),
                    size=(60, 60),
                    radius=[12]
                )

                # blue square
                Color(0.5, 0.55, 0.8)
                RoundedRectangle(
                    pos=(cx - 10, cy - 60),
                    size=(60, 60),
                    radius=[12]
                )

                PopMatrix()

        logo.bind(pos=draw_logo, size=draw_logo)
        self.add_widget(logo)

        # ================= TITLE =================
        self.add_widget(Label(
            text="Login or Sign Up",
            font_size='22sp',
            color=(0.15, 0.15, 0.15, 1)
        ))

        self.add_widget(Label(
            text="Please select your preferred method",
            font_size='14sp',
            color=(0.5, 0.5, 0.5, 1)
        ))

        # ================= BUTTONS =================
        login_btn = blue_button("Continue to Login")
        login_btn.bind(on_press=self.open_popup)
        self.add_widget(login_btn)

        signup_btn = blue_button("Sign Up")
        signup_btn.bind(on_press=self.go_create)
        self.add_widget(signup_btn)

    # ================= OPEN LOGIN POPUP =================
    def open_popup(self, instance):

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.popup_id = TextInput(
            hint_text="ID NUMBER",
            multiline=False
        )

        self.popup_pass = TextInput(
            hint_text="PASSWORD",
            password=True,
            multiline=False
        )

        layout.add_widget(self.popup_id)
        layout.add_widget(self.popup_pass)

        btn = blue_button("LOGIN")
        btn.bind(on_press=self.check_login)

        layout.add_widget(btn)

        self.popup = Popup(
            title="Login",
            content=layout,
            size_hint=(0.8, 0.4)
        )

        self.popup.open()

    # ================= LOGIN FUNCTION (FIXED) =================
    def check_login(self, instance):

        app = App.get_running_app()

        uid = self.popup_id.text.strip().replace("-", "")
        pw = self.popup_pass.text.strip()

        if not uid or not pw:
            Popup(
                title="Error",
                content=Label(text="Fill all fields"),
                size_hint=(0.7, 0.3)
            ).open()
            return

        try:
            user = app.db.login_user(uid, pw)

            if user:
                self.popup.dismiss()

                # ✅ FIXED MAPPING
                app.current_user = user[1]       # NAME
                app.current_user_id = user[0]     # ID

                popup = Popup(
                    title="Success",
                    content=Label(text=f"Welcome {app.current_user}!"),
                    size_hint=(0.7, 0.3)
                )
                popup.open()

                def go(dt):
                    popup.dismiss()
                    app.go_screen("mainpage")

                Clock.schedule_once(go, 1.2)

            else:
                self.popup.dismiss()

                Popup(
                    title="Error",
                    content=Label(text="Invalid ID or Password"),
                    size_hint=(0.7, 0.3)
                ).open()

        except Exception as e:
            Popup(
                title="Database Error",
                content=Label(text=str(e)),
                size_hint=(0.8, 0.4)
            ).open()

    # ================= GO TO SIGNUP =================
    def go_create(self, instance):
        App.get_running_app().sm.current = "create"
# ================= CREATE ACCOUNT (RESTORED COLORS + BACK + ALERT) =================
class CreateAccountScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=30, spacing=12)

        self.alert = Label(
            text="",
            color=(1, 0, 0, 1),
            size_hint=(1, None),
            height=20
        )
        self.add_widget(self.alert)

        self.add_widget(Label(
            text="Create Account",
            color=(0.15, 0.15, 0.15, 1),
            font_size=24
        ))

        def input_box(hint, password=False):
            box = BoxLayout(size_hint=(1, None), height=45)
            ti = TextInput(hint_text=hint, password=password, multiline=False)
            box.add_widget(ti)
            box.textinput = ti
            return box
        

        self.name = input_box("NAME")
        self.contact = input_box("CONTACT")
        self.idnum = input_box("ID NUMBER")
        self.password = BoxLayout(size_hint=(1, None), height=45, spacing=5)

        self.password.textinput = TextInput(
            hint_text="PASSWORD",
            password=True,
            multiline=False
        )

        toggle_btn = Button(
            text="Show",
            size_hint=(None, 1),
            width=70
        )

        toggle_btn.bind(on_press=self.toggle_password)

        self.password.add_widget(self.password.textinput)
        self.password.add_widget(toggle_btn)
        self.address = input_box("ADDRESS")

        self.contact.textinput.bind(text=self.limit_contact)
        self.idnum.textinput.bind(text=self.limit_id)

        self.add_widget(self.name)
        self.add_widget(self.contact)
        self.add_widget(self.idnum)
        self.add_widget(self.password)
        self.add_widget(self.address)

        btn = blue_button("Sign In")
        btn.bind(on_press=self.register)
        self.add_widget(btn)

        # BACK BUTTON RESTORED
        back = Button(
            text="Back",
            size_hint=(1, None),
            height=45,
            background_normal='',
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back.bind(on_press=lambda x: setattr(App.get_running_app().sm, "current", "login"))
        self.add_widget(back)
    
    def limit_contact(self, instance, value):
        # numbers only + max 11 digits
        filtered = ''.join(filter(str.isdigit, value))[:11]

        if value != filtered:
            instance.text = filtered


    def limit_id(self, instance, value):
        # keep numbers only
        numbers = ''.join(filter(str.isdigit, value))

        # limit to 8 digits only
        numbers = numbers[:8]

        # auto format: XX-XXXXXX
        if len(numbers) > 2:
            formatted = numbers[:2] + "-" + numbers[2:]
        else:
            formatted = numbers

        # avoid infinite loop
        if instance.text != formatted:
            instance.text = formatted

    def toggle_password(self, instance):
        # switch show/hide password
        self.password.textinput.password = not self.password.textinput.password

        # optional icon change (if you want later)
        if self.password.textinput.password:
            instance.text = "Show"
        else:
            instance.text = "Hide"

    def register(self, instance):
        app = App.get_running_app()
        users = app.load_users()

        uid = self.idnum.textinput.text.replace("-", "").strip()
        name = self.name.textinput.text.strip()
        contact = self.contact.textinput.text.strip()
        password = self.password.textinput.text.strip()
        address = self.address.textinput.text.strip()

        # ================= EMPTY FIELDS =================
        if not uid or not name or not contact or not password or not address:
            self.alert.text = "Fill all fields"
            return

        # ================= NAME VALIDATION =================
        # Only letters and spaces allowed
        if not re.fullmatch(r"[A-Za-z ]+", name):
            self.alert.text = "Name must contain letters only"
            return

        # Minimum name length
        if len(name) < 3:
            self.alert.text = "Name is too short"
            return

        # ================= CONTACT VALIDATION =================
        # Numbers only
        if not contact.isdigit():
            self.alert.text = "Contact must be numbers only"
            return

        # Philippine contact length
        if len(contact) != 11:
            self.alert.text = "Contact must be 11 digits"
            return

        # ================= ID NUMBER VALIDATION =================
        if not uid.isdigit():
            self.alert.text = "ID Number must be numbers only"
            return

        # Check duplicate ID
        if uid in users:
            self.alert.text = "ID Number already exists"
            return

        # ================= PASSWORD VALIDATION =================
        if len(password) < 6:
            self.alert.text = "Password must be at least 6 characters"
            return

        # ================= ADDRESS VALIDATION =================
        if len(address) < 1:
            self.alert.text = "Address is too short"
            return

        # ================= SAVE USER =================
        app.db.add_user(
            uid,
            name.title(),
            contact,
            password,
            address
        )

        app.save_users(users)
        app.current_user = name.title()

        # CLEAR ALERT
        self.alert.text = ""

        # GO TO FACE SCAN
        app.sm.current = "facescan"

# ================= SIDEBAR ===================
class Sidebar(StencilView, FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # IMPORTANT
        self.is_open = False
        self.disabled = True

        self.size_hint = (0.78, 1)
        self.pos_hint = {"x": -0.78, "y": 0}

        # ===== WHITE PANEL =====
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[0, 12, 12, 0]
            )

        self.bind(pos=self.update_bg, size=self.update_bg)

        # ================= ROOT =================
        root = BoxLayout(
            orientation="vertical",
            padding=[14, 8, 14, 10],
            spacing=6,
            size_hint=(1, 1)
        )
        self.add_widget(root)

        # ================= TOP =================
        top = BoxLayout(
            size_hint=(1, None),
            height=30
        )

        menu = Image(
            source="menu.png",
            size_hint=(None, None),
            size=(18, 18)
        )

        title = Label(
            text="Menu",
            color=(0, 0, 0, 1),
            font_size="11sp",
            halign="left",
            valign="middle"
        )
        title.bind(
            size=lambda s, a: setattr(s, "text_size", s.size)
        )

        top.add_widget(menu)
        top.add_widget(title)
        root.add_widget(top)

        # ================= LOGO =================
        logo_box = BoxLayout(
            size_hint=(1, None),
            height=55,
            spacing=8
        )

        logo = Widget(
            size_hint=(None, None),
            size=(40, 40)
        )

        def draw_logo(*args):
            logo.canvas.clear()
            with logo.canvas:
                PushMatrix()

                cx = logo.center_x
                cy = logo.center_y

                Rotate(
                    angle=-20,
                    origin=(cx, cy)
                )

                Color(1, 0.5, 0)
                RoundedRectangle(
                    pos=(cx - 18, cy - 10),
                    size=(28, 28),
                    radius=[6]
                )

                Color(0.5, 0.55, 0.8)
                RoundedRectangle(
                    pos=(cx - 6, cy - 22),
                    size=(28, 28),
                    radius=[6]
                )

                PopMatrix()

        logo.bind(pos=draw_logo, size=draw_logo)

        txt = Label(
            text="[b]Forever[/b]\nYoung",
            markup=True,
            color=(0, 0, 0, 1),
            font_size="12sp",
            halign="left",
            valign="middle"
        )
        txt.bind(
            size=lambda s, a: setattr(s, "text_size", s.size)
        )

        logo_box.add_widget(logo)
        logo_box.add_widget(txt)

        root.add_widget(logo_box)

        # ================= MENU LABEL =================
        main_menu = Label(
            text="Main menu",
            size_hint=(1, None),
            height=22,
            color=(0, 0, 0, 1),
            font_size="11sp",
            halign="left",
            valign="middle"
        )
        main_menu.bind(
            size=lambda s, a: setattr(s, "text_size", s.size)
        )
        root.add_widget(main_menu)

        # ================= MAIN ITEMS =================
        items = [
            ("home.png", "Home", "mainpage"),
            ("calendar.png", "Schedule", "schedule"),
            ("file.png", "Status", "status"),
            ("location.png", "Location", "location"),
            ("event.png", "Events", "events"),
        ]

        for icon, text, screen in items:
            root.add_widget(
                self.menu_item(icon, text, screen)
            )

        # ================= SETTINGS =================
        settings_lbl = Label(
            text="Settings & Privacy",
            size_hint=(1, None),
            height=24,
            color=(0, 0, 0, 1),
            font_size="11sp",
            bold=True,
            halign="left",
            valign="middle"
        )
        settings_lbl.bind(
            size=lambda s, a: setattr(s, "text_size", s.size)
        )

        root.add_widget(settings_lbl)

        root.add_widget(
            self.menu_item(
                "bell.png",
                "Settings",
                "settings"
            )
        )

        # ================= ACCOUNT =================
        account_lbl = Label(
            text="Account",
            size_hint=(1, None),
            height=24,
            color=(0, 0, 0, 1),
            font_size="11sp",
            bold=True,
            halign="left",
            valign="middle"
        )
        account_lbl.bind(
            size=lambda s, a: setattr(s, "text_size", s.size)
        )

        root.add_widget(account_lbl)

        root.add_widget(
            self.menu_item(
                "person.png",
                "My Profile",
                "profile"
            )
        )

        # PUSH BOTTOM DOWN
        root.add_widget(Widget())

        # ================= BOTTOM =================
        bottom = BoxLayout(
            size_hint=(1, None),
            height=40,
            spacing=8
        )

        user = Image(
            source="user.png",
            size_hint=(None, None),
            size=(18, 18)
        )

        app = App.get_running_app()

        username = "Guest"

        if hasattr(app, "current_user"):
            if app.current_user:
                username = app.current_user

        self.name_label = Label(
            text=username,
            color=(0, 0, 0, 1),
            font_size="9sp",
            halign="left",
            valign="middle"
        )
        self.name_label.bind(
            size=lambda s, a: setattr(s, "text_size", s.size)
        )


        logout = IconButton(
            source="logout.png",
            size_hint=(None, None),
            size=(18, 18),
            callback=self.logout_user
        )

        bottom.add_widget(user)
        bottom.add_widget(self.name_label)
        bottom.add_widget(logout)

        root.add_widget(bottom)

    # =====================================================
    # TOUCH BLOCKING
    # =====================================================
    def on_touch_down(self, touch):
        if self.disabled:
            return False
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.disabled:
            return False
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.disabled:
            return False
        return super().on_touch_up(touch)

    # =====================================================
    # MENU ITEM
    # =====================================================
    def menu_item(self, icon_file, text, screen):
        row = ButtonBehaviorBoxLayout(
            target=screen,
            size_hint=(1, None),
            height=34,
            spacing=8
        )

        def go(instance):
            self.navigate(screen)

        row.callback = go

        ic = IconButton(
            source=icon_file,
            size_hint=(None, None),
            size=(16, 16),
            callback=go
        )

        label = Label(
            text=text,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            font_size="10sp"
        )
        label.bind(size=lambda s, a: setattr(s, "text_size", s.size))

        arrow = Label(
            text=">",
            color=(0.4, 0.4, 0.4, 1),
            size_hint=(None, 1),
            width=20
        )

        row.add_widget(ic)
        row.add_widget(label)
        row.add_widget(arrow)

        return row

    # =====================================================
    # BACKGROUND UPDATE
    # =====================================================
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    # =====================================================
    # NAVIGATION
    # =====================================================
    def navigate(self, screen):
        app = App.get_running_app()

        if hasattr(app, "sm"):
            app.sm.current = screen

        # close sidebar after navigation
        self.is_open = False
        self.disabled = True

        Animation(pos_hint={"x": -0.78, "y": 0}, d=0.22).start(self)

    def logout_user(self, instance):
            app = App.get_running_app()

            # close sidebar first
            self.is_open = False
            self.disabled = True

            Animation(
                pos_hint={"x": -0.78, "y": 0},
                d=.22
            ).start(self)

            # go to login screen
            app.sm.current = "login"

# ================= DASHBOARD =================
class MainPageExact(FloatLayout):

    # ================= LOAD NOTIFICATIONS =================
    def load_notifications(self):

        app = App.get_running_app()

        user_id = getattr(app, "current_user_id", None)

        if not user_id:
            return "No notifications"

        try:
            notes = app.db.get_notifications(user_id)

            if not notes:
                return "No notifications"

            return "\n\n".join([
                f"• {n[0]}"
                for n in notes
            ])

        except Exception as e:
            print("Notification error:", e)
            return "No notifications"

    # ================= REALTIME UPDATE =================
    def update_notifications_realtime(self, dt):
        try:

            app = App.get_running_app()

            user_id = getattr(
                app,
                "current_user_id",
                None
            )

            if not user_id:
                return

            notes = app.db.get_notifications(user_id)

            if not notes:

                text = "No notifications"

            else:

                text = ""

                for note in notes:

                    message = str(note[0])
                    date = str(note[1])

                    text += f"• {message}\n"
                    text += f"[size=11]{date}[/size]\n\n"

            if hasattr(self, "notif_label"):

                # update instantly
                self.notif_label.text = text

        except Exception as e:

            print("Realtime notification error:", e)

    # ================= INIT =================
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.overlay = FloatLayout(size_hint=(1, 1))
        self.add_widget(self.overlay)

        self.main_layout = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10,
            size_hint=(1, 1)
        )

        self.overlay.add_widget(self.main_layout)

        # ================= BACKDROP =================
        self.backdrop = Button(
            size_hint=(1, 1),
            opacity=0,
            background_normal='',
            background_color=(0, 0, 0, 0.35),
            disabled=True
        )

        self.backdrop.bind(on_release=self.close_sidebar)

        self.overlay.add_widget(self.backdrop)

        # ================= SIDEBAR =================
        self.sidebar = Sidebar()

        self.sidebar.size_hint = (0.78, 1)

        self.sidebar.pos_hint = {
            "x": -0.78,
            "y": 0
        }

        self.overlay.add_widget(self.sidebar)

        self.sidebar_open = False
        self.notif_panel = None

        self.build_ui()

    # ================= UI =================
    def build_ui(self):

        self.main_layout.clear_widgets()

        # ================= HEADER =================
        top = BoxLayout(
            size_hint=(1, None),
            height=50,
            spacing=10,
            padding=[5, 5, 5, 5]
        )

        # ================= MENU =================
        menu = IconButton(
            source='menu.png',
            size_hint=(None, None),
            size=(30, 30)
        )

        def open_menu(instance):
            self.toggle_sidebar()

        menu.callback = open_menu

        # ================= TITLE =================
        title = Label(
            text="AgaPay",
            color=(0, 0, 0, 1),
            bold=True
        )

        # ================= BELL =================
        bell = IconButton(
            source='bell.png',
            size_hint=(None, None),
            size=(30, 30)
        )

        def open_bell(instance):

            self.show_notifications(instance)

            Clock.unschedule(
                self.update_notifications_realtime
            )

            Clock.schedule_interval(
                self.update_notifications_realtime,
                2
            )

            self.update_notifications_realtime(0)

        bell.callback = open_bell

        top.add_widget(menu)
        top.add_widget(title)
        top.add_widget(bell)

        self.main_layout.add_widget(top)

        # ================= WELCOME =================
        app = App.get_running_app()

        username = getattr(
            app,
            "current_user",
            "Guest"
        )

        self.welcome = Button(
            text="Welcome! " + str(username),
            font_size=14,
            size_hint=(1, None),
            height=50,
            background_normal='',
            background_color=(1, 0.6, 0.2, 1),
            color=(0, 0, 0, 1)
        )

        self.main_layout.add_widget(self.welcome)

        # ================= INFO BOX =================
        info = BoxLayout(
            size_hint=(1, None),
            height=90,
            spacing=10,
            padding=10
        )

        info.add_widget(
            Image(
                source='person.png',
                size_hint=(None, 1),
                width=60
            )
        )

        txt = Label(
            text="Please approach the counter when your number is called.",
            color=(0, 0, 0, 1),
            halign='left',
            valign='middle',
            font_size=12,
            size_hint=(1, None)
        )

        txt.bind(
            width=lambda s, w:
            setattr(s, 'text_size', (w, None))
        )

        txt.bind(
            texture_size=lambda s, _:
            setattr(s, 'height', s.texture_size[1])
        )

        info.add_widget(txt)

        self.main_layout.add_widget(info)

        # ================= SPACER =================
        self.main_layout.add_widget(Widget())

        # ================= NAVBAR =================
        nav = BoxLayout(
            size_hint=(1, None),
            height=78,
            padding=[8, 8, 8, 8],
            spacing=8
        )

        with nav.canvas.before:
            Color(45/255, 108/255, 223/255, 1)

            nav.bg = RoundedRectangle(
                pos=nav.pos,
                size=nav.size,
                radius=[14]
            )

        def update_nav_bg(*args):
            nav.bg.pos = nav.pos
            nav.bg.size = nav.size

        nav.bind(
            pos=update_nav_bg,
            size=update_nav_bg
        )

        icons = [
            ('home.png', 'mainpage'),
            ('calendar.png', 'schedule'),
            ('event.png', 'events'),
            ('user.png', 'status'),
        ]

        for img, screen in icons:

            nav_btn = ButtonBehaviorBoxLayout(
                orientation='vertical',
                size_hint=(1, 1),
                spacing=4,
                padding=[0, 2, 0, 2]
            )

            def go_screen(instance, scr=screen):
                App.get_running_app().go_screen(scr)

            nav_btn.callback = go_screen

            icon = IconButton(
                source=img,
                size_hint=(None, None),
                size=(28, 28),
                callback=go_screen
            )

            icon_wrap = AnchorLayout(
                anchor_x='center',
                anchor_y='center',
                size_hint=(1, None),
                height=36
            )

            icon_wrap.add_widget(icon)

            label = Label(
                text=screen.capitalize(),
                font_size='10sp',
                color=(1, 1, 1, 1),
                size_hint=(1, None),
                height=16,
                halign='center',
                valign='middle'
            )

            label.bind(
                size=lambda s, a:
                setattr(s, 'text_size', s.size)
            )

            nav_btn.add_widget(icon_wrap)
            nav_btn.add_widget(label)

            nav.add_widget(nav_btn)

        self.main_layout.add_widget(nav)

    # ================= SIDEBAR =================
    def toggle_sidebar(self, instance=None):

        if self.sidebar_open:
            self.close_sidebar()
        else:
            self.open_sidebar()

    def open_sidebar(self):

        self.sidebar_open = True

        self.sidebar.disabled = False
        self.backdrop.disabled = False

        Animation(
            pos_hint={"x": 0, "y": 0},
            d=0.25
        ).start(self.sidebar)

        Animation(
            opacity=1,
            d=0.25
        ).start(self.backdrop)

    def close_sidebar(self, instance=None):

        self.sidebar_open = False

        self.sidebar.disabled = True

        Animation(
            pos_hint={"x": -0.78, "y": 0},
            d=0.25
        ).start(self.sidebar)

        anim = Animation(
            opacity=0,
            d=0.25
        )

        def disable_backdrop(*args):
            self.backdrop.disabled = True

        anim.bind(
            on_complete=disable_backdrop
        )

        anim.start(self.backdrop)

    # ================= SHOW NOTIFICATIONS =================
    def show_notifications(self, instance):

        if self.notif_panel and self.notif_panel.parent:

            Clock.unschedule(
                self.update_notifications_realtime
            )

            self.overlay.remove_widget(
                self.notif_panel
            )

            self.notif_panel = None

            return

        self.notif_panel = self.create_notification_panel()

        self.overlay.add_widget(
            self.notif_panel
        )

    # ================= CREATE PANEL =================
    def create_notification_panel(self):

        panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, None),
            height=300,
            pos_hint={
                'center_x': 0.5,
                'top': 0.98
            },
            padding=10,
            spacing=10
        )

        with panel.canvas.before:

            Color(0, 0, 0, 0.9)

            panel.bg = RoundedRectangle(
                pos=panel.pos,
                size=panel.size,
                radius=[12]
            )

        def update_bg(*args):

            panel.bg.pos = panel.pos
            panel.bg.size = panel.size

        panel.bind(
            pos=update_bg,
            size=update_bg
        )

        # ================= TITLE =================
        panel.add_widget(
            Label(
                text="NOTIFICATIONS",
                color=(1, 1, 1, 1),
                bold=True,
                size_hint=(1, None),
                height=30
            )
        )

        # ================= SCROLL =================
        scroll = ScrollView()

        self.notif_label = Label(

            text=self.load_notifications(),
            color=(1,1,1,1),
            markup=True,
            size_hint_y=None,
            valign="top",
            halign="left"
        )

        self.notif_label.bind(
            width=lambda s, w:
            setattr(s, 'text_size', (w, None))
        )

        self.notif_label.bind(
            texture_size=lambda s, v:
            setattr(s, 'height', v[1])
        )

        scroll.add_widget(self.notif_label)

        panel.add_widget(scroll)

        # ================= CLOSE =================
        close = Button(
            text="Close",
            size_hint=(1, None),
            height=40,
            background_normal='',
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )

        def close_panel(instance):

            Clock.unschedule(
                self.update_notifications_realtime
            )

            if panel.parent:
                self.overlay.remove_widget(panel)

            self.notif_panel = None

        close.bind(on_release=close_panel)

        panel.add_widget(close)

        return panel

class BaseMenuScreen(FloatLayout):
    def __init__(self, title="PAGE", **kwargs):
        super().__init__(**kwargs)

        # ================= ROOT OVERLAY =================
        self.overlay = FloatLayout(size_hint=(1, 1))
        self.add_widget(self.overlay)

        # ================= MAIN CONTENT =================
        self.content = BoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10,
            size_hint=(1, 1)
        )
        self.overlay.add_widget(self.content)

        # ================= DARK BACKDROP =================
        self.backdrop = Button(
            size_hint=(1, 1),
            opacity=0,
            disabled=True,
            background_normal='',
            background_color=(0, 0, 0, 0.35)
        )
        self.backdrop.bind(on_release=self.close_sidebar)
        self.overlay.add_widget(self.backdrop)

        # ================= SIDEBAR =================
        self.sidebar = Sidebar()
        self.sidebar.size_hint = (0.78, 1)
        self.sidebar.pos_hint = {"x": -0.78, "y": 0}
        self.overlay.add_widget(self.sidebar)

        # ================= STATE =================
        self.sidebar_open = False
        self.notif_panel = None

        # ================= HEADER =================
        self.build_header(title)

    # =========================================================
    # HEADER
    # =========================================================
    def build_header(self, title):
        top = BoxLayout(
            size_hint=(1, None),
            height=50,
            spacing=10,
            padding=[5, 5, 5, 5]
        )

        # ================= MENU BUTTON =================
        menu = IconButton(
            source='menu.png',
            size_hint=(None, None),
            size=(30, 30)
        )

        def open_menu(instance):
            self.toggle_sidebar()

        menu.callback = open_menu

        # ================= TITLE =================
        center_title = Label(
            text=title,
            color=(0, 0, 0, 1),
            bold=True
        )

        # ================= BELL BUTTON =================
        bell = IconButton(
            source='bell.png',
            size_hint=(None, None),
            size=(30, 30)
        )

        def open_notifications(instance):
            self.show_notifications(instance)

        bell.callback = open_notifications

        # ADD
        top.add_widget(menu)
        top.add_widget(center_title)
        top.add_widget(bell)

        self.content.add_widget(top)


    # =========================================================
    # SIDEBAR
    # =========================================================
    def toggle_sidebar(self, instance=None):
        if self.sidebar_open:
            self.close_sidebar()
        else:
            self.open_sidebar()

    def open_sidebar(self):
        self.sidebar_open = True
        self.sidebar.disabled = False
        self.backdrop.disabled = False

        Animation(
            pos_hint={"x": 0, "y": 0},
            d=0.25
        ).start(self.sidebar)

        Animation(
            opacity=1,
            d=0.25
        ).start(self.backdrop)

    def close_sidebar(self, instance=None):
        self.sidebar_open = False
        self.sidebar.disabled = True

        Animation(
            pos_hint={"x": -0.78, "y": 0},
            d=0.25
        ).start(self.sidebar)

        anim = Animation(
            opacity=0,
            d=0.25
        )

        def disable_backdrop(*args):
            self.backdrop.disabled = True

        anim.bind(on_complete=disable_backdrop)
        anim.start(self.backdrop)

    # =========================================================
    # NOTIFICATIONS
    # =========================================================
    def show_notifications(self, instance):
        if self.notif_panel and self.notif_panel.parent:
            self.overlay.remove_widget(self.notif_panel)
            self.notif_panel = None
            return

        self.notif_panel = self.create_notification_panel()
        self.overlay.add_widget(self.notif_panel)

    def create_notification_panel(self):
        panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.9, None),
            height=300,
            pos_hint={
                'center_x': 0.5,
                'top': 0.98
            },
            padding=10,
            spacing=10
        )

        with panel.canvas.before:
            Color(0, 0, 0, 0.9)
            panel.bg = RoundedRectangle(
                pos=panel.pos,
                size=panel.size,
                radius=[12]
            )

        def update_bg(*args):
            panel.bg.pos = panel.pos
            panel.bg.size = panel.size

        panel.bind(pos=update_bg, size=update_bg)

        panel.add_widget(
            Label(
                text="NOTIFICATIONS",
                color=(1, 1, 1, 1),
                bold=True,
                size_hint=(1, None),
                height=30
            )
        )

        panel.add_widget(
            Label(
                text="• No new notifications\n• Queue updates will appear here",
                color=(1, 1, 1, 1)
            )
        )

        close = Button(
            text="Close",
            size_hint=(1, None),
            height=40,
            background_normal='',
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )

        def close_panel(instance):
            if panel.parent:
                self.overlay.remove_widget(panel)
            self.notif_panel = None

        close.bind(on_release=close_panel)

        panel.add_widget(close)

        return panel

class ScheduleScreenUI(BaseMenuScreen):
    def __init__(self, **kwargs):
        super().__init__(title="SCHEDULE", **kwargs)

        # OPTIONAL: just a placeholder or leave empty
        self.content.add_widget(Label(
            text="",
            size_hint=(1, 1)
        ))


class EventsScreenUI(BaseMenuScreen):
    def __init__(self, **kwargs):
        super().__init__(title="EVENTS", **kwargs)

        self.container = BoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint=(1, None),
            padding=5
        )

        self.container.bind(minimum_height=self.container.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.container)

        self.content.add_widget(scroll)

        self.container.add_widget(self.event_card("CHECKUP PROGRAM"))
        self.container.add_widget(self.event_card("TULONG PROGRAM"))

    def event_card(self, title):
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=140,
            padding=10
        )

        with card.canvas.before:
            Color(0.8, 0.9, 0.85, 1)
            rect = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[12]
            )

        card.bind(
            pos=lambda s, a: setattr(rect, 'pos', s.pos),
            size=lambda s, a: setattr(rect, 'size', s.size)
        )

        card.add_widget(Label(text=title, bold=True, color=(0, 0, 0, 1)))
        card.add_widget(Label(text="LOCATION:", color=(0, 0, 0, 1)))
        card.add_widget(Label(text="DATE:", color=(0, 0, 0, 1)))
        card.add_widget(Label(text="TIME:", color=(0, 0, 0, 1)))

        return card

    def show_notifications(self, instance):
        if hasattr(self, "notif_panel") and self.notif_panel in self.overlay.children:
            self.overlay.remove_widget(self.notif_panel)
            return

        panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.9,None),
            height=300,
            pos_hint={'center_x':0.5,'top':1},
            padding=10
        )

        with panel.canvas.before:
            Color(0,0,0,0.9)
            bg = RoundedRectangle(pos=panel.pos,size=panel.size,radius=[12])

        panel.bind(pos=lambda s,a:setattr(bg,'pos',s.pos))
        panel.bind(size=lambda s,a:setattr(bg,'size',s.size))

        panel.add_widget(Label(text="NOTIFICATIONS", color=(1,1,1,1)))

        close = Button(text="Close", size_hint=(1,None), height=40)
        close.bind(on_release=lambda x:self.overlay.remove_widget(panel))
        panel.add_widget(close)

        self.overlay.add_widget(panel)

# ================= STATUS SCREEN =================
class StatusScreenUI(BaseMenuScreen):
    def __init__(self, **kwargs):
        super().__init__(title="STATUS", **kwargs)

        self.content.add_widget(Label(
            text="FULENTES, JUNJI",
            color=(0, 0, 0, 1),
            bold=True,
            font_size="18sp",
            size_hint=(1, None),
            height=40
        ))

        grid = BoxLayout(
            orientation='vertical',
            spacing=16,
            size_hint=(1, None),
            height=230
        )

        row1 = BoxLayout(spacing=16)
        row2 = BoxLayout(spacing=16)

        row1.add_widget(self.action_card("inbox.png", "INBOX", "inbox"))
        row1.add_widget(self.action_card("calendar.png", "SCHEDULE", "schedule"))

        row2.add_widget(self.action_card("wallet.png", "WALLET", "wallet"))
        row2.add_widget(self.action_card("money.png", "PAYMENT", "payment"))

        grid.add_widget(row1)
        grid.add_widget(row2)

        self.content.add_widget(grid)

    def action_card(self, icon, title, target):
        def open_target(instance):
            if target in ["schedule", "wallet", "payment", "inbox"]:
                App.get_running_app().go_screen(target)
            else:
                Popup(
                    title=target.capitalize(),
                    content=Label(text=f"{target.capitalize()} page coming soon."),
                    size_hint=(0.7, 0.3)
                ).open()

        btn = ButtonBehaviorBoxLayout(
            orientation='vertical',
            padding=12,
            spacing=8,
            size_hint=(1, None),
            height=95,
            callback=open_target
        )

        with btn.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            btn.bg = RoundedRectangle(
                pos=btn.pos,
                size=btn.size,
                radius=[12]
            )

        btn.bind(
            pos=lambda s, a: setattr(btn.bg, 'pos', s.pos),
            size=lambda s, a: setattr(btn.bg, 'size', s.size)
        )

        img = IconButton(
            source=icon,
            callback=open_target,
            size_hint=(None, None),
            size=(28, 28),
            pos_hint={"center_x": 0.5}
        )

        lbl = Label(
            text=title,
            color=(0, 0, 0, 1),
            bold=True,
            font_size="12sp"
        )

        btn.add_widget(img)
        btn.add_widget(lbl)

        return btn

    # ---------- NAV ----------
    def open_target(self, target):
        app = App.get_running_app()

        if target in ["schedule"]:
            app.go_screen(target)
        else:
            popup = Popup(
                title=target.capitalize(),
                content=Label(text=f"{target.capitalize()} page coming soon."),
                size_hint=(0.7, 0.3)
            )
            popup.open()

    # ---------- HELP ----------
    def show_help(self, instance):
        popup = Popup(
            title="Help",
            content=Label(text="Your claim is ready.\nCheck inbox or payment."),
            size_hint=(0.7, 0.3)
        )
        popup.open()

    # ---------- SIDEBAR ----------
    def toggle_sidebar(self, instance=None):
        if self.sidebar_open:
            self.close_sidebar()
        else:
            self.open_sidebar()

# ================= APP =================
class MyApp(App):
    current_user = None

    class AgaPayDatabase:


        def get_notifications(self, user_id):

            sql = """
            SELECT 
                message,
                created_at
            FROM notifications
            WHERE user_id=%s
            ORDER BY id DESC
            """

            self.cursor.execute(sql, (user_id,))

            return self.cursor.fetchall()
        
        def __init__(self):

            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",      # PUT YOUR MYSQL PASSWORD
                database="agapay"
            )

            self.cursor = self.conn.cursor()

        # ================= ADD USER =================
        def add_user(self, id, name, contact, password, address):

            sql = """
            INSERT INTO users
            (
                id,
                name,
                contact,
                password,
                address
            )
            VALUES (%s, %s, %s, %s, %s)
            """

            values = (
                id ,
                name,
                contact,
                password,
                address
            )

            self.cursor.execute(sql, values)
            self.conn.commit()

        # ================= LOGIN =================
        def login_user(self, id, password):

            sql = """
            SELECT * FROM users
            WHERE id=%s
            AND password=%s
            """

            self.cursor.execute(sql, (id, password))

            return self.cursor.fetchone()

        # ================= CHECK USER =================
        def user_exists(self, id):

            sql = """
            SELECT * FROM users
            WHERE id=%s
            """

            self.cursor.execute(sql, (id,))

            return self.cursor.fetchone()

        # ================= EVENTS =================
        def add_event(self, title, location, date, time):

            sql = """
            INSERT INTO events
            (
                title,
                location,
                date,
                time
            )
            VALUES (%s, %s, %s, %s)
            """

            self.cursor.execute(sql, (
                title,
                location,
                date,
                time
            ))

            self.conn.commit()

        def get_events(self):

            sql = "SELECT * FROM events"

            self.cursor.execute(sql)

            return self.cursor.fetchall()

        # ================= NOTIFICATIONS =================
        def add_notification(self, message):

            sql = """
            INSERT INTO notifications (message)
            VALUES (%s)
            """

            self.cursor.execute(sql, (message,))
            self.conn.commit()

        def get_notifications(self, user_id):
            try:
                sql = """
                SELECT message
                FROM notifications
                WHERE user_id=%s
                ORDER BY id DESC
                LIMIT 20
                """
                self.cursor.execute(sql, (user_id,))
                return self.cursor.fetchall()
            except Exception as e:
                print("DB ERROR:", e)
                return []

    # ================= USER STORAGE =================
    def load_users(self):
        if os.path.exists("users.json"):
            try:
                with open("users.json", "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_users(self, data):
        try:
            with open("users.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Save error:", e)

    # ================= PLACEHOLDER SCREEN =================
    def placeholder_screen(self, name, message=None):
        screen = Screen(name=name)

        layout = BoxLayout(
            orientation="vertical",
            padding=20
        )

        layout.add_widget(Label(
            text=message or f"{name.capitalize()} Page Coming Soon",
            color=(0, 0, 0, 1)
        ))

        back = blue_button("Back to Main")
        back.bind(on_press=lambda x: setattr(self.sm, "current", "mainpage"))

        layout.add_widget(back)
        screen.add_widget(layout)

        return screen

    # ================= BUILD APP =================
    def build(self):
        self.sm = ScreenManager()
        self.db = MyApp.AgaPayDatabase()
        # ---------- MAIN FEATURE SCREENS ----------
        screens = {
            "status": StatusScreenUI(),
            "schedule": ScheduleScreenUI(),
            "events": EventsScreenUI(),
            "login": LoginScreen(),
            "create": CreateAccountScreen(),
            "facescan": FaceScanScreen(),
            "mainpage": MainPageExact(),
        }

        for name, widget in screens.items():
            scr = Screen(name=name)
            scr.add_widget(widget)
            self.sm.add_widget(scr)

        # ---------- ONBOARD ----------
        onboard = Screen(name="onboard")

        layout = BoxLayout(orientation='vertical')
        carousel = Carousel()

        pages = [
            ("Welcome", "AgaPAY"),
            ("Stay Safe", "Secure"),
            ("Start", "Now")
        ]

        for title, subtitle in pages:
            carousel.add_widget(Page(title, subtitle))

        btn = Button(
            text="Get Started",
            size_hint=(1, 0.1),
            background_normal='',
            background_color=(45/255, 108/255, 223/255, 1),
            color=(1, 1, 1, 1)
        )

        btn.bind(
            on_press=lambda x: setattr(self.sm, "current", "login")
        )

        layout.add_widget(carousel)
        layout.add_widget(btn)

        onboard.add_widget(layout)
        self.sm.add_widget(onboard)

        # ---------- PLACEHOLDER PAGES ----------
        placeholders = [
            "location",
            "settings",
            "profile",
            "wallet",
            "payment",
            "inbox"
        ]

        for name in placeholders:
            self.sm.add_widget(self.placeholder_screen(name))

        # ---------- START ----------
        self.sm.current = "onboard"

        return self.sm

    # ================= NAVIGATION =================
    def go_screen(self, screen_name):
        valid_screens = [screen.name for screen in self.sm.screens]

        if screen_name in valid_screens:

            self.sm.current = screen_name

            # FORCE UPDATE DASHBOARD WHEN ENTERING
            if screen_name == "mainpage":
                main = self.sm.get_screen("mainpage").children[0]

                app = self

                username = getattr(app, "current_user", None) or ""

                if hasattr(main, "welcome"):
                    main.welcome.text = "Welcome! " + (username if username else "Guest")

                if hasattr(main.sidebar, "name_label"):
                    main.sidebar.name_label.text = username if username else "Guest"

            self.sm.current = screen_name
    
    def set_current_user(self, name):
        self.current_user = name

        # update dashboard if exists
        if hasattr(self, "sm"):
            try:
                main = self.sm.get_screen("mainpage").children[0]

                if hasattr(main, "welcome"):
                    main.welcome.text = f"Welcome! {name}"

                if hasattr(main, "sidebar") and hasattr(main.sidebar, "name_label"):
                    main.sidebar.name_label.text = name

            except:
                pass


if __name__ == "__main__":
    MyApp().run()
