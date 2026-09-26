"""
====================================================================
ملف الإعدادات الأصلي (Single-Hand Soundboard Configuration)
====================================================================
هذا الملف مضبوط للعمل بيد واحدة (One Hand) بدقة وسلاسة،
مع ربط إيماءات اليد الأساسية الـ 7 بالملفات الصوتية المخصصة.
====================================================================
"""

import os
import sounddevice as sd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

# ====================================================================
# 1. إعدادات أجهزة الصوت (Audio Devices Configuration)
# ====================================================================

def find_device_id_by_keyword(keyword, is_output=True):
    try:
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            name = dev['name'].lower()
            if keyword.lower() in name:
                if is_output and dev['max_output_channels'] > 0:
                    return i
                elif not is_output and dev['max_input_channels'] > 0:
                    return i
    except Exception:
        pass
    return None

# مخرج Virtual Cable (الذي يرسل الصوت لديسكورد)
AUTO_CABLE_ID = find_device_id_by_keyword("cable input", is_output=True)
CABLE_INPUT_ID = AUTO_CABLE_ID if AUTO_CABLE_ID is not None else 6

# سماع المؤثرات في سماعتك الشخصية أيضاً (Dual Audio Monitor)
ENABLE_MONITOR = True
MONITOR_OUTPUT_ID = None

# مستويات الصوت (0.0 إلى 1.0)
VOLUME_CABLE = 1.0
VOLUME_MONITOR = 0.75

# ====================================================================
# 2. إعدادات الكاميرا واليد الواحدة (Camera & Single Hand Tracking)
# ====================================================================

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FLIP_HORIZONTAL = True

# تتبع يد واحدة فقط لتفادي أي تشتت أو بطء
NUM_HANDS = 1

# حساسية نموذج الذكاء الاصطناعي
MIN_DETECTION_CONFIDENCE = 0.65
MIN_TRACKING_CONFIDENCE = 0.65

# مسار نموذج MediaPipe Gesture Recognizer
MODEL_PATH = os.path.join(BASE_DIR, "gesture_recognizer.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"

# ====================================================================
# 3. إعدادات الـ Cooldown وتفادي التكرار (Debounce & Cooldown)
# ====================================================================

COOLDOWN_SECONDS = 2.0
GLOBAL_COOLDOWN_SECONDS = 0.6
REQUIRE_GESTURE_RELEASE = True
MIN_GESTURE_SCORE = 0.60

# ====================================================================
# 4. جدول ربط الإيماءات الـ 7 بالملفات الصوتية (Gesture-to-Sound Mapping)
# ====================================================================

GESTURE_SOUND_MAP = {
    # 🖐️ كف اليد مفتوح
    "Open_Palm": {
        "sound": os.path.join(SOUNDS_DIR, "open_palm.wav"),
        "label": "Open Palm",
        "label_ar": "كف مفتوح (ترحيب)",
        "emoji": "🖐️",
        "color": (0, 255, 128)  # أخضر زمردي
    },
    # ✌️ علامة النصر
    "Victory": {
        "sound": os.path.join(SOUNDS_DIR, "victory.wav"),
        "label": "Victory",
        "label_ar": "علامة النصر (فوز)",
        "emoji": "✌️",
        "color": (255, 200, 0)  # أزرق سماوي
    },
    # ✊ قبضة اليد
    "Closed_Fist": {
        "sound": os.path.join(SOUNDS_DIR, "closed_fist.wav"),
        "label": "Closed Fist",
        "label_ar": "قبضة يد (ضربة/بونك)",
        "emoji": "✊",
        "color": (0, 0, 255)  # أحمر
    },
    # 👍 إبهام لأعلى
    "Thumb_Up": {
        "sound": os.path.join(SOUNDS_DIR, "thumb_up.wav"),
        "label": "Thumb Up",
        "label_ar": "إبهام لأعلى (إعجاب)",
        "emoji": "👍",
        "color": (0, 255, 255)  # أصفر
    },
    # 👎 إبهام لأسفل
    "Thumb_Down": {
        "sound": os.path.join(SOUNDS_DIR, "thumb_down.wav"),
        "label": "Thumb Down",
        "label_ar": "إبهام لأسفل (إخفاق)",
        "emoji": "👎",
        "color": (128, 0, 255)  # أرجواني
    },
    # ☝️ سبابة لأعلى
    "Pointing_Up": {
        "sound": os.path.join(SOUNDS_DIR, "pointing_up.wav"),
        "label": "Pointing Up",
        "label_ar": "سبابة لأعلى (تنبيه/ليزر)",
        "emoji": "☝️",
        "color": (255, 100, 255)  # وردي
    },
    # 🤟 علامة الروك / الحب
    "ILoveYou": {
        "sound": os.path.join(SOUNDS_DIR, "iloveyou.wav"),
        "label": "Rock / Love",
        "label_ar": "روك / هورن حماسي",
        "emoji": "🤟",
        "color": (255, 128, 0)  # أزرق فاقع
    }
}
