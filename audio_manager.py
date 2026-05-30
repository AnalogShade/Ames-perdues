import math
import os
import random
import struct
import wave

import pygame


class AudioManager:
    def __init__(self, assets_dir="assets", sample_rate=22050, master_volume=0.5):
        self.assets_dir = assets_dir
        self.sample_rate = sample_rate
        self.master_volume = master_volume

        pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
        self.generate_audio_assets()

        self.sfx_hit = self.load_sound("sfx_hit.wav")
        self.sfx_sword = self.load_sound("sfx_sword.wav")
        self.sfx_hurt = self.load_sound("sfx_hurt.wav")
        self.sfx_victory = self.load_sound("sfx_victory.wav")
        self.sfx_defeat = self.load_sound("sfx_defeat.wav")
        self.apply_volume()

    def asset_path(self, filename):
        return os.path.join(self.assets_dir, filename)

    def load_sound(self, filename):
        return pygame.mixer.Sound(self.asset_path(filename))

    def write_wav(self, filename, samples):
        os.makedirs(self.assets_dir, exist_ok=True)
        path = self.asset_path(filename)
        if os.path.exists(path):
            return

        clamped = [int(max(-32768, min(32767, sample))) for sample in samples]
        packed = struct.pack(f"<{len(clamped)}h", *clamped)

        with wave.open(path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(packed)

    def generate_audio_assets(self):
        sample_rate = self.sample_rate

        hit_samples = []
        num_samples_hit = int(0.25 * sample_rate)
        for i in range(num_samples_hit):
            t = i / sample_rate
            phase = 2 * math.pi * (150 * t - 240 * t * t)
            sq = 0.7 * math.exp(-12 * t) * (1.0 if math.sin(phase) > 0 else -1.0)
            ns = 0.7 * math.exp(-40 * t) * random.uniform(-1.0, 1.0)
            hit_samples.append((sq + ns) * 32767)
        self.write_wav("sfx_hit.wav", hit_samples)

        sword_samples = []
        num_samples_sword = int(0.20 * sample_rate)
        for i in range(num_samples_sword):
            t = i / sample_rate
            phase = 2 * math.pi * (800 * t - 1625 * t * t)
            sq = 0.3 * math.exp(-15 * t) * (1.0 if math.sin(phase) > 0 else -1.0)
            ns = 0.8 * math.exp(-15 * t) * random.uniform(-1.0, 1.0)
            sword_samples.append((sq + ns) * 32767)
        self.write_wav("sfx_sword.wav", sword_samples)

        hurt_samples = []
        num_samples_hurt = int(0.20 * sample_rate)
        for i in range(num_samples_hurt):
            t = i / sample_rate
            phase = 2 * math.pi * 350 * t - 3.75 * math.cos(80 * math.pi * t)
            sq = 0.7 * math.exp(-18 * t) * (1.0 if math.sin(phase) > 0 else -1.0)
            ns = 0.3 * math.exp(-30 * t) * random.uniform(-1.0, 1.0)
            hurt_samples.append((sq + ns) * 32767)
        self.write_wav("sfx_hurt.wav", hurt_samples)

        defeat_samples = []
        notes_def = [261.63, 207.65, 196.00, 174.61]
        phase = 0.0
        for i in range(int(0.8 * sample_rate)):
            t_total = i / sample_rate
            note_idx = min(3, int(t_total / 0.2))
            freq = notes_def[note_idx]
            t_note = (i % int(0.2 * sample_rate)) / sample_rate
            env = 0.6 * math.exp(-8 * t_note)
            phase += 2 * math.pi * freq / sample_rate
            sq = 1.0 if math.sin(phase) > 0 else -1.0
            defeat_samples.append(sq * env * 32767)
        self.write_wav("sfx_defeat.wav", defeat_samples)

        victory_samples = []
        notes_vic = [261.63, 329.63, 392.00, 523.25]
        phase = 0.0
        for i in range(int(0.6 * sample_rate)):
            t_total = i / sample_rate
            note_idx = min(3, int(t_total / 0.15))
            freq = notes_vic[note_idx]
            t_note = (i % int(0.15 * sample_rate)) / sample_rate
            env = 0.5 * math.exp(-5 * t_note)
            phase += 2 * math.pi * freq / sample_rate
            tri = 4.0 * abs((phase % (2 * math.pi)) / (2 * math.pi) - 0.5) - 1.0
            victory_samples.append(tri * env * 32767)
        self.write_wav("sfx_victory.wav", victory_samples)

        music_samples = []
        bass_notes = [
            55.00, 55.00, 55.00, 55.00, 55.00, 55.00, 55.00, 55.00,
            65.41, 65.41, 65.41, 65.41, 65.41, 65.41, 65.41, 65.41,
            73.42, 73.42, 73.42, 73.42, 73.42, 73.42, 73.42, 73.42,
            82.41, 82.41, 82.41, 82.41, 82.41, 82.41, 82.41, 82.41,
        ]
        melody_notes = [
            440.00, 493.88, 523.25, 659.25,
            587.33, 523.25, 493.88, 415.30,
        ]

        phase_bass = 0.0
        phase_mel = 0.0
        step_duration = 0.25

        for i in range(int(8.0 * sample_rate)):
            t = i / sample_rate
            step_idx = min(31, int(t / step_duration))
            mel_idx = min(7, int(t / 1.0))
            t_step = t % step_duration
            t_note = t % 1.0

            freq_bass = bass_notes[step_idx]
            phase_bass += 2 * math.pi * freq_bass / sample_rate
            tri_bass = 4.0 * abs((phase_bass % (2 * math.pi)) / (2 * math.pi) - 0.5) - 1.0
            env_bass = 0.45 * math.exp(-12 * t_step)

            freq_mel = melody_notes[mel_idx]
            phase_mel += 2 * math.pi * freq_mel / sample_rate
            sq_mel = 1.0 if math.sin(phase_mel) > 0 else -1.0
            env_mel = 0.25 * math.exp(-1.5 * t_note)

            music_samples.append((tri_bass * env_bass + sq_mel * env_mel) * 32767)
        self.write_wav("music.wav", music_samples)

    def apply_volume(self):
        self.sfx_hit.set_volume(self.master_volume)
        self.sfx_sword.set_volume(self.master_volume)
        self.sfx_hurt.set_volume(self.master_volume)
        self.sfx_victory.set_volume(self.master_volume)
        self.sfx_defeat.set_volume(self.master_volume)
        pygame.mixer.music.set_volume(self.master_volume)

    def increase_volume(self, step=0.1):
        self.master_volume = min(1.0, self.master_volume + step)
        self.apply_volume()

    def decrease_volume(self, step=0.1):
        self.master_volume = max(0.0, self.master_volume - step)
        self.apply_volume()

    def play_music(self):
        try:
            pygame.mixer.music.load(self.asset_path("music.wav"))
            pygame.mixer.music.play(-1)
        except Exception as exc:
            print("Erreur de chargement de la musique:", exc)

    def stop_music(self):
        pygame.mixer.music.stop()

    def play_hit(self):
        self.sfx_hit.play()

    def play_sword(self):
        self.sfx_sword.play()

    def play_hurt(self):
        self.sfx_hurt.play()

    def play_victory(self):
        self.sfx_victory.play()

    def play_defeat(self):
        self.sfx_defeat.play()
