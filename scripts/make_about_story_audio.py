#!/usr/bin/env python3
"""
Render the About panel's "Listen to the story" narration to MP3 with Google Cloud Text-to-Speech.

Reads   scripts/narration/about-story.{en,de}.txt   (paragraphs separated by blank lines)
Writes  public/audio/about-story.{en,de}.mp3

Re-run whenever a narration text changes. The site plays these files and only falls back to the
browser's built-in speech if one fails to load.

Setup (once):
    pip install google-auth==2.58.0 urllib3 soundfile==0.14.0
    A Google Cloud project with the Cloud Text-to-Speech API enabled (billing on), and one way to
    sign in (service-account keys are blocked by this organisation's policy, so not those):
      a) an API key restricted to the Cloud Text-to-Speech API, saved in a text file kept OUTSIDE
         this repository, passed with --api-key-file; or
      b) the Google Cloud CLI:  gcloud auth application-default login
                                gcloud auth application-default set-quota-project PROJECT_ID
         after which no option is needed — the script picks that login up automatically.

Usage:
    # list the voices Google offers for a language
    python scripts/make_about_story_audio.py [--api-key-file KEY.txt] --list-voices de-DE
    # render the first paragraph with several voices, to choose by ear
    python scripts/make_about_story_audio.py [--api-key-file KEY.txt] --lang de --samples DIR \
        --voices de-DE-Chirp3-HD-Leda de-DE-Chirp3-HD-Charon
    # render the full narration(s) with the voices set in VOICES below
    python scripts/make_about_story_audio.py [--api-key-file KEY.txt]
"""
import argparse
import base64
import io
import json
import sys
from pathlib import Path

import google.auth
import numpy as np
import soundfile as sf
import urllib3
from google.auth.transport.urllib3 import Request as AuthRequest

REPO = Path(__file__).resolve().parent.parent
TEXT_DIR = REPO / "scripts" / "narration"
OUT_DIR = REPO / "public" / "audio"

API = "https://texttospeech.googleapis.com/v1"
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

# Chirp 3 HD: Google's most natural voice family. Chosen by ear from comparison reels of 13 voices.
VOICES = {
    "en": {"code": "en-GB", "name": "en-GB-Chirp3-HD-Vindemiatrix"},
    "de": {"code": "de-DE", "name": "de-DE-Chirp3-HD-Laomedeia"},
}

SPEAKING_RATE = 0.95     # a touch slower than default: a story, not an announcement
SAMPLE_RATE = 24000
PARAGRAPH_PAUSE_S = 0.8  # between paragraphs; the voice paces its own sentences
LEAD_IN_S, TAIL_S = 0.25, 0.6
TARGET_LUFS = -20.0      # integrated loudness (mono), so every file plays equally loud; low enough
                         # that both chosen voices reach it without their peaks hitting PEAK_DBFS
PEAK_DBFS = -1.0         # ceiling: a voice whose peaks would pass it is turned down instead
# libsndfile's MP3 compression level (0 = best/largest, 1 = smallest); constant bitrate. The site
# only fetches the file when someone presses the button.
MP3_COMPRESSION = 0.6


class GoogleTts:
    def __init__(self, api_key_file=None):
        self.http = urllib3.PoolManager()
        self.api_key = api_key_file.read_text(encoding="utf-8").strip() if api_key_file else None
        # Without an API key, use the login saved by `gcloud auth application-default login`.
        self.creds = None if self.api_key else google.auth.default(scopes=SCOPES)[0]

    def _call(self, method, path, body=None):
        # Credentials always travel in headers, never in the URL.
        headers = {"Content-Type": "application/json; charset=utf-8"}
        if self.api_key:
            headers["X-Goog-Api-Key"] = self.api_key
        else:
            if not self.creds.valid:
                self.creds.refresh(AuthRequest(self.http))
            self.creds.apply(headers)  # bearer token, plus the quota-project header user logins need
        r = self.http.request(method, f"{API}/{path}", headers=headers,
                              body=json.dumps(body).encode("utf-8") if body is not None else None)
        data = json.loads(r.data.decode("utf-8") or "{}")
        if r.status != 200:
            sys.exit(f"Google Text-to-Speech refused the request (HTTP {r.status}): "
                     f"{data.get('error', {}).get('message', data)}")
        return data

    def voices(self, language_code):
        return self._call("GET", f"voices?languageCode={language_code}").get("voices", [])

    def synthesize(self, text, language_code, voice_name):
        body = {
            "input": {"text": text},
            "voice": {"languageCode": language_code, "name": voice_name},
            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": SAMPLE_RATE, "speakingRate": SPEAKING_RATE},
        }
        wav = base64.b64decode(self._call("POST", "text:synthesize", body)["audioContent"])
        audio, sr = sf.read(io.BytesIO(wav), dtype="float32")  # LINEAR16 arrives as a WAV file
        return audio, sr


def paragraphs(lang):
    text = (TEXT_DIR / f"about-story.{lang}.txt").read_text(encoding="utf-8")
    return [" ".join(p.split()) for p in text.split("\n\n") if p.strip()]


def render(tts, lang, voice_name, paras):
    parts, sr = [], SAMPLE_RATE
    silence = lambda s: np.zeros(int(s * sr), dtype=np.float32)
    parts.append(silence(LEAD_IN_S))
    for i, p in enumerate(paras):
        audio, sr = tts.synthesize(p, VOICES[lang]["code"], voice_name)
        parts.append(audio)
        if i < len(paras) - 1:
            parts.append(silence(PARAGRAPH_PAUSE_S))
    parts.append(silence(TAIL_S))
    return np.concatenate(parts), sr


def _k_weighting(sr):
    """BS.1770's K-weighting as two biquads (b, a): a +4 dB shelf above ~1.5 kHz, then a ~38 Hz high-pass."""
    w, q = 2 * np.pi * 1500.0 / sr, 1 / np.sqrt(2)
    A, al, c = 10 ** (4.0 / 40), np.sin(w) / (2 * q), np.cos(w)
    shelf = ([A * ((A + 1) + (A - 1) * c + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * c),
              A * ((A + 1) + (A - 1) * c - 2 * np.sqrt(A) * al)],
             [(A + 1) - (A - 1) * c + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * c),
              (A + 1) - (A - 1) * c - 2 * np.sqrt(A) * al])
    w, q = 2 * np.pi * 38.0 / sr, 0.5
    al, c = np.sin(w) / (2 * q), np.cos(w)
    high_pass = ([(1 + c) / 2, -(1 + c), (1 + c) / 2], [1 + al, -2 * c, 1 - al])
    return [shelf, high_pass]


def loudness_lufs(audio, sr):
    """Integrated loudness of a mono signal (ITU-R BS.1770: K-weighted, gated 400 ms blocks)."""
    x = audio.astype(np.float64)
    z1 = np.exp(-2j * np.pi * np.fft.rfftfreq(len(x), 1 / sr) / sr)  # z^-1 around the unit circle
    response = np.ones_like(z1)
    for b, a in _k_weighting(sr):
        response *= (b[0] + b[1] * z1 + b[2] * z1 ** 2) / (a[0] + a[1] * z1 + a[2] * z1 ** 2)
    y = np.fft.irfft(np.fft.rfft(x) * response, n=len(x))
    block, step = int(0.4 * sr), int(0.1 * sr)
    energy = np.concatenate([[0.0], np.cumsum(y ** 2)])
    starts = np.arange(0, len(y) - block + 1, step)
    power = (energy[starts + block] - energy[starts]) / block
    lufs = lambda p: -0.691 + 10 * np.log10(p + 1e-20)
    power = power[lufs(power) > -70]                          # absolute gate: skip silence
    power = power[lufs(power) > lufs(power.mean()) - 10]      # relative gate: skip pauses
    return float(lufs(power.mean()))


def level_together(clips, sr, target=TARGET_LUFS):
    """Bring every clip to one loudness: TARGET_LUFS, or lower if a clip's peaks would pass PEAK_DBFS."""
    levels = [loudness_lufs(c, sr) for c in clips]
    for c, lufs in zip(clips, levels):
        peak_db = 20 * np.log10(float(np.abs(c).max()) or 1.0)
        target = min(target, PEAK_DBFS - (peak_db - lufs))
    return [c * np.float32(10 ** ((target - lufs) / 20)) for c, lufs in zip(clips, levels)], target


def write_mp3(path, audio, sr):
    path.parent.mkdir(parents=True, exist_ok=True)
    with sf.SoundFile(path, "w", samplerate=sr, channels=1, format="MP3", subtype="MPEG_LAYER_III",
                      compression_level=MP3_COMPRESSION, bitrate_mode="CONSTANT") as f:
        f.write(audio)
    secs, size = len(audio) / sr, path.stat().st_size
    print(f"{path}: {secs:.0f}s, {size / 1024:.0f} KB, ~{size * 8 / secs / 1000:.0f} kbps")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--api-key-file", type=Path, help="text file holding a Text-to-Speech-restricted API key "
                                                      "(keep it outside the repo); omit to use the gcloud CLI login")
    ap.add_argument("--lang", nargs="+", choices=sorted(VOICES), default=sorted(VOICES))
    ap.add_argument("--list-voices", metavar="LANGUAGE_CODE", help="e.g. de-DE or en-GB")
    ap.add_argument("--samples", type=Path, metavar="DIR", help="render only the first paragraph, once per --voices entry")
    ap.add_argument("--voices", nargs="+", help="voice names for --samples")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    tts = GoogleTts(args.api_key_file)

    if args.list_voices:
        for v in sorted(tts.voices(args.list_voices), key=lambda v: v["name"]):
            print(f"{v['name']:<40} {v.get('ssmlGender', ''):<8} {', '.join(v.get('languageCodes', []))}")
        return

    if args.samples:
        if not args.voices or len(args.lang) != 1:
            sys.exit("--samples needs exactly one --lang and at least one --voices name")
        lang = args.lang[0]
        first = paragraphs(lang)[:1]
        # One shared loudness, so no sample sounds "better" just for being louder.
        clips, target = level_together([render(tts, lang, name, first)[0] for name in args.voices], SAMPLE_RATE)
        for name, audio in zip(args.voices, clips):
            write_mp3(args.samples / f"{name}.mp3", audio, SAMPLE_RATE)
        print(f"All samples at {target:.1f} LUFS")
        return

    for lang in args.lang:
        name = VOICES[lang]["name"]
        if not name:
            sys.exit(f"No voice chosen for '{lang}' yet: set VOICES['{lang}']['name'] (see --list-voices / --samples)")
        audio, sr = render(tts, lang, name, paragraphs(lang))
        (audio,), target = level_together([audio], sr)
        write_mp3(args.out_dir / f"about-story.{lang}.mp3", audio, sr)
        print(f"  at {target:.1f} LUFS")


if __name__ == "__main__":
    main()
