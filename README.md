# 🖐️🔊 AI Hand-Gesture Soundboard

A real-time, low-latency **AI Hand-Gesture Controlled Soundboard** that translates webcam hand movements into audio sound effects and routes them directly into your **Microphone Input (Discord, Games, Zoom, OBS)** using Virtual Audio Cable, with simultaneous playback into your own headphones.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange?logo=google)
![SoundDevice](https://img.shields.io/badge/Audio-SoundDevice%20%2F%20PortAudio-red)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)

---

## 🌟 Key Features

* **Real-Time Hand Tracking**: Powered by Google MediaPipe Vision Tasks for ultra-smooth 60+ FPS tracking with minimal CPU footprint.
* **Direct Virtual Microphone Routing**: Sends audio directly to **VB-Audio Virtual Cable** (`CABLE Input`) so people in Discord, Steam voice chats, or games hear your soundboard as your microphone.
* **Dual Audio Monitoring (Mirror Playback)**: Simultaneously outputs sounds to both the virtual cable (for your friends) and your local headphones/speakers (so you can hear what you just triggered).
* **RAM Audio Pre-Caching**: All sounds are loaded into memory at startup for zero-latency (< 2ms) instant response.
* **Cooldown & Debounce Engine**: Per-gesture timers and release-to-rearm logic prevent accidental double-triggering or stutter while holding a gesture.
* **Interactive HUD Overlay**: Displays a sleek futuristic head-up display with hand skeleton joints, confidence score, cooldown progress bar, and real-time FPS counter.
* **Custom Sounds Ready**: Easily drop any `.wav` or `.mp3` files into the `sounds/` directory.

---

## 🖐️ Hand Gestures & Default Sounds

| Emoji | Gesture | Description | Sound Effect |
| :---: | :--- | :--- | :--- |
| 🖐️ | **Open Palm** | Open flat hand with spread fingers | **Sparkle Welcome Chime** |
| ✌️ | **Victory** | Index and middle finger raised (V sign) | **Victory Fanfare / Level Up** |
| ✊ | **Closed Fist** | Fully closed fist | **Heavy Punch / Bonk Impact** |
| 👍 | **Thumb Up** | Closed fist with thumb pointing upward | **Crystal Success Bell / Ding** |
| 👎 | **Thumb Down** | Closed fist with thumb pointing downward | **Sad Fail Trombone Slide** |
| ☝️ | **Pointing Up** | Index finger pointing straight up | **Sci-Fi Laser Zap** |
| 🤟 | **Rock / Love** | Extended thumb, index, and pinky | **Hype Meme Airhorn** |

---

## 📁 Project Structure

```
hand-gesture-soundboard/
├── hand_soundboard.py     # Main application (Webcam loop, MediaPipe, Audio routing, HUD)
├── config.py              # Configuration file (Device IDs, cooldown timers, mappings)
├── list_devices.py        # Audio device inspection utility
├── generate_samples.py    # Algorithmic DSP generator for 7 clean WAV sound effects
├── requirements.txt       # Python dependencies
├── run_soundboard.bat     # One-click launcher for Windows
└── sounds/                # Sound effects directory (.wav / .mp3)
    ├── open_palm.wav
    ├── victory.wav
    ├── closed_fist.wav
    ├── thumb_up.wav
    ├── thumb_down.wav
    ├── pointing_up.wav
    └── iloveyou.wav
```

---

## ⚡ Quick Start

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/Kimobest/hand-gesture-soundboard.git
cd hand-gesture-soundboard
pip install -r requirements.txt
```

### 2. Verify Audio Devices

Run the audio device explorer to check your sound cards and Virtual Cable:

```bash
python list_devices.py
```

### 3. Launch the Soundboard

Run via command line or double-click `run_soundboard.bat`:

```bash
python hand_soundboard.py
```

* Press **`Q`** or **`ESC`** at any time to exit cleanly.

---

## 🎙️ Routing Audio to Discord / Games (Microphone Integration)

To let friends in **Discord** hear your real voice **and** your soundboard effects together with zero lag:

### Step 1: Install Virtual Cable
Download and install [VB-Audio Virtual Cable](https://vb-audio.com/Cable/) (Free).

### Step 2: Combine Real Mic with Soundboard (Windows Native Zero-Lag Trick)
1. Press `Win + R`, type `mmsys.cpl`, and hit `Enter` to open the Windows Sound Control Panel.
2. Go to the **Recording** tab.
3. Right-click your **Real Microphone** -> **Properties**.
4. Go to the **Listen** tab:
   * Check **"Listen to this device"**.
   * Under **"Playback through this device"**, select **`CABLE Input (VB-Audio Virtual Cable)`**.
5. Click **Apply** -> **OK**.

> **Result:** Your voice and the Python soundboard both feed directly into `CABLE Input` without using any third-party mixing software or CPU resources!

### Step 3: Discord Voice Settings
In Discord, go to **User Settings ⚙️ -> Voice & Video**:
1. **Input Device**: Select **`CABLE Output (VB-Audio Virtual Cable)`**.
2. **Output Device**: Select your normal headphones/speakers.
3. **Important**: Under **Voice Processing**, set **Noise Suppression** to **None** or **Standard** (Avoid *Krisp* because Krisp's AI filter might mute soundboard sound effects thinking they are background noise).

---

## 🎛️ Customization

Edit `config.py` to customize:
* `COOLDOWN_SECONDS`: Delay between triggers (default: `2.0`s).
* `VOLUME_CABLE`: Volume sent to Discord/mic (0.0 to 1.0).
* `VOLUME_MONITOR`: Volume in your own headphones (0.0 to 1.0).
* `GESTURE_SOUND_MAP`: Map any gesture to your own custom `.mp3` or `.wav` files.

---

## 📜 License

MIT License. Free to use, modify, and distribute for personal and commercial projects.
