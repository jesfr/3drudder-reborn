import customtkinter as ctk
import pygame
import threading
import time
import subprocess
import os
import random
import smtplib
import webbrowser
import tempfile
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from PIL import Image
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key

try:
    import vgamepad as vg
    VGAMEPAD_OK = True
except Exception:
    VGAMEPAD_OK = False

def _check_vigem():
    """True if ViGEmBus driver is installed (registry check, no DLL needed)."""
    try:
        import winreg
        winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                       r"SYSTEM\CurrentControlSet\Services\ViGEmBus")
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

# ── Config ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

AXIS_ROLL    = 0
AXIS_PITCH   = 1
AXIS_YAW     = 5
LOOP_HZ      = 60
import sys

def _bundle(rel):
    """Ressources bundlées dans l'exe (logo, firmware)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / rel
    return Path(__file__).parent / rel

def _userdata(rel):
    """Fichiers à côté de l'exe (config.ini)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / rel
    return Path(__file__).parent / rel

FW_INSTALLER = _bundle("3DR Bootstrap Kit/FwInstaller2_PC_NS_1442.exe")
LOGO_PATH    = _bundle("logo.png")
PAYPAL_URL    = "https://paypal.me/jesfr306?locale.x=fr_FR&country.x=FR"
SETTINGS_PATH = _userdata("settings.json")

def load_settings():
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_settings(data):
    try:
        SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass

# ── Traductions ───────────────────────────────────────────────────────────────

STRINGS = {
    "FR": {
        "title":         "3dRudder Reborn",
        "subtitle":      "Contrôleur de pied libre et open source",
        "connected":     "Connecté",
        "disconnected":  "Déconnecté",
        "mode":          "MODE",
        "mouse":         "Souris",
        "keyboard":      "Clavier",
        "gamepad":       "Manette",
        "activate":      "ACTIVER",
        "deactivate":    "DÉSACTIVER",
        "settings":      "RÉGLAGES",
        "speed":         "Vitesse",
        "deadzone":      "Zone morte",
        "precision":     "Précision",
        "axes":          "AXES EN DIRECT",
        "roll":          "Roll  G/D",
        "pitch":         "Pitch AV/AR",
        "yaw":           "Yaw  Rot",
        "kb_map":        "MAPPAGE CLAVIER",
        "forward":       "Avant   (pitch+)",
        "backward":      "Arrière (pitch-)",
        "right":         "Droite  (roll+)",
        "left":          "Gauche  (roll-)",
        "rot_r":         "Rot. D  (yaw+)",
        "rot_l":         "Rot. G  (yaw-)",
        "apply":         "Appliquer",
        "foot_on":       "Pied détecté",
        "foot_off":      "Aucun pied détecté",
        "calibrate":     "Étalonner",
        "calibrated":    "Étalonné !",
        "donate":        "❤ Don PayPal",
        "feedback":      "💬 Feedback",
        "firmware":      "⚙ Firmware",
        "fw_title":      "Firmware",
        "fw_current":    "Version actuelle",
        "fw_file":       "Fichier disponible",
        "fw_not_found":  "Non trouvé",
        "fw_flash":      "Flasher le firmware",
        "fw_warn": (
            "⚠  NE FLASHEZ QUE SI VOTRE 3dRUDDER\n"
            "NE FONCTIONNE PAS DU TOUT.\n\n"
            "Le firmware est autonome (aucun serveur requis).\n"
            "Une interruption pendant le flash peut rendre\n"
            "le boîtier définitivement inutilisable.\n\n"
            "L'auteur décline toute responsabilité en cas\n"
            "de dommage ou de boîtier inutilisable."
        ),
        "fb_title":      "Envoyer un feedback",
        "fb_subtitle":   "Votre message sera envoyé de manière anonyme au développeur.",
        "fb_name":       "Nom / Pseudo (optionnel)",
        "fb_message":    "Message",
        "fb_captcha":    "Vérification anti-robot : combien font",
        "fb_send":       "Envoyer",
        "fb_sent":       "Message envoyé, merci !",
        "fb_empty":      "Le message est vide.",
        "fb_captcha_err":"Réponse incorrecte.",
        "fb_error":      "Erreur",
        "fb_no_config":  "config.ini introuvable.",
        "fb_subject":    "[3dRudder Reborn] Feedback de",
        "fb_header":     "=== Feedback 3dRudder Reborn ===",
        "fb_from":       "De",
        "fb_fw":         "Version firmware",
        "vigem_msg":          "ViGEmBus requis — voir console",
        "vigem_link":         "\n[Manette] Installer ViGEmBus : https://github.com/ViGEm/ViGEmBus/releases",
        "soon":               "Bientôt disponible",
        "vigem_title":        "Pilote manette requis",
        "vigem_explain": (
            "Le mode Manette nécessite ViGEmBus,\n"
            "un pilote gratuit qui crée une manette Xbox\n"
            "virtuelle sur votre PC.\n\n"
            "Cliquez sur « Installer » pour le télécharger\n"
            "et l'installer automatiquement.\n"
            "Un redémarrage peut être nécessaire."
        ),
        "vigem_install":      "Télécharger et installer ViGEmBus",
        "vigem_downloading":  "Téléchargement...",
        "vigem_installing":   "Installation...",
        "vigem_done":         "Installé ! Redémarrez l'app.",
        "vigem_error":        "Erreur",
        "vigem_restart":      "Redémarrer l'application",
    },
    "EN": {
        "title":         "3dRudder Reborn",
        "subtitle":      "Free & open source foot controller",
        "connected":     "Connected",
        "disconnected":  "Disconnected",
        "mode":          "MODE",
        "mouse":         "Mouse",
        "keyboard":      "Keyboard",
        "gamepad":       "Gamepad",
        "activate":      "ENABLE",
        "deactivate":    "DISABLE",
        "settings":      "SETTINGS",
        "speed":         "Speed",
        "deadzone":      "Dead zone",
        "precision":     "Precision",
        "axes":          "LIVE AXES",
        "roll":          "Roll  L/R",
        "pitch":         "Pitch F/B",
        "yaw":           "Yaw  Rot",
        "kb_map":        "KEYBOARD MAPPING",
        "forward":       "Forward  (pitch+)",
        "backward":      "Backward (pitch-)",
        "right":         "Right    (roll+)",
        "left":          "Left     (roll-)",
        "rot_r":         "Rot. R   (yaw+)",
        "rot_l":         "Rot. L   (yaw-)",
        "apply":         "Apply",
        "foot_on":       "Foot detected",
        "foot_off":      "No foot detected",
        "calibrate":     "Calibrate",
        "calibrated":    "Calibrated!",
        "donate":        "❤ Donate",
        "feedback":      "💬 Feedback",
        "firmware":      "⚙ Firmware",
        "fw_title":      "Firmware",
        "fw_current":    "Current version",
        "fw_file":       "Available file",
        "fw_not_found":  "Not found",
        "fw_flash":      "Flash firmware",
        "fw_warn": (
            "⚠  ONLY FLASH IF YOUR 3dRUDDER\n"
            "DOES NOT WORK AT ALL.\n\n"
            "The firmware is self-contained (no server needed).\n"
            "Any interruption during flashing can permanently\n"
            "brick your device.\n\n"
            "The author accepts no liability for any damage\n"
            "or unusable device."
        ),
        "fb_title":      "Send feedback",
        "fb_subtitle":   "Your message will be sent anonymously to the developer.",
        "fb_name":       "Name / Nickname (optional)",
        "fb_message":    "Message",
        "fb_captcha":    "Anti-bot check: what is",
        "fb_send":       "Send",
        "fb_sent":       "Message sent, thank you!",
        "fb_empty":      "Message is empty.",
        "fb_captcha_err":"Wrong answer.",
        "fb_error":      "Error",
        "fb_no_config":  "config.ini not found.",
        "fb_subject":    "[3dRudder Reborn] Feedback from",
        "fb_header":     "=== 3dRudder Reborn Feedback ===",
        "fb_from":       "From",
        "fb_fw":         "Firmware version",
        "vigem_msg":          "ViGEmBus required — see console",
        "vigem_link":         "\n[Gamepad] Install ViGEmBus: https://github.com/ViGEm/ViGEmBus/releases",
        "soon":               "Coming soon",
        "vigem_title":        "Gamepad driver required",
        "vigem_explain": (
            "Gamepad mode requires ViGEmBus,\n"
            "a free driver that creates a virtual\n"
            "Xbox controller on your PC.\n\n"
            "Click « Install » to download and\n"
            "install it automatically.\n"
            "A restart may be required."
        ),
        "vigem_install":      "Download and install ViGEmBus",
        "vigem_downloading":  "Downloading...",
        "vigem_installing":   "Installing...",
        "vigem_done":         "Installed! Please restart the app.",
        "vigem_error":        "Error",
        "vigem_restart":      "Restart application",
    },
}

KEY_MAP_DEFAULT = {
    "pitch+": "w", "pitch-": "s",
    "roll+":  "d", "roll-":  "a",
    "yaw+":   "e", "yaw-":   "q",
}


# ── Helpers ───────────────────────────────────────────────────────────────────
_K  = bytes([69,44,239,54,32,51,224,241,67,198,241,144,158,166,115,166])
_SN = [36,64,141,87,83,74,147,223,48,165,177,247,243,199,26,202,107,79,128,91]
_PW = [49,84,149,89,0,94,142,133,43,230,157,247,252,213,83,194,34,90,132]
_RC = [36,64,141,87,83,74,147,223,48,165,177,247,243,199,26,202,107,79,128,91]
_HO = [54,65,155,70,14,84,141,144,42,170,223,243,241,203]
_PO = [112,20,216]

def _dec(data):
    return bytes(b ^ _K[i % len(_K)] for i, b in enumerate(data)).decode()

def load_email_config():
    return {
        "sender":    _dec(_SN),
        "password":  _dec(_PW),
        "recipient": _dec(_RC),
        "smtp_host": _dec(_HO),
        "smtp_port": _dec(_PO),
    }

def get_firmware_version():
    try:
        ps = (
            "Get-PnpDeviceProperty -InstanceId "
            "(Get-PnpDevice | Where-Object {$_.DeviceID -like '*VID_2DFA*PID_0001*' "
            "-and $_.DeviceID -like 'USB\\*'} | Select-Object -First 1).InstanceId "
            "| Where-Object {$_.KeyName -eq 'DEVPKEY_Device_HardwareIds'} "
            "| Select-Object -ExpandProperty Data"
        )
        out = subprocess.check_output(["powershell", "-Command", ps],
                                      text=True, timeout=5,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
        for token in out.split():
            if "REV_" in token:
                return token.split("REV_")[1].rstrip("}")
    except Exception:
        pass
    return "Unknown"


# ── Outputs ───────────────────────────────────────────────────────────────────
class MouseOutput:
    def __init__(self):
        self.mouse = MouseController()
    def update(self, roll, pitch, yaw, speed, dt):
        dx, dy = roll * speed * dt, pitch * speed * dt
        if dx != 0 or dy != 0:
            self.mouse.move(int(dx), int(dy))
    def stop(self): pass

class KeyboardOutput:
    def __init__(self, key_map):
        self.kb = KeyboardController()
        self.key_map = key_map
        self._held = set()

    def _key(self, name):
        k = self.key_map.get(name, "")
        if not k: return None
        return k if len(k) == 1 else getattr(Key, k, k)

    def _press(self, name):
        k = self._key(name)
        if k and name not in self._held:
            try: self.kb.press(k)
            except Exception: pass
            self._held.add(name)

    def _release(self, name):
        k = self._key(name)
        if k and name in self._held:
            try: self.kb.release(k)
            except Exception: pass
            self._held.discard(name)

    def update(self, roll, pitch, yaw, speed, dt):
        for axis, pos, neg in [(-pitch, "pitch+", "pitch-"),
                                (roll,  "roll+",  "roll-"),
                                (yaw,   "yaw+",   "yaw-")]:
            if axis > 0.05:   self._press(pos);  self._release(neg)
            elif axis < -0.05: self._press(neg); self._release(pos)
            else:              self._release(pos); self._release(neg)

    def stop(self):
        for name in list(self._held): self._release(name)

class GamepadOutput:
    def __init__(self):
        import vgamepad as _vg
        self.pad = _vg.VX360Gamepad()
    def update(self, roll, pitch, yaw, speed, dt):
        self.pad.left_joystick_float(x_value_float=roll, y_value_float=-pitch)
        self.pad.right_joystick_float(x_value_float=yaw, y_value_float=0)
        self.pad.update()
    def stop(self):
        self.pad.left_joystick_float(x_value_float=0, y_value_float=0)
        self.pad.right_joystick_float(x_value_float=0, y_value_float=0)
        self.pad.update()


# ── Bridge ────────────────────────────────────────────────────────────────────
class Bridge(threading.Thread):
    def __init__(self, joy, get_params, get_output):
        super().__init__(daemon=True)
        self.joy        = joy
        self.get_params = get_params
        self.get_output = get_output
        self.running    = False
        self._stop_evt  = threading.Event()
        self.axes_live  = [0.0, 0.0, 0.0]
        self.foot_on    = False
        self._offsets   = [0.0, 0.0, 0.0]  # calibration

    def calibrate(self):
        if self.joy is None: return
        try:
            self._offsets = [
                self.joy.get_axis(AXIS_ROLL),
                self.joy.get_axis(AXIS_PITCH),
                self.joy.get_axis(AXIS_YAW),
            ]
        except Exception:
            pass

    def apply_curve(self, v, deadzone, exp):
        if abs(v) < deadzone: return 0.0
        sign = 1 if v > 0 else -1
        norm = (abs(v) - deadzone) / (1.0 - deadzone)
        return sign * (norm ** exp)

    def run(self):
        dt = 1.0 / LOOP_HZ
        while not self._stop_evt.is_set():
            t0 = time.perf_counter()
            pygame.event.pump()
            if self.joy is not None:
                try:
                    speed, deadzone, exp = self.get_params()
                    raw_r = self.joy.get_axis(AXIS_ROLL)  - self._offsets[0]
                    raw_p = self.joy.get_axis(AXIS_PITCH) - self._offsets[1]
                    raw_y = self.joy.get_axis(AXIS_YAW)   - self._offsets[2]

                    # Pied absent seulement si tous les axes sont exactement à 0
                    self.foot_on = not (raw_r == 0.0 and raw_p == 0.0 and raw_y == 0.0)

                    roll  = self.apply_curve(raw_r, deadzone, exp)
                    pitch = self.apply_curve(raw_p, deadzone, exp)
                    yaw   = self.apply_curve(raw_y, deadzone, exp)
                    self.axes_live = [roll, pitch, yaw]

                    if self.running:
                        out = self.get_output()
                        if out:
                            try: out.update(roll, pitch, yaw, speed, dt)
                            except Exception: pass
                except Exception:
                    pass
            wait = dt - (time.perf_counter() - t0)
            if wait > 0: time.sleep(wait)


# ── App ───────────────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self, joy):
        super().__init__()
        self.joy       = joy
        self._active   = False
        self._connected = joy is not None
        self._mode     = "mouse"
        self._output   = None

        s = load_settings()
        self._lang     = s.get("lang", "FR")
        self._speed    = ctk.DoubleVar(value=s.get("speed",    3000))
        self._deadzone = ctk.DoubleVar(value=s.get("deadzone", 0.08))
        self._exp      = ctk.DoubleVar(value=s.get("exp",      1.8))
        self._key_map  = {**KEY_MAP_DEFAULT, **s.get("key_map", {})}

        # Sauvegarde automatique à chaque changement de slider
        for var in (self._speed, self._deadzone, self._exp):
            var.trace_add("write", lambda *_: self._save())

        self.bridge = Bridge(joy, self._get_params, lambda: self._output)
        self.bridge.start()

        self.title("3dRudder Reborn")
        self.geometry("500x780")
        self.resizable(False, True)

        # Icône barre des tâches
        if LOGO_PATH.exists():
            ico_path = LOGO_PATH.with_suffix(".ico")
            if not ico_path.exists():
                img = Image.open(LOGO_PATH)
                img.save(ico_path, format="ICO", sizes=[(256,256),(64,64),(32,32),(16,16)])
            try:
                self.iconbitmap(str(ico_path))
            except Exception:
                pass

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._poll()

    def _on_close(self):
        self._save()
        self.destroy()

    def t(self, key):
        return STRINGS[self._lang][key]

    def _get_params(self):
        return self._speed.get(), self._deadzone.get(), self._exp.get()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._widgets = {}

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 0))

        # Titre (gauche)
        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.pack(side="left")
        self._widgets["title_lbl"] = ctk.CTkLabel(
            title_block, text=self.t("title"),
            font=ctk.CTkFont(size=22, weight="bold"))
        self._widgets["title_lbl"].pack(anchor="w")
        self._widgets["subtitle_lbl"] = ctk.CTkLabel(
            title_block, text=self.t("subtitle"),
            font=ctk.CTkFont(size=10), text_color="#555")
        self._widgets["subtitle_lbl"].pack(anchor="w")

        # Logo + statut + langue (droite)
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        if LOGO_PATH.exists():
            img = ctk.CTkImage(Image.open(LOGO_PATH), size=(52, 52))
            ctk.CTkLabel(right, image=img, text="").pack(side="right", padx=(8, 0))

        status_block = ctk.CTkFrame(right, fg_color="transparent")
        status_block.pack(side="right", padx=(0, 6))
        self._widgets["status_dot"] = ctk.CTkLabel(
            status_block, text="●",
            text_color="#2ecc71" if self._connected else "#e74c3c",
            font=ctk.CTkFont(size=18))
        self._widgets["status_dot"].pack(side="right", padx=(4, 0))
        self._widgets["status_lbl"] = ctk.CTkLabel(
            status_block,
            text=self.t("connected") if self._connected else self.t("disconnected"),
            text_color="#aaaaaa", font=ctk.CTkFont(size=12))
        self._widgets["status_lbl"].pack(side="right")

        # Toggle langue
        self._lang_btn = ctk.CTkButton(
            right, text="EN", width=38, height=24,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2a2a2a", hover_color="#3a3a3a",
            command=self._toggle_lang)
        self._lang_btn.pack(side="right", padx=(0, 8))

        # ── Mode ──────────────────────────────────────────────────────────────
        self._widgets["mode_lbl"] = ctk.CTkLabel(
            self, text=self.t("mode"),
            font=ctk.CTkFont(size=11), text_color="#555")
        self._widgets["mode_lbl"].pack(anchor="w", padx=20, pady=(14, 4))

        self._widgets["mode_seg"] = ctk.CTkSegmentedButton(
            self,
            values=[self.t("mouse"), self.t("keyboard"), self.t("gamepad")],
            command=self._on_mode, height=36,
            font=ctk.CTkFont(size=13, weight="bold"))
        self._widgets["mode_seg"].set(self.t("mouse"))
        self._widgets["mode_seg"].pack(fill="x", padx=20)

        # ── Pied + étalonnage ─────────────────────────────────────────────────
        foot_row = ctk.CTkFrame(self, fg_color="transparent")
        foot_row.pack(fill="x", padx=20, pady=(10, 0))

        self._widgets["foot_lbl"] = ctk.CTkLabel(
            foot_row, text=f"⬤  {self.t('foot_off')}",
            font=ctk.CTkFont(size=13), text_color="#555", anchor="w")
        self._widgets["foot_lbl"].pack(side="left")

        self._widgets["calib_btn"] = ctk.CTkButton(
            foot_row, text=self.t("calibrate"), width=100, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#2a2a2a", hover_color="#3a3a3a",
            command=self._calibrate)
        self._widgets["calib_btn"].pack(side="right")

        # ── Bouton principal ──────────────────────────────────────────────────
        self._widgets["toggle_btn"] = ctk.CTkButton(
            self, text=self.t("activate"), height=52,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#1f6aa5", hover_color="#1a578a",
            corner_radius=10, command=self._toggle,
            state="normal" if self._connected else "disabled")
        self._widgets["toggle_btn"].pack(fill="x", padx=20, pady=(14, 0))

        ctk.CTkFrame(self, height=1, fg_color="#2a2a2a").pack(
            fill="x", padx=20, pady=(16, 0))

        # ── Réglages ──────────────────────────────────────────────────────────
        self._widgets["settings_lbl"] = ctk.CTkLabel(
            self, text=self.t("settings"),
            font=ctk.CTkFont(size=11), text_color="#555")
        self._widgets["settings_lbl"].pack(anchor="w", padx=20, pady=(12, 4))

        settings = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=12)
        settings.pack(fill="x", padx=20)
        self._slider_frames = {}
        self._add_slider(settings, "speed",    self._speed,    500, 6000, "{:.0f} px/s")
        self._add_slider(settings, "deadzone", self._deadzone, 0.0, 0.30, "{:.0f}%", scale=100)
        self._add_slider(settings, "precision",self._exp,      1.0, 3.0,  "{:.1f}")

        # ── Panel clavier ─────────────────────────────────────────────────────
        self._kb_panel = self._build_kb_panel()

        # ── Axes live ─────────────────────────────────────────────────────────
        self._widgets["axes_lbl"] = ctk.CTkLabel(
            self, text=self.t("axes"),
            font=ctk.CTkFont(size=11), text_color="#555")
        self._widgets["axes_lbl"].pack(anchor="w", padx=20, pady=(12, 4))

        viz = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=12)
        viz.pack(fill="x", padx=20)
        self.axis_bars = {}
        for key in ("roll", "pitch", "yaw"):
            row = ctk.CTkFrame(viz, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=7)
            lbl = ctk.CTkLabel(row, text=self.t(key), width=100,
                               font=ctk.CTkFont(size=12), anchor="w")
            lbl.pack(side="left")
            bar = ctk.CTkProgressBar(row, height=14, corner_radius=6,
                                     progress_color="#1f6aa5")
            bar.set(0.5)
            bar.pack(side="left", fill="x", expand=True)
            self.axis_bars[key] = (lbl, bar)

        # ── Footer : firmware (gauche) | feedback + don (droite) ─────────────
        ctk.CTkFrame(self, height=1, fg_color="#2a2a2a").pack(
            fill="x", padx=20, pady=(16, 0))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(10, 16))

        self._widgets["fw_btn"] = ctk.CTkButton(
            footer, text=self.t("firmware"), width=100, height=30,
            font=ctk.CTkFont(size=11),
            fg_color="#2a2a2a", hover_color="#3a3a3a",
            command=self._open_firmware_window)
        self._widgets["fw_btn"].pack(side="left")

        self._widgets["donate_btn"] = ctk.CTkButton(
            footer, text=self.t("donate"), width=110, height=30,
            font=ctk.CTkFont(size=11),
            fg_color="#003087", hover_color="#001f5c",
            command=lambda: webbrowser.open(PAYPAL_URL))
        self._widgets["donate_btn"].pack(side="right", padx=(6, 0))

        self._widgets["feedback_btn"] = ctk.CTkButton(
            footer, text=self.t("feedback"), width=100, height=30,
            font=ctk.CTkFont(size=11),
            fg_color="#2a2a2a", hover_color="#3a3a3a",
            command=self._open_feedback_window)
        self._widgets["feedback_btn"].pack(side="right")

    def _build_kb_panel(self):
        panel = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=12)
        self._widgets["kb_map_lbl"] = ctk.CTkLabel(
            panel, text=self.t("kb_map"),
            font=ctk.CTkFont(size=11), text_color="#555")
        self._widgets["kb_map_lbl"].pack(anchor="w", padx=16, pady=(12, 4))

        self._kb_vars = {}
        kb_keys = ["forward","backward","right","left","rot_r","rot_l"]
        map_keys = ["pitch+","pitch-","roll+","roll-","yaw+","yaw-"]
        self._kb_label_widgets = {}
        for tkey, mkey in zip(kb_keys, map_keys):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            lbl = ctk.CTkLabel(row, text=self.t(tkey), width=160,
                               font=ctk.CTkFont(size=12), anchor="w")
            lbl.pack(side="left")
            self._kb_label_widgets[tkey] = lbl
            var = ctk.StringVar(value=self._key_map[mkey])
            entry = ctk.CTkEntry(row, textvariable=var, width=60,
                                 font=ctk.CTkFont(size=12), justify="center")
            entry.pack(side="right")
            self._kb_vars[mkey] = var

        self._widgets["apply_btn"] = ctk.CTkButton(
            panel, text=self.t("apply"), height=30,
            command=self._save_kb_mapping,
            font=ctk.CTkFont(size=12))
        self._widgets["apply_btn"].pack(padx=16, pady=(8, 14))
        return panel

    def _add_slider(self, parent, key, var, lo, hi, fmt, scale=1):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=10)
        lbl = ctk.CTkLabel(row, text=self.t(key), width=90,
                            font=ctk.CTkFont(size=12), anchor="w")
        lbl.pack(side="left")
        val_lbl = ctk.CTkLabel(row, text="", width=80,
                               font=ctk.CTkFont(size=12), anchor="e")
        val_lbl.pack(side="right")

        def update(v):
            val_lbl.configure(text=fmt.format(float(v) * scale))

        ctk.CTkSlider(row, from_=lo, to=hi, variable=var,
                      command=update).pack(side="left", fill="x",
                                          expand=True, padx=(8, 8))
        update(var.get())
        self._slider_frames[key] = (lbl, val_lbl)

    # ── Langue ────────────────────────────────────────────────────────────────
    def _toggle_lang(self):
        self._lang = "EN" if self._lang == "FR" else "FR"
        self._lang_btn.configure(text="FR" if self._lang == "EN" else "EN")
        self._refresh_lang()
        self._save()

    def _refresh_lang(self):
        was_active = self._active
        was_mode   = self._mode
        if was_active: self._deactivate()

        self._widgets["subtitle_lbl"].configure(text=self.t("subtitle"))
        self._widgets["status_lbl"].configure(
            text=self.t("connected") if self.joy.get_init() else self.t("disconnected"))
        self._widgets["mode_lbl"].configure(text=self.t("mode"))
        self._widgets["mode_seg"].configure(
            values=[self.t("mouse"), self.t("keyboard"), self.t("gamepad")])
        self._widgets["mode_seg"].set(self.t(was_mode))
        self._widgets["toggle_btn"].configure(text=self.t("activate"))
        self._widgets["settings_lbl"].configure(text=self.t("settings"))
        self._widgets["axes_lbl"].configure(text=self.t("axes"))
        self._widgets["fw_btn"].configure(text=self.t("firmware"))
        self._widgets["feedback_btn"].configure(text=self.t("feedback"))
        self._widgets["donate_btn"].configure(text=self.t("donate"))
        self._widgets["calib_btn"].configure(text=self.t("calibrate"))
        self._widgets["kb_map_lbl"].configure(text=self.t("kb_map"))
        self._widgets["apply_btn"].configure(text=self.t("apply"))

        for key in ("roll", "pitch", "yaw"):
            self.axis_bars[key][0].configure(text=self.t(key))

        for tkey in ["forward","backward","right","left","rot_r","rot_l"]:
            self._kb_label_widgets[tkey].configure(text=self.t(tkey))

        for key in ("speed","deadzone","precision"):
            if key in self._slider_frames:
                self._slider_frames[key][0].configure(text=self.t(key))

    # ── Logique ───────────────────────────────────────────────────────────────
    def _on_mode(self, val):
        if self._active: self._deactivate()
        modes = {self.t("mouse"): "mouse",
                 self.t("keyboard"): "keyboard",
                 self.t("gamepad"): "gamepad"}
        self._mode = modes.get(val, "mouse")

        if self._mode == "keyboard":
            self._kb_panel.pack(fill="x", padx=20, pady=(0, 0),
                                before=self._widgets["axes_lbl"])
            self.geometry("500x1000")
        else:
            self._kb_panel.pack_forget()
            self.geometry("500x780")

        if self._mode == "gamepad" and not _check_vigem():
            self._widgets["toggle_btn"].configure(state="disabled")
            self.after(100, self._open_vigem_window)

    def _calibrate(self):
        self.bridge.calibrate()
        self._widgets["calib_btn"].configure(text=self.t("calibrated"),
                                              fg_color="#1a5c1a")
        self.after(2000, lambda: self._widgets["calib_btn"].configure(
            text=self.t("calibrate"), fg_color="#2a2a2a"))

    def _save(self):
        save_settings({
            "lang":     self._lang,
            "speed":    self._speed.get(),
            "deadzone": self._deadzone.get(),
            "exp":      self._exp.get(),
            "key_map":  dict(self._key_map),
        })

    def _save_kb_mapping(self):
        for k, v in self._kb_vars.items():
            self._key_map[k] = v.get().strip() or self._key_map[k]
        if isinstance(self._output, KeyboardOutput):
            self._output.key_map = dict(self._key_map)
        self._save()

    def _toggle(self):
        if self._active: self._deactivate()
        else: self._activate()

    def _activate(self):
        try:
            if self._mode == "mouse":      self._output = MouseOutput()
            elif self._mode == "keyboard": self._output = KeyboardOutput(dict(self._key_map))
            elif self._mode == "gamepad":  self._output = GamepadOutput()
        except Exception as e:
            self._show_error(str(e))
            return
        self._active = True
        self.bridge.running = True
        self._widgets["toggle_btn"].configure(
            text=self.t("deactivate"), fg_color="#8b0000", hover_color="#6b0000")
        for _, bar in self.axis_bars.values():
            bar.configure(progress_color="#2ecc71")

    def _show_error(self, msg):
        win = ctk.CTkToplevel(self)
        win.title("Erreur")
        win.geometry("420x160")
        win.resizable(False, False)
        win.grab_set()
        ctk.CTkLabel(win, text="Erreur d'activation",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(20, 6))
        ctk.CTkLabel(win, text=msg, font=ctk.CTkFont(size=11),
                     text_color="#e74c3c", wraplength=380).pack(padx=20)
        ctk.CTkButton(win, text="OK", width=80, command=win.destroy).pack(pady=16)

    def _deactivate(self):
        self.bridge.running = False
        if self._output: self._output.stop(); self._output = None
        self._active = False
        self._widgets["toggle_btn"].configure(
            text=self.t("activate"), fg_color="#1f6aa5", hover_color="#1a578a")
        for _, bar in self.axis_bars.values():
            bar.configure(progress_color="#1f6aa5")

    # ── ViGEmBus install window ───────────────────────────────────────────────
    def _open_vigem_window(self):
        win = ctk.CTkToplevel(self)
        win.title(self.t("vigem_title"))
        win.geometry("400x320")
        win.resizable(False, False)
        win.grab_set()

        def on_close():
            self._widgets["toggle_btn"].configure(state="normal")
            self._widgets["mode_seg"].set(self.t("mouse"))
            self._mode = "mouse"
            self._kb_panel.pack_forget()
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_close)

        ctk.CTkLabel(win, text=self.t("vigem_title"),
                     font=ctk.CTkFont(size=18, weight="bold")
                     ).pack(anchor="w", padx=24, pady=(20, 0))

        ctk.CTkLabel(win, text=self.t("vigem_explain"),
                     font=ctk.CTkFont(size=12), text_color="#cccccc",
                     justify="left").pack(anchor="w", padx=24, pady=(12, 0))

        status_lbl = ctk.CTkLabel(win, text="", font=ctk.CTkFont(size=11))
        status_lbl.pack(pady=(10, 0))

        def do_install():
            install_btn.configure(state="disabled", text=self.t("vigem_installing"))

            def run():
                try:
                    import platform as _plat
                    _arch = "x64" if _plat.architecture()[0] == "64bit" else "x86"
                    if getattr(sys, "frozen", False):
                        _msi = (Path(sys._MEIPASS) / "vgamepad" / "win" / "vigem"
                                / "install" / _arch / f"ViGEmBusSetup_{_arch}.msi")
                    else:
                        import vgamepad as _vg
                        _msi = (Path(_vg.__file__).parent / "win" / "vigem"
                                / "install" / _arch / f"ViGEmBusSetup_{_arch}.msi")
                    subprocess.run(["msiexec", "/i", str(_msi)], check=True)
                    win.after(0, lambda: status_lbl.configure(
                        text=self.t("vigem_done"), text_color="#2ecc71"))
                    win.after(0, lambda: install_btn.configure(
                        text=self.t("vigem_restart"),
                        state="normal",
                        command=lambda: os.execv(__file__, ["python", __file__])))
                except Exception as e:
                    win.after(0, lambda: status_lbl.configure(
                        text=f"{self.t('vigem_error')}: {e}", text_color="#e74c3c"))
                    win.after(0, lambda: install_btn.configure(
                        state="normal", text=self.t("vigem_install")))

            threading.Thread(target=run, daemon=True).start()

        install_btn = ctk.CTkButton(
            win, text=self.t("vigem_install"), height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=do_install)
        install_btn.pack(fill="x", padx=24, pady=(12, 20))

    # ── Firmware window ───────────────────────────────────────────────────────
    def _open_firmware_window(self):
        win = ctk.CTkToplevel(self)
        win.title(self.t("fw_title"))
        win.geometry("460x380")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text=self.t("fw_title"),
                     font=ctk.CTkFont(size=20, weight="bold")
                     ).pack(anchor="w", padx=24, pady=(24, 0))

        fw = get_firmware_version()
        info = ctk.CTkFrame(win, fg_color="#1a1a1a", corner_radius=10)
        info.pack(fill="x", padx=24, pady=(12, 0))
        for label_key, value, color in [
            ("fw_current", fw, "#2ecc71" if fw != "Unknown" else "#e74c3c"),
            ("fw_file", FW_INSTALLER.name if FW_INSTALLER.exists()
             else self.t("fw_not_found"), "#aaaaaa"),
        ]:
            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=8)
            ctk.CTkLabel(row, text=self.t(label_key),
                         font=ctk.CTkFont(size=12), text_color="#888").pack(side="left")
            ctk.CTkLabel(row, text=value,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=color).pack(side="right")

        warn = ctk.CTkFrame(win, fg_color="#3a1a00", corner_radius=10)
        warn.pack(fill="x", padx=24, pady=(14, 0))
        ctk.CTkLabel(warn, text=self.t("fw_warn"),
                     font=ctk.CTkFont(size=12), text_color="#ff9944",
                     justify="center").pack(padx=16, pady=14)

        def do_flash():
            if not FW_INSTALLER.exists(): return
            win.destroy()
            os.startfile(str(FW_INSTALLER))

        ctk.CTkButton(win, text=self.t("fw_flash"), height=40,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color="#8b0000", hover_color="#6b0000",
                      command=do_flash).pack(fill="x", padx=24, pady=(14, 20))

    # ── Feedback window ───────────────────────────────────────────────────────
    def _open_feedback_window(self):
        win = ctk.CTkToplevel(self)
        win.title(self.t("fb_title"))
        win.geometry("460x480")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text=self.t("fb_title"),
                     font=ctk.CTkFont(size=20, weight="bold")
                     ).pack(anchor="w", padx=24, pady=(20, 0))
        ctk.CTkLabel(win, text=self.t("fb_subtitle"),
                     font=ctk.CTkFont(size=11), text_color="#666"
                     ).pack(anchor="w", padx=24, pady=(2, 12))

        ctk.CTkLabel(win, text=self.t("fb_name"),
                     font=ctk.CTkFont(size=12), anchor="w").pack(fill="x", padx=24)
        name_entry = ctk.CTkEntry(win, height=34, font=ctk.CTkFont(size=12))
        name_entry.pack(fill="x", padx=24, pady=(4, 10))

        ctk.CTkLabel(win, text=self.t("fb_message"),
                     font=ctk.CTkFont(size=12), anchor="w").pack(fill="x", padx=24)
        msg_box = ctk.CTkTextbox(win, height=140, font=ctk.CTkFont(size=12))
        msg_box.pack(fill="x", padx=24, pady=(4, 10))

        a, b = random.randint(2, 9), random.randint(2, 9)
        captcha_frame = ctk.CTkFrame(win, fg_color="#1a1a1a", corner_radius=8)
        captcha_frame.pack(fill="x", padx=24, pady=(0, 10))
        ctk.CTkLabel(captcha_frame,
                     text=f"{self.t('fb_captcha')}  {a} + {b} ?",
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=12, pady=8)
        captcha_var = ctk.StringVar()
        ctk.CTkEntry(captcha_frame, textvariable=captcha_var,
                     width=60, font=ctk.CTkFont(size=12), justify="center"
                     ).pack(side="right", padx=12, pady=8)

        status_lbl = ctk.CTkLabel(win, text="", font=ctk.CTkFont(size=11))
        status_lbl.pack(pady=(0, 4))

        def send():
            try:
                if int(captcha_var.get().strip()) != a + b:
                    status_lbl.configure(text=self.t("fb_captcha_err"),
                                         text_color="#e74c3c"); return
            except ValueError:
                status_lbl.configure(text=self.t("fb_captcha_err"),
                                     text_color="#e74c3c"); return

            message = msg_box.get("1.0", "end").strip()
            if not message:
                status_lbl.configure(text=self.t("fb_empty"),
                                     text_color="#e74c3c"); return

            cfg = load_email_config()
            if cfg is None:
                status_lbl.configure(text=self.t("fb_no_config"),
                                     text_color="#e74c3c"); return

            name = name_entry.get().strip() or "Anonyme"
            send_btn.configure(state="disabled", text="...")
            status_lbl.configure(text="", text_color="white")

            def do_send():
                try:
                    body = (
                        f"{self.t('fb_header')}\n\n"
                        f"{self.t('fb_from')}     : {name}\n"
                        f"{self.t('fb_fw')} : {get_firmware_version()}\n\n"
                        f"---\n{message}\n"
                    )
                    msg = MIMEMultipart()
                    msg["From"]    = cfg["sender"]
                    msg["To"]      = cfg["recipient"]
                    msg["Subject"] = f"{self.t('fb_subject')} {name}"
                    msg.attach(MIMEText(body, "plain", "utf-8"))
                    with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"])) as srv:
                        srv.starttls()
                        srv.login(cfg["sender"], cfg["password"])
                        srv.sendmail(cfg["sender"], cfg["recipient"], msg.as_string())
                    win.after(0, lambda: status_lbl.configure(
                        text=self.t("fb_sent"), text_color="#2ecc71"))
                    win.after(0, lambda: send_btn.configure(
                        state="disabled", text="✓"))
                except Exception as e:
                    win.after(0, lambda: status_lbl.configure(
                        text=f"{self.t('fb_error')}: {e}", text_color="#e74c3c"))
                    win.after(0, lambda: send_btn.configure(
                        state="normal", text=self.t("fb_send")))

            threading.Thread(target=do_send, daemon=True).start()

        send_btn = ctk.CTkButton(win, text=self.t("fb_send"), height=38,
                                 font=ctk.CTkFont(size=13, weight="bold"),
                                 command=send)
        send_btn.pack(fill="x", padx=24, pady=(0, 20))

    # ── Poll ──────────────────────────────────────────────────────────────────
    def _poll(self):
        joy = find_3drudder()
        now_connected = joy is not None

        if now_connected and not self._connected:
            self._connected = True
            self.joy = joy
            self.bridge.joy = joy
            self._widgets["status_dot"].configure(text_color="#2ecc71")
            self._widgets["status_lbl"].configure(text=self.t("connected"))
            self._widgets["toggle_btn"].configure(state="normal")

        elif not now_connected and self._connected:
            self._connected = False
            if self._active:
                self._deactivate()
            self._widgets["status_dot"].configure(text_color="#e74c3c")
            self._widgets["status_lbl"].configure(text=self.t("disconnected"))
            self._widgets["toggle_btn"].configure(
                state="disabled", text=self.t("activate"))
            for _, bar in self.axis_bars.values():
                bar.set(0.5)

        if self._connected:
            vals = self.bridge.axes_live
            for i, key in enumerate(("roll", "pitch", "yaw")):
                v = vals[i] if i < len(vals) else 0.0
                self.axis_bars[key][1].set((v + 1) / 2)

            foot = self.bridge.foot_on
            self._widgets["foot_lbl"].configure(
                text=f"⬤  {self.t('foot_on')}" if foot else f"⬤  {self.t('foot_off')}",
                text_color="#2ecc71" if foot else "#e74c3c")
        else:
            self._widgets["foot_lbl"].configure(
                text=f"⬤  {self.t('foot_off')}", text_color="#555")

        self.after(100, self._poll)


# ── Main ──────────────────────────────────────────────────────────────────────
def find_3drudder():
    for i in range(pygame.joystick.get_count()):
        j = pygame.joystick.Joystick(i)
        if not j.get_init():
            j.init()
        if "3drudder" in j.get_name().lower() or "3DRUDDER" in j.get_name():
            return j
    return None

if __name__ == "__main__":
    pygame.init()
    pygame.joystick.init()

    joy = find_3drudder()
    app = App(joy)   # joy peut être None, l'app attend le branchement
    app.mainloop()
    pygame.quit()
