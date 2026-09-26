"""
================================================================================
 تطبيق Soundboard يتم تفعيله بحركات اليد الواحدة (Single-Hand Soundboard)
================================================================================
الخصائص:
- تتبع يد واحدة فقط (One Hand) لضمان أعلى سرعة واستجابة وأقل استهلاك معالج.
- 7 إيماءات واضحة وسريعة:
  🖐️ كف مفتوح | ✌️ علامة النصر | ✊ قبضة اليد | 👍 إبهام لأعلى
  👎 إبهام لأسفل | ☝️ سبابة لأعلى | 🤟 علامة الروك
- نظام Cooldown & Debounce لمنع التكرار العشوائي.
- بث الصوت المباشر إلى CABLE Input (ديسكورد والألعاب) وسماعتك الشخصية معاً.
================================================================================
"""

import os
import sys
import time
import threading
import urllib.request
import numpy as np
import cv2
import sounddevice as sd
import soundfile as sf

import config

# ضمان دعم الترميز UTF-8 في ويندوز
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# روابط مفاصل اليد (21 Landmark Hand Topology)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # الإبهام (Thumb)
    (0, 5), (5, 6), (6, 7), (7, 8),        # السبابة (Index)
    (5, 9), (9, 10), (10, 11), (11, 12),   # الوسطى (Middle)
    (9, 13), (13, 14), (14, 15), (15, 16), # البنصر (Ring)
    (13, 17), (17, 18), (18, 19), (19, 20),# الخنصر (Pinky)
    (0, 17)                                # قاعدة الكف (Palm Base)
]


class SoundEngine:
    """محرك إدارة وتحميل وتشغيل المؤثرات الصوتية بكفاءة عالية وبدون تأخير (Zero Latency)"""

    def __init__(self):
        self.sound_cache = {}
        self.cable_device_id = config.CABLE_INPUT_ID
        self.monitor_device_id = config.MONITOR_OUTPUT_ID
        self.enable_monitor = config.ENABLE_MONITOR
        self.last_played_name = "None"
        self.last_played_time = 0.0

        self.preload_sounds()

    def preload_sounds(self):
        """تحميل جميع ملفات الصوت مسبقاً في الذاكرة RAM لتفادي أي بطء في القراءة من القرص"""
        print("\n[*] جاري تحميل المؤثرات الصوتية الـ 7 إلى الذاكرة RAM...")
        for gesture_name, info in config.GESTURE_SOUND_MAP.items():
            path = info["sound"]
            if os.path.exists(path):
                try:
                    data, samplerate = sf.read(path, dtype='float32')
                    if len(data.shape) == 1:
                        data = np.column_stack((data, data))

                    cable_data = data * float(config.VOLUME_CABLE)
                    monitor_data = data * float(config.VOLUME_MONITOR)

                    self.sound_cache[gesture_name] = {
                        "cable_data": cable_data,
                        "monitor_data": monitor_data,
                        "samplerate": samplerate,
                        "label": info.get("label", gesture_name),
                        "label_ar": info.get("label_ar", gesture_name),
                        "emoji": info.get("emoji", "🔊")
                    }
                    print(f"  [✓] {info.get('emoji', '')} {info['label']:<16} <- {os.path.basename(path)}")
                except Exception as e:
                    print(f"  [X] خطأ في تحميل الملف {path}: {e}")
            else:
                print(f"  [!] تحذير: الملف الصوتي غير موجود: {path}")

        print("[✓] اكتمل بنك الأصوات بنجاح!\n")

    def play(self, gesture_name):
        """تشغيل الصوت في مسارين متزامنين مستقلين (CABLE Virtual Mic + Monitor Headphones)"""
        if gesture_name not in self.sound_cache:
            return

        sound = self.sound_cache[gesture_name]
        self.last_played_name = f"{sound['emoji']} {sound['label']}"
        self.last_played_time = time.time()

        def _stream_to_device(data, samplerate, dev_id, name="Device"):
            stream = None
            try:
                channels = data.shape[1] if len(data.shape) > 1 else 1
                duration = len(data) / float(samplerate)
                stream = sd.OutputStream(device=dev_id, samplerate=samplerate, channels=channels, dtype='float32')
                stream.start()
                stream.write(data)
                # الانتظار حتى اكتمال خروج الصوت من كرت الصوت قبل إغلاق القناة
                time.sleep(duration + 0.05)
                stream.stop()
            except Exception as e:
                print(f"[!] خطأ أثناء بث الصوت إلى {name} (ID #{dev_id}): {e}")
            finally:
                if stream:
                    try:
                        stream.close()
                    except Exception:
                        pass

        def _play_worker():
            threads = []
            # 1. إرسال الصوت إلى مخرج الكابل الافتراضي (CABLE Input ليسمعه ديسكورد والمايك)
            if self.cable_device_id is not None:
                t_cable = threading.Thread(
                    target=_stream_to_device,
                    args=(sound["cable_data"], sound["samplerate"], self.cable_device_id, "Virtual Cable"),
                    daemon=True
                )
                threads.append(t_cable)
                t_cable.start()

            # 2. إرسال الصوت متزامناً إلى سماعتك الشخصية (إذا تم تفعيل خيار Monitor)
            if self.enable_monitor and self.monitor_device_id is not None:
                t_mon = threading.Thread(
                    target=_stream_to_device,
                    args=(sound["monitor_data"], sound["samplerate"], self.monitor_device_id, "Monitor Speakers"),
                    daemon=True
                )
                threads.append(t_mon)
                t_mon.start()

            for t in threads:
                t.join()

        threading.Thread(target=_play_worker, daemon=True).start()


class GestureCooldownManager:
    """نظام إدارة المؤقتات (Cooldown & Debounce) لمنع تكرار الصوت بالخطأ"""

    def __init__(self):
        self.cooldown_seconds = config.COOLDOWN_SECONDS
        self.global_cooldown = config.GLOBAL_COOLDOWN_SECONDS
        self.require_release = config.REQUIRE_GESTURE_RELEASE

        self.last_trigger_times = {g: 0.0 for g in config.GESTURE_SOUND_MAP}
        self.global_last_trigger = 0.0
        self.last_detected_gesture = "None"
        self.gesture_is_released = True

    def update_state(self, current_gesture):
        """تحديث حالة إفلات اليد وإعادة التأهب (Re-arming)"""
        if current_gesture != self.last_detected_gesture:
            self.gesture_is_released = True
        self.last_detected_gesture = current_gesture

    def can_trigger(self, gesture):
        """التحقق مما إذا كانت الحركة مؤهلة لإطلاق الصوت الآن"""
        now = time.time()

        if (now - self.global_last_trigger) < self.global_cooldown:
            return False, 0.0

        if self.require_release and not self.gesture_is_released:
            return False, 0.0

        last_time = self.last_trigger_times.get(gesture, 0.0)
        time_elapsed = now - last_time
        if time_elapsed < self.cooldown_seconds:
            progress = time_elapsed / self.cooldown_seconds
            return False, progress

        return True, 1.0

    def mark_triggered(self, gesture):
        """تسجيل تفعيل الحركة وحفظ التوقيت"""
        now = time.time()
        self.last_trigger_times[gesture] = now
        self.global_last_trigger = now
        self.gesture_is_released = False

    def get_remaining_cooldown(self, gesture):
        """حساب النسبة المئوية المتبقية للمؤقت (من 0.0 إلى 1.0)"""
        now = time.time()
        time_elapsed = now - self.last_trigger_times.get(gesture, 0.0)
        if time_elapsed >= self.cooldown_seconds:
            return 1.0
        return max(0.0, min(1.0, time_elapsed / self.cooldown_seconds))


class HandSoundboardApp:
    """التطبيق الرئيسي للـ Soundboard التفاعلي باليد الواحدة"""

    def __init__(self):
        self.ensure_model_exists()
        self.sound_engine = SoundEngine()
        self.cooldown_mgr = GestureCooldownManager()

        # تهيئة نموذج MediaPipe Gesture Recognizer ليد واحدة
        base_options = mp_python.BaseOptions(model_asset_path=config.MODEL_PATH)
        options = mp_vision.GestureRecognizerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.IMAGE,
            num_hands=config.NUM_HANDS,
            min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.MIN_TRACKING_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        print("[*] جاري تحميل محرك الذكاء الاصطناعي (MediaPipe Tasks Vision)...")
        self.recognizer = mp_vision.GestureRecognizer.create_from_options(options)
        print("[✓] تم تفعيل محرك الذكاء الاصطناعي لليد الواحدة بنجاح!\n")

        self.fps = 0.0
        self.fps_filter = 0.9
        self.prev_time = time.time()

    def ensure_model_exists(self):
        """التأكد من وجود ملف نموذج MediaPipe وتنزيله تلقائياً إذا كان مفقوداً"""
        if not os.path.exists(config.MODEL_PATH):
            print(f"[!] جاري تنزيل نموذج الذكاء الاصطناعي من Google: {config.MODEL_URL}")
            try:
                urllib.request.urlretrieve(config.MODEL_URL, config.MODEL_PATH)
                print("[✓] اكتمل تنزيل النموذج بنجاح!")
            except Exception as e:
                print(f"[X] فشل تنزيل النموذج: {e}")
                sys.exit(1)

    def draw_hand_skeleton(self, frame, landmarks, color=(0, 255, 128)):
        """رسم هيكل اليد والمفاصل بخطوط متوهجة وتصميم عصري"""
        h, w, _ = frame.shape
        points = []

        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            points.append((cx, cy))

        for p1_idx, p2_idx in HAND_CONNECTIONS:
            pt1 = points[p1_idx]
            pt2 = points[p2_idx]
            cv2.line(frame, pt1, pt2, (35, 35, 40), 4, cv2.LINE_AA)
            cv2.line(frame, pt1, pt2, color, 2, cv2.LINE_AA)

        for i, (cx, cy) in enumerate(points):
            radius = 5 if i in [4, 8, 12, 16, 20] else 3
            cv2.circle(frame, (cx, cy), radius + 2, (0, 0, 0), -1, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), radius, (255, 255, 255), -1, cv2.LINE_AA)

    def draw_hud(self, frame, current_gesture, score, is_triggering):
        """رسم واجهة تفاعلية شاشية مستقبلية (HUD Overlay)"""
        h, w, _ = frame.shape

        # الشريط العلوي والسفلي الشفاف
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 75), (14, 14, 20), -1)
        cv2.rectangle(overlay, (0, h - 45), (w, h), (14, 14, 20), -1)
        cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)

        cv2.line(frame, (0, 75), (w, 75), (55, 55, 75), 1)
        cv2.line(frame, (0, h - 45), (w, h - 45), (55, 55, 75), 1)

        # معلومات الحركة الحالية
        gesture_info = config.GESTURE_SOUND_MAP.get(current_gesture, None)
        if gesture_info and score >= config.MIN_GESTURE_SCORE:
            label = gesture_info["label"]
            emoji = gesture_info.get("emoji", "")
            color = gesture_info.get("color", (0, 255, 128))
            cooldown_ratio = self.cooldown_mgr.get_remaining_cooldown(current_gesture)

            cv2.putText(frame, f"{emoji} {label.upper()}", (20, 32),
                        cv2.FONT_HERSHEY_DUPLEX, 0.75, color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"Conf: {int(score * 100)}% | Single Hand Mode", (20, 58),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (190, 190, 200), 1, cv2.LINE_AA)

            # شريط مؤقت الـ Cooldown
            bar_x, bar_y, bar_w, bar_h = 300, 44, 160, 12
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (40, 40, 50), -1)
            fill_w = int(bar_w * cooldown_ratio)
            bar_color = (0, 255, 128) if cooldown_ratio >= 1.0 else (0, 140, 255)
            if fill_w > 0:
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), bar_color, -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 120), 1)

            status_text = "READY" if cooldown_ratio >= 1.0 else f"WAIT {int((1.0 - cooldown_ratio) * config.COOLDOWN_SECONDS * 10) / 10}s"
            cv2.putText(frame, status_text, (bar_x + bar_w + 8, bar_y + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, bar_color, 1, cv2.LINE_AA)

            if is_triggering:
                cv2.rectangle(frame, (0, 0), (w, h), color, 6)
        else:
            cv2.putText(frame, "READY | Show Hand to Play", (20, 42),
                        cv2.FONT_HERSHEY_DUPLEX, 0.65, (150, 150, 160), 2, cv2.LINE_AA)

        # معدل الإطارات (FPS) ومخرج الصوت
        cv2.putText(frame, f"FPS: {int(self.fps)}", (w - 110, 30),
                    cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"CABLE: #{self.sound_engine.cable_device_id}", (w - 160, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)

        # الشريط السفلي
        last_sfx = f"Last SFX: {self.sound_engine.last_played_name}"
        cv2.putText(frame, last_sfx, (20, h - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 220, 100), 1, cv2.LINE_AA)

        hint_text = "[Q] Exit | Single Hand (7 SFX)"
        cv2.putText(frame, hint_text, (w - 250, h - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (160, 160, 170), 1, cv2.LINE_AA)

    def run(self):
        cap = cv2.VideoCapture(config.CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        if not cap.isOpened():
            print(f"[X] خطأ: تعذر فتح كاميرا الويب برقم الفهرس {config.CAMERA_INDEX}")
            return

        window_name = "AI Hand-Gesture Soundboard (Single Hand - Discord / Mic In)"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        print("=" * 70)
        print("  🚀 نظام الـ Soundboard باليد الواحدة (7 حركات) يعمل الآن بنجاح! 🚀")
        print("  - أظهر يدك أمام الكاميرا ونفذ أي حركة لإطلاق الصوت مباشرة إلى المايك.")
        print("  - اضغط حرف [Q] من لوحة المفاتيح للخروج.")
        print("=" * 70 + "\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.04)
                continue

            curr_time = time.time()
            instant_fps = 1.0 / max(curr_time - self.prev_time, 1e-5)
            self.fps = self.fps_filter * self.fps + (1.0 - self.fps_filter) * instant_fps
            self.prev_time = curr_time

            if config.FLIP_HORIZONTAL:
                frame = cv2.flip(frame, 1)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            recognition_result = self.recognizer.recognize(mp_image)

            current_gesture = "None"
            score = 0.0
            is_triggering = False

            if recognition_result.gestures and len(recognition_result.gestures) > 0:
                top_gesture = recognition_result.gestures[0][0]
                current_gesture = top_gesture.category_name
                score = top_gesture.score

                # رسم هيكل اليد
                if recognition_result.hand_landmarks and len(recognition_result.hand_landmarks) > 0:
                    hand_lms = recognition_result.hand_landmarks[0]
                    g_color = config.GESTURE_SOUND_MAP.get(current_gesture, {}).get("color", (0, 255, 128))
                    self.draw_hand_skeleton(frame, hand_lms, color=g_color)

                self.cooldown_mgr.update_state(current_gesture)

                # التحقق من شروط التفعيل
                if current_gesture in config.GESTURE_SOUND_MAP and score >= config.MIN_GESTURE_SCORE:
                    can_fire, _ = self.cooldown_mgr.can_trigger(current_gesture)
                    if can_fire:
                        self.sound_engine.play(current_gesture)
                        self.cooldown_mgr.mark_triggered(current_gesture)
                        is_triggering = True
                        g_info = config.GESTURE_SOUND_MAP[current_gesture]
                        print(f"  [🔊 تفعيل!] {g_info['emoji']} {g_info['label']:<16} ({int(score * 100)}%) -> تم الإرسال للمايك")
            else:
                self.cooldown_mgr.update_state("None")

            self.draw_hud(frame, current_gesture, score, is_triggering)

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q') or key == 27:
                print("\n[*] إغلاق السكريبت...")
                break

        cap.release()
        cv2.destroyAllWindows()
        sd.stop()
        print("[✓] تم إنهاء جميع العمليات وإغلاق الكاميرا والصوت بأمان.")


if __name__ == "__main__":
    app = HandSoundboardApp()
    app.run()
