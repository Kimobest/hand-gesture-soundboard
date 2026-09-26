"""
====================================================================
أداة فحص واستعراض أجهزة الصوت في النظام (Audio Device Explorer)
====================================================================
هذا السكريبت يقوم بقراءة كافة أجهزة الإدخال والإخراج المتاحة في Windows
وعرض أرقام الـ IDs الخاصة بكل جهاز، مع تمييز تلقائي لأجهزة:
1. Virtual Cable (CABLE Input - المخصص لإرسال المؤثرات لديسكورد)
2. الميكروفونات الحقيقية (Microphones)
3. السماعات العادية (Speakers / Headphones)
====================================================================
"""

import sys
import sounddevice as sd

# ضمان دعم الترميز UTF-8 في موجه أوامر ويندوز لمنع أخطاء الرموز
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def list_audio_devices():
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()

    print("\n" + "=" * 75)
    print(" [Audio Devices] قائمة أجهزة الصوت المكتشفة في النظام")
    print("=" * 75)

    suggested_cable_in = None
    suggested_cable_out = None
    suggested_mic = None
    suggested_speakers = None

    default_input_id = sd.default.device[0]
    default_output_id = sd.default.device[1]

    print(f"\n[!] الجهاز الافتراضي للإدخال (Default Input): ID #{default_input_id}")
    print(f"[!] الجهاز الافتراضي للإخراج (Default Output): ID #{default_output_id}\n")

    print("-" * 75)
    print(f"{'ID':<4} | {'نوع الجهاز':<16} | {'الاسم':<35} | {'API':<12}")
    print("-" * 75)

    for i, dev in enumerate(devices):
        api_name = hostapis[dev['hostapi']]['name']
        name = dev['name']
        max_in = dev['max_input_channels']
        max_out = dev['max_output_channels']

        dev_type = []
        if max_in > 0:
            dev_type.append("Input (مايك)")
        if max_out > 0:
            dev_type.append("Output (مخرج)")
        type_str = " & ".join(dev_type)

        tag = ""
        lower_name = name.lower()

        # الكشف عن مخرج CABLE الافتراضي (الذي يبث له الساوند بورد)
        if ("cable input" in lower_name or "vb-audio virtual" in lower_name or ("vb-audio" in lower_name and "cable" in lower_name)) and max_out > 0:
            tag = "  <-- * [VB-Cable Playback - مخرج الساوند بورد]"
            if suggested_cable_in is None:
                suggested_cable_in = (i, name, api_name)

        # الكشف عن CABLE Output (مدخل المايك في ديسكورد)
        elif "cable output" in lower_name and max_in > 0:
            tag = "  <-- [CABLE Output - اختاره كمايك في ديسكورد]"
            if suggested_cable_out is None:
                suggested_cable_out = (i, name, api_name)

        # الكشف عن المايك الحقيقي
        elif max_in > 0 and "cable" not in lower_name and "streaming" not in lower_name and "mapper" not in lower_name:
            if suggested_mic is None and ("usb" in lower_name or "realtek" in lower_name or "mic" in lower_name):
                suggested_mic = (i, name, api_name)

        # الكشف عن السماعة الأساسية لسماع الصوت
        elif max_out > 0 and "cable" not in lower_name and "streaming" not in lower_name and "mapper" not in lower_name:
            if suggested_speakers is None and ("speakers" in lower_name or "headphones" in lower_name):
                suggested_speakers = (i, name, api_name)

        print(f"[{i:2d}] | {type_str:<16} | {name[:34]:<35} | {api_name:<12}{tag}")

    print("=" * 75)
    print(" [التوصيات المقترحة للاستخدام في ملف config.py]")
    print("=" * 75)

    if suggested_cable_in:
        print(f"[+] مخرج الكيبل الافتراضي (CABLE_INPUT_ID): {suggested_cable_in[0]}  -> ({suggested_cable_in[1]}) [{suggested_cable_in[2]}]")
    else:
        print("[-] لم يتم العثور على VB-Audio CABLE Input. يرجى تثبيت VB-Cable أولاً.")

    if suggested_speakers:
        print(f"[+] سماعتك الشخصية للمراقبة (MONITOR_OUTPUT_ID): {suggested_speakers[0]}  -> ({suggested_speakers[1]}) [{suggested_speakers[2]}]")

    if suggested_mic:
        print(f"[+] المايك الحقيقي الخاص بك (REAL_MIC_ID): {suggested_mic[0]}  -> ({suggested_mic[1]}) [{suggested_mic[2]}]")

    print("\n* ملاحظة: يمكنك وضع هذه الأرقام في ملف config.py لربط السكريبت مباشرة بمخارج الصوت الصحيحة.")


if __name__ == "__main__":
    list_audio_devices()
