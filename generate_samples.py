"""
====================================================================
مولد العينات والمؤثرات الصوتية الافتراضية (Sample Sounds Generator)
====================================================================
يقوم هذا السكريبت بإنشاء كافة المؤثرات الصوتية الفردية والمزدوجة (الكفين)
تلقائياً وحفظها داخل مجلد sounds/ بصيغة .wav باستخدام خوارزميات التوليد الصوتي (DSP).
====================================================================
"""

import os
import sys
import numpy as np
import soundfile as sf

# ضبط ترميز UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SAMPLE_RATE = 44100
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")


def create_sounds_directory():
    if not os.path.exists(SOUNDS_DIR):
        os.makedirs(SOUNDS_DIR)
        print(f"[+] تم إنشاء مجلد الأصوات: {SOUNDS_DIR}")


# ====================================================================
# 1. مؤثرات اليد الفردية (Single Hand Sounds)
# ====================================================================

def generate_open_palm():
    """كف مفتوح: رنين ترحيبي صاعد ناعم (Sparkle Chime)"""
    duration = 0.8
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freqs = [523.25, 659.25, 783.99, 1046.50]
    audio = np.zeros_like(t)

    for i, f in enumerate(freqs):
        start_idx = int(i * 0.12 * SAMPLE_RATE)
        sub_len = len(t) - start_idx
        if sub_len > 0:
            sub_t = np.linspace(0, sub_len / SAMPLE_RATE, sub_len, False)
            env = np.exp(-4.5 * sub_t)
            tone = (np.sin(2 * np.pi * f * sub_t) + 0.3 * np.sin(2 * np.pi * f * 2 * sub_t)) * env
            audio[start_idx:] += tone

    return audio / np.max(np.abs(audio) + 1e-9) * 0.8


def generate_victory():
    """علامة النصر: نغمة الفوز وLevel Up كلاسيكية مبهجة"""
    duration = 1.0
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    notes = [
        (392.0, 0.0, 0.18),
        (523.25, 0.18, 0.18),
        (659.25, 0.36, 0.18),
        (783.99, 0.54, 0.46),
    ]
    audio = np.zeros_like(t)

    for freq, start_s, note_dur in notes:
        s_idx = int(start_s * SAMPLE_RATE)
        e_idx = s_idx + int(note_dur * SAMPLE_RATE)
        sub_t = np.linspace(0, note_dur, e_idx - s_idx, False)
        attack = int(0.02 * SAMPLE_RATE)
        decay = len(sub_t) - attack
        env = np.concatenate([np.linspace(0, 1, attack), np.exp(-3.0 * np.linspace(0, 1, decay))])
        tone = (
            np.sin(2 * np.pi * freq * sub_t)
            + 0.5 * np.sin(2 * np.pi * freq * 2 * sub_t)
            + 0.25 * np.sin(2 * np.pi * freq * 3 * sub_t)
        ) * env
        audio[s_idx:e_idx] += tone

    return audio / np.max(np.abs(audio) + 1e-9) * 0.85


def generate_closed_fist():
    """قبضة يد: ضربة ارتطام قوية (Heavy Punch / Bonk)"""
    duration = 0.45
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq_sweep = np.linspace(220, 45, len(t))
    phase = 2 * np.pi * np.cumsum(freq_sweep) / SAMPLE_RATE
    env = np.exp(-12.0 * t)
    noise = np.random.uniform(-0.3, 0.3, len(t)) * np.exp(-35.0 * t)
    audio = (np.sin(phase) + noise) * env
    return audio / np.max(np.abs(audio) + 1e-9) * 0.9


def generate_thumb_up():
    """إبهام لأعلى: رنة إنجاز إيجابية ونقية (Bright Success Bell)"""
    duration = 0.7
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    env = np.exp(-4.0 * t)
    bell = (
        np.sin(2 * np.pi * 880 * t)
        + 0.4 * np.sin(2 * np.pi * 1760 * t)
        + 0.15 * np.sin(2 * np.pi * 2640 * t)
    ) * env
    return bell / np.max(np.abs(bell) + 1e-9) * 0.8


def generate_thumb_down():
    """إبهام لأسفل: صوت الخسارة أو الإخفاق (Sad Fail Trombone Slide)"""
    duration = 0.9
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    vibrato = 6.0 * np.sin(2 * np.pi * 5.0 * t)
    freq_slide = np.linspace(310, 110, len(t)) + vibrato
    phase = 2 * np.pi * np.cumsum(freq_slide) / SAMPLE_RATE
    env = np.exp(-2.2 * t)
    audio = (
        np.sin(phase)
        + 0.45 * np.sin(2 * phase)
        + 0.25 * np.sin(3 * phase)
    ) * env
    return audio / np.max(np.abs(audio) + 1e-9) * 0.8


def generate_pointing_up():
    """سبابة لأعلى: ليزر تنبيه وتوجيه مستقبلي (Sci-Fi Laser Zap)"""
    duration = 0.35
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq_sweep = 2200 * np.exp(-10.0 * t) + 200
    phase = 2 * np.pi * np.cumsum(freq_sweep) / SAMPLE_RATE
    env = np.exp(-8.0 * t)
    audio = np.sin(phase) * env
    return audio / np.max(np.abs(audio) + 1e-9) * 0.8


def generate_iloveyou():
    """إيماءة الروك: بوق حماسي ثلاثي النبضات (Meme Airhorn Effect)"""
    duration = 0.7
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    f0 = 370.0
    harmonics = [(1.0, 1.0), (1.5, 0.8), (2.0, 0.7), (3.0, 0.5), (4.0, 0.3)]
    pulses = [(0.0, 0.12), (0.16, 0.12), (0.32, 0.35)]
    pulse_pattern = np.zeros_like(t)

    for start_p, dur_p in pulses:
        p_start = int(start_p * SAMPLE_RATE)
        p_end = min(p_start + int(dur_p * SAMPLE_RATE), len(t))
        sub_len = p_end - p_start
        sub_t = np.linspace(0, dur_p, sub_len, False)
        p_env = np.sin(np.pi * np.clip(sub_t / dur_p, 0, 1)) ** 0.5
        pulse_pattern[p_start:p_end] = p_env

    horn = np.zeros_like(t)
    for mult, amp in harmonics:
        horn += amp * np.sin(2 * np.pi * (f0 * mult) * t)

    audio = horn * pulse_pattern
    return audio / np.max(np.abs(audio) + 1e-9) * 0.85


# ====================================================================
# 2. مؤثرات الكفين المزدوجة الجديدة (Creative Two-Hand Sounds)
# ====================================================================

def generate_two_hand_clap():
    """تصفيق الكفين 👏: ضربة تصفيق حادة يعقبها تصفيق جماهيري وتصفير حماسي"""
    duration = 1.4
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    audio = np.zeros_like(t)

    # 1. صوت الضربة الأولى الحادة (Slap / Clap Impact)
    slap_env = np.exp(-30.0 * t)
    slap_noise = np.random.normal(0, 1, len(t)) * slap_env
    slap_pop = np.sin(2 * np.pi * 180 * t) * np.exp(-40.0 * t)

    # 2. تتابع تصفيقات سريعة متداخلة (Crowd applause bursts)
    clap_times = [0.08, 0.16, 0.23, 0.31, 0.40, 0.50, 0.62, 0.75, 0.90, 1.05]
    crowd = np.zeros_like(t)
    for ct in clap_times:
        idx = int(ct * SAMPLE_RATE)
        sub_t = t[idx:]
        if len(sub_t) > 0:
            c_env = np.exp(-18.0 * (sub_t - ct))
            c_noise = np.random.normal(0, 0.4, len(sub_t)) * c_env
            crowd[idx:] += c_noise

    # 3. صافرة حماسية خفيفة في الخلفية (Stadium Whistle)
    whistle_env = np.clip((t - 0.3) / 0.2, 0, 1) * np.exp(-3.0 * np.maximum(0, t - 0.5))
    whistle = np.sin(2 * np.pi * 2400 * t + 0.3 * np.sin(2 * np.pi * 12 * t)) * whistle_env * 0.3

    audio = slap_noise * 0.7 + slap_pop * 0.5 + crowd * 0.6 + whistle
    return audio / np.max(np.abs(audio) + 1e-9) * 0.9


def generate_kamehameha():
    """الكاميهاميها ⚡: شحن طاقة تصاعدي يعقبه انفجار ليزر هائل (Energy Blast)"""
    duration = 1.5
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    audio = np.zeros_like(t)

    # المرحلة 1: شحن الطاقة (0.0s إلى 0.6s) - تردد يرتفع مع تذبذب كهربائي
    charge_dur = 0.6
    c_mask = t < charge_dur
    c_t = t[c_mask]
    charge_freq = np.linspace(100, 750, len(c_t))
    wobble = 25 * np.sin(2 * np.pi * 35 * c_t)
    c_phase = 2 * np.pi * np.cumsum(charge_freq + wobble) / SAMPLE_RATE
    c_env = np.linspace(0.1, 1.0, len(c_t)) ** 2
    audio[c_mask] = (np.sin(c_phase) + 0.3 * np.sin(2 * c_phase)) * c_env

    # المرحلة 2: الانفجار الهائل وإطلاق الشعاع (0.6s إلى 1.5s)
    b_mask = t >= charge_dur
    b_t = t[b_mask] - charge_dur
    # انفجار sub-bass عميق يهبط بسرعة
    bass_freq = np.linspace(400, 35, len(b_t))
    bass_phase = 2 * np.pi * np.cumsum(bass_freq) / SAMPLE_RATE
    bass_env = np.exp(-3.5 * b_t)
    # زئير ليزر صاخب (Noise burst)
    noise_env = np.exp(-5.0 * b_t)
    laser_noise = np.random.uniform(-1, 1, len(b_t)) * noise_env
    # نغمة رنين شعاع فضائي
    beam_tone = np.sin(2 * np.pi * 950 * np.exp(-4 * b_t) * b_t) * np.exp(-3 * b_t)

    audio[b_mask] = (np.sin(bass_phase) * 0.8 + laser_noise * 0.6 + beam_tone * 0.4) * bass_env

    return audio / np.max(np.abs(audio) + 1e-9) * 0.95


def generate_heart_love():
    """حركة القلب 🫶: نغمة رومانسية ميمز بنكهة الساكسفون (Careless Whisper Vibe)"""
    duration = 1.6
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    audio = np.zeros_like(t)

    # النوتات الرومانسية الشهيرة: D5 -> C5 -> Bb4 -> A4
    notes = [
        (587.33, 0.0, 0.35),  # D5
        (523.25, 0.35, 0.35), # C5
        (466.16, 0.70, 0.35), # Bb4
        (440.00, 1.05, 0.55), # A4
    ]

    for freq, s_time, n_dur in notes:
        s_idx = int(s_time * SAMPLE_RATE)
        e_idx = min(s_idx + int(n_dur * SAMPLE_RATE), len(t))
        sub_len = e_idx - s_idx
        sub_t = np.linspace(0, n_dur, sub_len, False)
        # فيبراتو الساكسفون الناعم
        vib = 7.0 * np.sin(2 * np.pi * 5.5 * sub_t)
        phase = 2 * np.pi * np.cumsum(freq + vib) / SAMPLE_RATE
        # غلاف ناعم (Smooth swell)
        env = np.sin(np.pi * np.clip(sub_t / n_dur, 0, 1)) ** 0.7
        # توافقيات دافئة لمحاكاة آلة النفخ
        sax = (
            np.sin(phase)
            + 0.5 * np.sin(2 * phase)
            + 0.3 * np.sin(3 * phase)
            + 0.15 * np.sin(4 * phase)
        ) * env
        audio[s_idx:e_idx] += sax

    return audio / np.max(np.abs(audio) + 1e-9) * 0.85


def generate_mind_blown():
    """الانفجار الذهني 🤯: ميم Vine Boom الشهير مع صدمة Sub-Bass وتردد سينمائي ضخم"""
    duration = 1.2
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    # هبوط ترددي حاد من 130Hz إلى 30Hz
    freq_curve = 130 * np.exp(-12.0 * t) + 32
    phase = 2 * np.pi * np.cumsum(freq_curve) / SAMPLE_RATE
    # ارتداد جهير قوي (Sub-Bass Boom)
    boom_env = np.exp(-2.5 * t)
    # تشويش انفجاري في الصدمة الأولى (Impact transient)
    transient = np.random.normal(0, 0.8, len(t)) * np.exp(-45.0 * t)
    # موجة مربعة مشبعة خفيفة لإعطاء خشونة الميم الشهير
    bass_wave = np.sin(phase) + 0.35 * np.sin(3 * phase)
    audio = (bass_wave + transient) * boom_env
    return audio / np.max(np.abs(audio) + 1e-9) * 0.95


def generate_timeout():
    """علامة التوقف 🛑: سكراتش أسطوانة الـ DJ ("Wait a minute!") + صافرة حكم حادة"""
    duration = 1.1
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    audio = np.zeros_like(t)

    # 1. سكراتش أسطوانة الفينيل (Record Scratch: 0.0s إلى 0.4s)
    scratch_dur = 0.4
    s_mask = t < scratch_dur
    s_t = t[s_mask]
    scratch_freq = 600 + 400 * np.sin(2 * np.pi * 9 * s_t)
    s_phase = 2 * np.pi * np.cumsum(scratch_freq) / SAMPLE_RATE
    scratch_noise = np.random.uniform(-0.5, 0.5, len(s_t)) * np.sin(np.pi * s_t / scratch_dur)
    s_env = np.sin(np.pi * s_t / scratch_dur)
    audio[s_mask] = (np.sin(s_phase) * 0.6 + scratch_noise * 0.4) * s_env

    # 2. صافرة حكم رياضية حادة (0.45s إلى 1.0s)
    w_start = int(0.45 * SAMPLE_RATE)
    w_t = t[w_start:]
    if len(w_t) > 0:
        w_env = np.exp(-4.0 * (w_t - 0.45))
        # تردد صافرة مزدوجة التردد (Trill whistle)
        w_freq1 = 2800 + 70 * np.sin(2 * np.pi * 30 * w_t)
        w_freq2 = 3100 + 70 * np.sin(2 * np.pi * 30 * w_t)
        whistle = (np.sin(2 * np.pi * w_freq1 * w_t) + np.sin(2 * np.pi * w_freq2 * w_t)) * w_env * 0.5
        audio[w_start:] += whistle

    return audio / np.max(np.abs(audio) + 1e-9) * 0.9


def generate_prayer_choir():
    """ضم الكفين 🙏: كواير ملائكي فخم وهادئ (Angelic Hallelujah Choir Chord)"""
    duration = 1.6
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    # تآلف رباعي ملائكي فخم (C Major 9: C4, E4, G4, B4, D5)
    freqs = [261.63, 329.63, 392.00, 493.88, 587.33]
    audio = np.zeros_like(t)

    # غلاف صوتي تصاعدي ناعم ثم تلاشي بطيء (Angelic swell)
    attack = int(0.3 * SAMPLE_RATE)
    decay = len(t) - attack
    env = np.concatenate([np.linspace(0, 1, attack) ** 1.5, np.exp(-1.8 * np.linspace(0, 1, decay))])

    for i, f in enumerate(freqs):
        # إضافة رنين وتمايل طفيف لمحاكاة أصوات متعددة
        detune = (i % 2 - 0.5) * 1.5
        vibrato = 2.0 * np.sin(2 * np.pi * 4.5 * t)
        phase = 2 * np.pi * (f + detune) * t + vibrato
        voice = np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.1 * np.sin(3 * phase)
        audio += voice * (1.0 / len(freqs))

    audio = audio * env
    return audio / np.max(np.abs(audio) + 1e-9) * 0.85


def generate_finger_guns():
    """مسدسات الأصابع 🔫: طلقتان ليزر خاطفتان متعاقبتان (Dual Pew Pew Blasters)"""
    duration = 0.6
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    audio = np.zeros_like(t)

    # طلقتان متعاقبتان (Shot 1 at 0.0s, Shot 2 at 0.22s)
    shots = [0.0, 0.22]
    for shot_start in shots:
        s_idx = int(shot_start * SAMPLE_RATE)
        sub_t = t[s_idx:]
        if len(sub_t) > 0:
            rel_t = sub_t - shot_start
            shot_env = np.exp(-16.0 * rel_t)
            # انحدار ليزري سريع من 1800Hz إلى 200Hz
            laser_sweep = 1800 * np.exp(-22.0 * rel_t) + 180
            laser_phase = 2 * np.pi * np.cumsum(laser_sweep) / SAMPLE_RATE
            shot = np.sin(laser_phase) * shot_env
            audio[s_idx:] += shot

    return audio / np.max(np.abs(audio) + 1e-9) * 0.85


# ====================================================================
# توليد جميع المؤثرات وحفظها
# ====================================================================

def generate_all_samples():
    create_sounds_directory()

    sound_makers = {
        # أصوات اليد الفردية
        "open_palm.wav": (generate_open_palm, "🖐️ كف مفتوح (Sparkle Chime)"),
        "victory.wav": (generate_victory, "✌️ علامة النصر (Victory Fanfare)"),
        "closed_fist.wav": (generate_closed_fist, "✊ قبضة اليد (Heavy Punch Bonk)"),
        "thumb_up.wav": (generate_thumb_up, "👍 إبهام لأعلى (Success Bell)"),
        "thumb_down.wav": (generate_thumb_down, "👎 إبهام لأسفل (Fail Slide)"),
        "pointing_up.wav": (generate_pointing_up, "☝️ سبابة لأعلى (Laser Zap)"),
        "iloveyou.wav": (generate_iloveyou, "🤟 علامة الروك (Hype Airhorn)"),
        # أصوات الكفين المزدوجة الجديدة
        "two_hand_clap.wav": (generate_two_hand_clap, "👏 تصفيق الكفين (Epic Stadium Clap)"),
        "kamehameha.wav": (generate_kamehameha, "⚡ كاميهاميها (Kamehameha Energy Blast)"),
        "heart_love.wav": (generate_heart_love, "🫶 حركة القلب (Romantic Sax Riff)"),
        "mind_blown.wav": (generate_mind_blown, "🤯 انفجار ذهني (Vine Boom Explosion)"),
        "timeout.wav": (generate_timeout, "🛑 علامة التوقف T (Record Scratch & Whistle)"),
        "prayer_choir.wav": (generate_prayer_choir, "🙏 ضم الكفين (Angelic Hallelujah Choir)"),
        "finger_guns.wav": (generate_finger_guns, "🔫 مسدسات الأصابع (Dual Blaster Pew-Pew)"),
    }

    print("\n" + "=" * 65)
    print(" [توليد المؤثرات الصوتية الشاملة الفردية والمزدوجة في sounds/]")
    print("=" * 65)

    for filename, (func, description) in sound_makers.items():
        filepath = os.path.join(SOUNDS_DIR, filename)
        audio_data = func()
        sf.write(filepath, audio_data, SAMPLE_RATE)
        print(f"  [✓] {filename:<19} | {description}")

    print("=" * 65)
    print(" [تم إنشاء كافة المؤثرات بنجاح وجاهزة للعمل الفوري]")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    generate_all_samples()
