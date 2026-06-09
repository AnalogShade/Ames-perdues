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
        # Suppression du cache de fichier pour toujours générer les nouvelles modifications sonores
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
        num_samples_hit = int(0.20 * sample_rate)
        prev_ns = 0.0
        for i in range(num_samples_hit):
            t = i / sample_rate
            phase = 2 * math.pi * (140 * t - 200 * t * t)
            tri = 4.0 * abs((phase % (2 * math.pi)) / (2 * math.pi) - 0.5) - 1.0
            env = 0.8 * math.exp(-14 * t)
            
            ns = random.uniform(-1.0, 1.0)
            lp_ns = 0.3 * ns + 0.7 * prev_ns
            prev_ns = lp_ns
            env_ns = 0.6 * math.exp(-35 * t)
            
            hit_samples.append((tri * env + lp_ns * env_ns) * 32767)
        self.write_wav("sfx_hit.wav", hit_samples)

        sword_samples = []
        num_samples_sword = int(0.22 * sample_rate)
        prev_noise = 0.0
        for i in range(num_samples_sword):
            t = i / sample_rate
            env = math.sin((t / 0.22) * math.pi) ** 1.5
            
            white_noise = random.uniform(-1.0, 1.0)
            lp_noise = 0.25 * white_noise + 0.75 * prev_noise
            prev_noise = lp_noise
            
            freq = 600 - 300 * (t / 0.22)
            phase = 2 * math.pi * freq * t
            sine_tone = math.sin(phase) * 0.15
            
            sword_samples.append((lp_noise * 0.45 + sine_tone) * env * 32767)
        self.write_wav("sfx_sword.wav", sword_samples)

        hurt_samples = []
        num_samples_hurt = int(0.25 * sample_rate)
        prev_ns = 0.0
        for i in range(num_samples_hurt):
            t = i / sample_rate
            phase = 2 * math.pi * 220 * t - 2.5 * math.cos(60 * math.pi * t)
            tri = 4.0 * abs((phase % (2 * math.pi)) / (2 * math.pi) - 0.5) - 1.0
            env = 0.65 * math.exp(-12 * t)
            
            ns = random.uniform(-1.0, 1.0)
            lp_ns = 0.4 * ns + 0.6 * prev_ns
            prev_ns = lp_ns
            env_ns = 0.35 * math.exp(-20 * t)
            
            hurt_samples.append((tri * env + lp_ns * env_ns) * 32767)
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
        
        melody_sequence = [
            220.00, 0.00,   261.63, 293.66, 329.63, 0.00,   392.00, 329.63,
            293.66, 0.00,   220.00, 0.00,   261.63, 0.00,   220.00, 0.00,
            220.00, 261.63, 293.66, 329.63, 392.00, 0.00,   440.00, 392.00,
            329.63, 0.00,   293.66, 0.00,   261.63, 293.66, 220.00, 0.00
        ]

        delay_seconds = 0.35
        delay_samples = int(delay_seconds * sample_rate)
        delay_buffer = [0.0] * delay_samples
        delay_index = 0
        delay_feedback = 0.45
        delay_mix = 0.35

        phase_bass = 0.0
        phase_mel = 0.0
        step_duration = 0.25

        for i in range(int(8.0 * sample_rate)):
            t = i / sample_rate
            step_idx = min(31, int(t / step_duration))
            t_step = t % step_duration

            # Bass synth (onde triangle basse et douce)
            freq_bass = bass_notes[step_idx]
            phase_bass += 2 * math.pi * freq_bass / sample_rate
            tri_bass = 4.0 * abs((phase_bass % (2 * math.pi)) / (2 * math.pi) - 0.5) - 1.0
            env_bass = 0.35 * math.exp(-6.0 * t_step)

            # Melody synth (onde triangle mélodique)
            freq_mel = melody_sequence[step_idx]
            if freq_mel > 0:
                phase_mel += 2 * math.pi * freq_mel / sample_rate
                tri_mel = 4.0 * abs((phase_mel % (2 * math.pi)) / (2 * math.pi) - 0.5) - 1.0
                env_mel = 0.15 * math.exp(-2.5 * t_step)
                raw_mel = tri_mel * env_mel
            else:
                raw_mel = 0.0

            # Ligne de délai (écho)
            delayed_sample = delay_buffer[delay_index]
            delay_buffer[delay_index] = raw_mel + delayed_sample * delay_feedback
            delay_index = (delay_index + 1) % delay_samples
            
            mel_with_echo = raw_mel + delayed_sample * delay_mix

            music_samples.append((tri_bass * env_bass + mel_with_echo) * 32767)
        self.write_wav("music.wav", music_samples)

    def apply_volume(self):
        self.sfx_hit.set_volume(self.master_volume * 0.7)
        self.sfx_sword.set_volume(self.master_volume * 0.6)
        self.sfx_hurt.set_volume(self.master_volume * 0.8)
        self.sfx_victory.set_volume(self.master_volume * 0.5)
        self.sfx_defeat.set_volume(self.master_volume * 0.5)
        pygame.mixer.music.set_volume(self.master_volume * 0.4)

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
