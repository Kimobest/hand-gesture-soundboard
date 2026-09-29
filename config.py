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

def find_cable_output_id():
    """البحث الذكي عن مخرج Virtual Cable (سواء سُمي CABLE Input أو VB-Audio Virtual Cable)"""
    try:
        devices = sd.query_devices()
        candidates = []
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:
                name = dev['name'].lower()
                if 'cable input' in name or 'vb-audio virtual' in name or ('vb-audio' in name and 'cable' in name):
                    candidates.append((i, dev))
        if candidates:
            # نفضل MME (hostapi == 0) لتفادي أي تعارض في الترددات بين التطبيقات
            for idx, d in candidates:
                if d['hostapi'] == 0:
                    return idx
            return candidates[0][0]
    except Exception:
        pass
    return 6  # القيمة الافتراضية

def find_monitor_output_id():
    """البحث الذكي عن سماعاتك الشخصية لسماع الصوت في نفس الوقت"""
    try:
        devices = sd.query_devices()
        def_out = sd.default.device[1]
        if def_out is not None and def_out >= 0:
            dev = devices[def_out]
            name = dev['name'].lower()
            if 'vb-audio' not in name and 'cable' not in name:
                return def_out
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0 and dev['hostapi'] == 0:
                name = dev['name'].lower()
                if ('realtek' in name or 'speaker' in name or 'headphone' in name) and 'vb-audio' not in name and 'cable' not in name:
                    return i
    except Exception:
        pass
    return 5

def find_real_mic_id():
    """البحث الذكي عن الميكروفون الحقيقي الخاص بك (Realtek Microphone)"""
    try:
        devices = sd.query_devices()
        # 1. تفضيل مايك Realtek الأصلي للجهاز
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0 and dev['hostapi'] == 0:
                name = dev['name'].lower()
                if 'realtek' in name and 'mic' in name:
                    return i
        # 2. أي مايك حقيقي لا يحتوي على كلمات برامج البث الافتراضية
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0 and dev['hostapi'] == 0:
                name = dev['name'].lower()
                if 'mic' in name and not any(k in name for k in ['steam', 'cable', 'mapper', 'virtual']):
                    return i
    except Exception:
        pass
    return 3

# مخرج Virtual Cable (الذي يرسل الصوت لديسكورد والمايك)
CABLE_INPUT_ID = find_cable_output_id()

# سماع المؤثرات في سماعتك الشخصية أيضاً (Dual Audio Monitor)
ENABLE_MONITOR = True
MONITOR_OUTPUT_ID = find_monitor_output_id()

# الميكروفون الحقيقي الخاص بك (لتمرير صوتك مع الساوند بورد مباشرة)
REAL_MIC_ID = find_real_mic_id()

# دمج وتمرير صوتك الحقيقي مع مؤثرات الساوند بورد تلقائياً بدون أي برامج خارجية
ENABLE_MIC_PASSTHROUGH = True
MIC_VOLUME = 1.0

# مستويات الصوت (0.0 إلى 1.0)
VOLUME_CABLE = 1.0
VOLUME_MONITOR = 0.85

# ====================================================================
# 2. إعدادات الكاميرا واليد الواحدة (Camera & Single Hand Tracking)
# ====================================================================

def detect_available_cameras(max_check=4):
    """فحص واكتشاف أرقام الكاميرات المتاحة في النظام"""
    available = []
    try:
        import cv2
        for i in range(max_check):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append(i)
                cap.release()
    except Exception:
        pass
    return available if available else [0]

# رقم الكاميرا الافتراضية (0 أو 1 أو 2...)
CAMERA_INDEX = 0

# إظهار قائمة اختيار الكاميرا عند بدء التشغيل إذا وُجدت أكثر من كاميرا
PROMPT_CAMERA_ON_START = True

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
