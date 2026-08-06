import argparse
import os
import sys
import time

import config
from audio_player import AudioPlayer
from display_manager import DisplayManager


def fail(message):
    print(f"[FAIL] {message}")
    return 1


def main():
    parser = argparse.ArgumentParser(description="PiMP3bPlus smoke test")
    parser.add_argument(
        "--skip-audio-play",
        action="store_true",
        help="Skip brief audio playback test",
    )
    args = parser.parse_args()

    print("== PiMP3bPlus Smoke Test ==")

    display = DisplayManager()
    if not display.is_hardware_active():
        reason = getattr(display, "simulation_reason", "unknown reason")
        return fail(f"Display is not in hardware mode: {reason}")

    print("[OK] Display hardware initialized")
    display.clear()
    display.draw_text(10, 10, "PiMP3bPlus")
    display.draw_text(10, 35, "Smoke test")
    display.draw_text(10, 60, "Display: OK")
    display.display(partial=False)
    print("[OK] Display draw command sent")

    audio = AudioPlayer()
    if not audio.available:
        return fail("Audio mixer unavailable")

    print("[OK] Audio mixer initialized")
    songs = audio.get_music_list()
    print(f"[INFO] Songs detected: {len(songs)}")
    if not songs:
        print("[WARN] No songs found in music directory. Skipping playback check.")
    elif not args.skip_audio_play:
        first_song = songs[0]
        if not audio.play_song(first_song):
            return fail(f"Failed to play test track: {first_song}")
        print(f"[OK] Playing test track: {first_song}")
        time.sleep(1.5)
        audio.stop()
        print("[OK] Audio playback test completed")

    display.sleep()
    print("[PASS] Smoke test completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
