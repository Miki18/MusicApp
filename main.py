import wave
import pygame
import dearpygui.dearpygui as dpg

# Globalne zmienne
current_wave_path = "bitwa.wav"
is_playing = False
volume = 1.0  # Głośność (od 0.0 do 1.0)
speed = 1.0

def change_speed(input_file, output_file, speed_factor):
    with wave.open(input_file, 'rb') as wf:
        params = wf.getparams()  # Pobranie parametrów pliku
        frames = wf.readframes(wf.getnframes())

    # Nowy obiekt dla pliku wyjściowego
    with wave.open(output_file, 'wb') as wf_out:
        # Zmiana częstotliwości próbkowania
        new_framerate = int(params.framerate * speed_factor)
        wf_out.setparams(params._replace(framerate=new_framerate))
        wf_out.writeframes(frames)

# Przyspieszenie utworu o 50%
change_speed("bitwa.wav", "bitwa_faster.wav", 1.5)

# Spowolnienie utworu o 50%
change_speed("bitwa.wav", "bitwa_slower.wav", 0.5)

def cut_audio(input_file, output_file, start_time, end_time):
    with wave.open(input_file, 'rb') as wf:
        params = wf.getparams()
        framerate = params.framerate
        n_channels = params.nchannels
        start_frame = int(start_time * framerate)
        end_frame = int(end_time * framerate)

        # Wycinanie ramek
        wf.setpos(start_frame)
        frames = wf.readframes(end_frame - start_frame)

    # Zapis wyciętego fragmentu do nowego pliku
    with wave.open(output_file, 'wb') as wf_out:
        wf_out.setparams(params)
        wf_out.writeframes(frames)

# Wycięcie fragmentu od 10 do 20 sekundy
cut_audio("bitwa.wav", "bitwa_cut.wav", 10, 20)

# Funkcja do odtwarzania muzyki
def play_music(sender, app_data):
    global is_playing
    if not is_playing:
        pygame.mixer.init()
        pygame.mixer.music.load(current_wave_path)
        pygame.mixer.music.set_volume(volume)  # Ustawienie początkowej głośności
        pygame.mixer.music.play()
        is_playing = True

# Funkcja do zatrzymania muzyki
def stop_music(sender, app_data):
    global is_playing
    if is_playing:
        pygame.mixer.music.stop()
        is_playing = False

# Funkcja do zwiększania głośności
def make_louder(sender, app_data):
    global volume
    volume = min(volume + 0.1, 1.0)  # Maksymalna głośność to 1.0
    pygame.mixer.music.set_volume(volume)
    print(f"Głośność: {volume}")

# Funkcja do zmniejszania głośności
def make_quieter(sender, app_data):
    global volume
    volume = max(volume - 0.1, 0.0)  # Minimalna głośność to 0.0
    pygame.mixer.music.set_volume(volume)
    print(f"Głośność: {volume}")

def faster_music(sender, app_data):
    change_speed(current_wave_path, "bitwa_faster.wav", 1.5)
    pygame.mixer.music.load("bitwa_faster.wav")
    pygame.mixer.music.play()

def slower_music(sender, app_data):
    change_speed(current_wave_path, "bitwa_slower.wav", 0.5)
    pygame.mixer.music.load("bitwa_slower.wav")
    pygame.mixer.music.play()

def cut_music(sender, app_data):
    cut_audio(current_wave_path, "bitwa_cut.wav", 10, 20)
    pygame.mixer.music.load("bitwa_cut.wav")
    pygame.mixer.music.play()


# Funkcja do analizy pliku za pomocą wave
def get_wave_info(file_path):
    with wave.open(file_path, 'rb') as wf:
        return {
            "Channels": wf.getnchannels(),
            "Sample Width": wf.getsampwidth(),
            "Frame Rate (Hz)": wf.getframerate(),
            "Number of Frames": wf.getnframes(),
            "Duration (s)": round(wf.getnframes() / wf.getframerate(), 2)
        }

# Funkcja do wyświetlania informacji w GUI
def show_wave_info(sender, app_data):
    info = get_wave_info(current_wave_path)
    info_text = "\n".join([f"{key}: {value}" for key, value in info.items()])
    dpg.set_value("wave_info", info_text)

if __name__ == "__main__":
    # Inicjalizacja Dear PyGui
    dpg.create_context()
    dpg.create_viewport(title="Music Program", width=600, height=700)

    # Tworzenie okna aplikacji
    with dpg.window(label="Main Window", width=400, height=300) as main_window:
        dpg.add_text("Program do odtwarzania muzyki")
        dpg.add_button(label="Play Music", callback=play_music)
        dpg.add_button(label="Stop Music", callback=stop_music)
        dpg.add_button(label="Głośniej", callback=make_louder)
        dpg.add_button(label="Ciszej", callback=make_quieter)
        dpg.add_button(label="Faster Music", callback=faster_music)
        dpg.add_button(label="Slower Music", callback=slower_music)
        dpg.add_button(label="Cut Music (10-20s)", callback=cut_music)
        dpg.add_button(label="Show Info", callback=show_wave_info)
        dpg.add_text("", tag="wave_info")  # Obszar na informacje o pliku .wav

    # Uruchomienie Dear PyGui
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
