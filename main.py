import pygame
import wave
import time
import os
import shutil
import dearpygui.dearpygui as dpg

#song class - each instance of this class stores 1 song
class Song:
    def __init__(self, name, Title, Author, Year):
        self.filename = name
        self.Title = name
        self.Author = Author
        self.Year = Year
        self.volume = 0.5
        self.filename_to_play = "Current.wav"
        self.speed = 1.0

        #for time menagement
        self.need_reload = True
        self.is_playing = False
        self.paused_time = 0

    def get_duration(self):
        with wave.open(self.filename, 'rb') as wf:
            framerate = wf.getframerate()
            frames = wf.getnframes()
            return frames / framerate  # Czas trwania w sekundach

    # start music
    def play(self, sender=None, app_data=None):
        if self.need_reload:
            with wave.open(self.filename, 'rb') as wf:
                params = wf.getparams()
                frames = wf.readframes(wf.getnframes())

            with wave.open(self.filename_to_play, 'wb') as wf_out:
                new_framerate = int(params.framerate * self.speed)
                wf_out.setparams(params._replace(framerate=new_framerate))
                wf_out.writeframes(frames)

            self.paused_time = 0
            self.start_time = time.time()
            self.need_reload = False

        if not self.is_playing:
            pygame.mixer.init()
            pygame.mixer.music.load(self.filename_to_play)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(0, self.paused_time)
            self.start_time = time.time()
            self.is_playing = True

    # stop music
    def stop(self, sender=None, app_data=None):
        if self.is_playing:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.paused_time = time.time() - self.start_time
            self.is_playing = False

    def louder(self, sedner=None, app_data=None):
        self.volume = min(self.volume + 0.1, 1.0)

    def quieter(self, sedner=None, app_data=None):
        self.volume = max(self.volume - 0.1, 0.0)

    def faster(self, sender=None, app_data=None):
        self.speed = min(self.speed + 0.1, 2.0)
        self.need_reload = True

    def slower(self, sender=None, app_data=None):
        self.speed = max(self.speed - 0.1, 0.1)
        self.need_reload = True

    def forward(self, sender=None, app_data=None):
        was_playing = False
        if self.is_playing:
            self.stop()
            was_playing = True

        self.paused_time = self.paused_time + 10

        if was_playing:
            self.play()  # Wznawiamy od nowej pozycji

    def backward(self, sender=None, app_data=None):
        was_playing = False
        if self.is_playing:
            was_playing = True
            self.stop()

        self.paused_time = self.paused_time - 10

        if was_playing:
            self.play()

    def info(self, sender=None, app_data=None):
        with wave.open(self.filename, 'rb') as wf:
            info_text = "Framerate: " + str(wf.getframerate()) + "\n" + "Time: " + str(
                round(wf.getnframes() / wf.getframerate(), 2))
            dpg.set_value("wave_info", info_text)

    def getFilename(self, sender=None, app_data=None):
        return self.filename

    def getTitle(self, sender=None, app_data=None):
        return self.Title

    def getAuthor(self, sender=None, app_data=None):
        return self.Author

    def getYear(self, sender=None, app_data=None):
        return self.Year

SongList = []
SongNumber = 0

#FILE IMPORT
def import_file(file_path, title, author, year):
    destination_folder = os.getcwd()
    try:
        shutil.copy(file_path, destination_folder)
        global current_wave_path
        current_wave_path = os.path.basename(file_path)
        # print(f"File {current_wave_path} was imported.")
        SongList.append(Song(current_wave_path, current_wave_path, author, year))
        update_song_list()
    except Exception as e:
        print(f"Failed to import file: {e}")

# FILE IMPORT - interraction with user
def import_file_interract(sender, app_data):
    from tkinter import filedialog, Tk
    Tk().withdraw()
    file_path = filedialog.askopenfilename(title="Choose file", filetypes=[("Wav files", "*.wav")])
    if file_path:
        import_file(file_path, "", "Unknown", "----")

def ChooseSong(k):
    global SongNumber
    SongNumber = k
    print(k)
    updateSongProperties()

def update_song_list():
    dpg.delete_item("SongListWindow", children_only=True)

    for i, song in enumerate(SongList):
        #print("check: " + str(i))
        dpg.add_button(
            label=song.filename,  # title
            callback=lambda a=i: ChooseSong(a-57 - len(SongList)),
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

#save files
def save():
    if os.path.exists("save.txt"):
        os.remove("save.txt")

    with open("save.txt", "w") as file:
        for Song in SongList:
            file.write(Song.getFilename() + "\n")
            file.write(Song.getTitle() + "\n")
            file.write(Song.getAuthor() + "\n")
            file.write(Song.getYear() + "\n")

# cut music
def cut_music(sender, app_data):
    cut_audio(current_wave_path, "bitwa_cut.wav", 10, 20)
    pygame.mixer.music.load("bitwa_cut.wav")
    pygame.mixer.music.play()

#update song properties
def updateSongProperties():
    print("hello")
    dpg.delete_item("SongProperties", children_only=True)

    dpg.add_text("SongProperties", parent="SongProperties")

    dpg.add_text("Title:", parent="SongProperties")
    dpg.add_input_text(default_value=SongList[SongNumber].Title, parent="SongProperties",
                       callback=lambda sender, app_data: setattr(SongList[SongNumber], "Title", app_data))

    dpg.add_text("Author:", parent="SongProperties")
    dpg.add_input_text(default_value=SongList[SongNumber].Author, parent="SongProperties",
                       callback=lambda sender, app_data: setattr(SongList[SongNumber], "Author", app_data))

    dpg.add_text("Year:", parent="SongProperties")
    dpg.add_input_text(default_value=SongList[SongNumber].Year, parent="SongProperties",
                       callback=lambda sender, app_data: setattr(SongList[SongNumber], "Year", app_data))

#exit program
def exit_program():
    dpg.stop_dearpygui()
    dpg.destroy_context()
    exit()

# Main window
if __name__ == "__main__":
    pygame.init()
    dpg.create_context()

    #read previous data
    with open("save.txt") as file:
        while True:
            lines = [file.readline().strip() for _ in range(4)]

            if not all(lines):
                break
            import_file(lines[0], lines[1], lines[2], lines[3])

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
        width, height, channels, data = dpg.load_image("forward.png")
        texture_forward = dpg.add_static_texture(width, height, data, tag="texture_forward")
        width, height, channels, data = dpg.load_image("backward.png")
        texture_backward = dpg.add_static_texture(width, height, data, tag="texture_backward")

    dpg.create_viewport(title="Music Program", width=1600, height=900, resizable=False, decorated=False)

    #Main Window
    with dpg.window(label="Main Window", width=1600, height=900, tag="MainWindow", no_move=True, no_resize=True):
        # Main section
        with dpg.group(horizontal=True):
            # Buttons
            with dpg.child(tag="ButtonGroup", width=50):
                dpg.add_image_button(callback=lambda: SongList[SongNumber].play(), width=20, height=20, texture_tag="texture_play")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].stop(), width=20, height=20, texture_tag="texture_stop")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].louder(), width=20, height=20, texture_tag="texture_louder")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].quieter(), width=20, height=20, texture_tag="texture_quieter")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].faster(), width=20, height=20, texture_tag="texture_faster")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].slower(), width=20, height=20, texture_tag="texture_slower")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].forward(), height=20, texture_tag="texture_forward")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].backward(), width=20, height=20, texture_tag="texture_backward")
                dpg.add_image_button(callback=lambda: SongList[SongNumber].info(), width=20, height=20, texture_tag="texture_info")
                dpg.add_image_button(callback=import_file_interract, width=20, height=20, texture_tag="texture_file")
                dpg.add_image_button(callback=save, width=20, height=20, texture_tag="texture_file")
                dpg.add_image_button(callback=lambda: exit_program(), width=20, height=20, texture_tag="texture_exit")
                # dpg.add_button(label="Cut Music (10-20s)", callback=cut_music)
            dpg.add_spacing()

            with dpg.child(tag="SongProperties", width=500):
                dpg.add_text("Song Properties")
                dpg.add_text("Nothing to show here")

            dpg.add_spacing()
            # Song list
            with dpg.child(tag="SongListWindow", width=250):
                dpg.add_text("Song List:", tag="songlist_title")
                dpg.add_text("No songs added yet.", tag="songlist_content")

        dpg.add_text("", tag="wave_info")

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()