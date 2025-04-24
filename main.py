import wave
import pygame
import dearpygui.dearpygui as dpg
import os
import shutil

#song class - each instance of this class stores 1 song
class Song:
    def __init__(self, name):
        self.filename = name
        self.Title = name
        self.Author = "Unknown"
        self.Year = "----"
        self.is_playing = False
        self.volume = 1.0
        self.filename_to_play = "Current.wav"
        self.speed = 1.0

    # start music
    def play(self, sender=None, app_data=None):
        if not self.is_playing:
            with wave.open(self.filename, 'rb') as wf:
                params = wf.getparams()
                frames = wf.readframes(wf.getnframes())

            with wave.open(self.filename_to_play, 'wb') as wf_out:
                new_framerate = int(params.framerate * self.speed)
                wf_out.setparams(params._replace(framerate=new_framerate))
                wf_out.writeframes(frames)

            pygame.mixer.init()
            pygame.mixer.music.load(self.filename_to_play)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.is_playing = True

    # stop music
    def stop(self, sender=None, app_data=None):
        if self.is_playing:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.is_playing = False
            os.remove(self.filename_to_play)

    # Increase volume
    def louder(self, sender=None, app_data=None):
        self.volume = min(self.volume + 0.1, 1.0)
        print(self.volume)

    # Decrease volume
    def quieter(self, sender=None, app_data=None):
        self.volume = max(self.volume - 0.1, 0.0)
        print(self.volume)

    def faster(self, sender=None, app_data=None):
        self.speed = min(self.speed + 0.1, 2.0)
        print(self.speed)

    def slower(self, sender=None, app_data=None):
        self.speed = max(self.speed - 0.1, 0.1)
        print(self.speed)

    # analize wav
    def info(self, sender=None, app_data=None):
        with wave.open(self.filename, 'rb') as wf:
            info_text = "Framerate: " + str(wf.getframerate()) + "\n" + "Time: " + str(
                round(wf.getnframes() / wf.getframerate(), 2))
            dpg.set_value("wave_info", info_text)

SongList = []
SongNumber = 0

# FILE IMPORT
def import_file(sender, app_data):
    from tkinter import filedialog, Tk
    Tk().withdraw()
    file_path = filedialog.askopenfilename(title="Choose file", filetypes=[("Wav files", "*.wav")])
    if file_path:
        destination_folder = os.getcwd()
        try:
            shutil.copy(file_path, destination_folder)
            global current_wave_path
            current_wave_path = os.path.basename(file_path)
            print(f"File {current_wave_path} was imported.")
            SongList.append(Song(current_wave_path))
            update_song_list()
        except Exception as e:
            print(f"Failed to import file: {e}")

def ChooseSong(k):
    global SongNumber
    SongNumber = k
    print(k)

def update_song_list():
    dpg.delete_item("SongListWindow", children_only=True)

    for i, song in enumerate(SongList):
        #print("check: " + str(i))
        dpg.add_button(
            label=song.filename,  # title
            callback=lambda a=i: ChooseSong(a-46 - len(SongList)),
            parent="SongListWindow",
            width=200,
            height=50
        )


# cut audio
def cut_audio(input_file, output_file, start_time, end_time):
    with wave.open(input_file, 'rb') as wf:
        params = wf.getparams()
        framerate = params.framerate
        start_frame = int(start_time * framerate)
        end_frame = int(end_time * framerate)

        wf.setpos(start_frame)
        frames = wf.readframes(end_frame - start_frame)

    with wave.open(output_file, 'wb') as wf_out:
        wf_out.setparams(params)
        wf_out.writeframes(frames)

# cut music
def cut_music(sender, app_data):
    cut_audio(current_wave_path, "bitwa_cut.wav", 10, 20)
    pygame.mixer.music.load("bitwa_cut.wav")
    pygame.mixer.music.play()

#exit program
def exit_program():
    dpg.stop_dearpygui()
    dpg.destroy_context()
    exit()

# Main window
if __name__ == "__main__":
    dpg.create_context()

    #load textures
    with dpg.texture_registry():
        width, height, channels, data = dpg.load_image("start.png")
        texture_play = dpg.add_static_texture(width, height, data, tag="texture_play")
        width, height, channels, data = dpg.load_image("stop.png")
        texture_stop = dpg.add_static_texture(width, height, data, tag="texture_stop")
        width, height, channels, data = dpg.load_image("Faster.png")
        texture_faster = dpg.add_static_texture(width, height, data, tag="texture_faster")
        width, height, channels, data = dpg.load_image("Slower.png")
        texture_slower = dpg.add_static_texture(width, height, data, tag="texture_slower")
        width, height, channels, data = dpg.load_image("Louder.png")
        texture_louder = dpg.add_static_texture(width, height, data, tag="texture_louder")
        width, height, channels, data = dpg.load_image("Quieter.png")
        texture_quieter = dpg.add_static_texture(width, height, data, tag="texture_quieter")
        width, height, channels, data = dpg.load_image("Info.png")
        texture_info = dpg.add_static_texture(width, height, data, tag="texture_info")
        width, height, channels, data = dpg.load_image("exit.png")
        texture_exit = dpg.add_static_texture(width, height, data, tag="texture_exit")
        width, height, channels, data = dpg.load_image("file.png")
        texture_file = dpg.add_static_texture(width, height, data, tag="texture_file")

    dpg.create_viewport(title="Music Program", width=1600, height=900, resizable=False, decorated=False)

    #Main Window
    with dpg.window(label="Main Window", width=1600, height=900, tag="MainWindow", no_move=True, no_resize=True):
        # Main section
        with dpg.group(horizontal=True):
            # Buttons
            with dpg.group(tag="ButtonGroup"):
                dpg.add_image_button(callback=lambda: SongList[SongNumber].play(), width=20, height=20,
                                     texture_tag="texture_play")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].stop(), width=20, height=20,
                                     texture_tag="texture_stop")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].louder(), width=20, height=20,
                                     texture_tag="texture_louder")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].quieter(), width=20, height=20,
                                     texture_tag="texture_quieter")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].faster(), width=20, height=20,
                                     texture_tag="texture_faster")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].slower(), width=20, height=20,
                                     texture_tag="texture_slower")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].info(), width=20, height=20,
                                     texture_tag="texture_info")
                dpg.add_image_button(callback=import_file, width=20, height=20, texture_tag="texture_file")
                dpg.add_image_button(callback=lambda: exit_program(), width=20, height=20, texture_tag="texture_exit")
                # dpg.add_button(label="Cut Music (10-20s)", callback=cut_music)

            # Song list
            with dpg.group(tag="SongListWindow"):
                dpg.add_text("Song List:", tag="songlist_title")
                dpg.add_text("No songs added yet.", tag="songlist_content")

        # Under main section
        dpg.add_separator()
        #info
        dpg.add_text("", tag="wave_info")

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()