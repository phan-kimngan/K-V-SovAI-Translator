import pyaudio
import wave
import threading
import tkinter as tk
from tkinter import messagebox

class AudioRecorder:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.frames = []
        self.recording = False
        self.p = pyaudio.PyAudio()
        self.stream = None

    def start_recording(self):
        if self.recording:
            return
        self.frames = []
        self.recording = True
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)
        threading.Thread(target=self._record).start()

    def _record(self):
        while self.recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except OSError as e:
                print(f"Stream read error: {e}")

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None

    def save_recording(self, filename="output.wav"):
        if not self.frames:
            messagebox.showerror("Error", "No audio recorded.")
            return
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        #messagebox.showinfo("Saved", f"Audio saved as {filename}")

    def terminate(self):
        self.p.terminate()


# GUI Setup
recorder = AudioRecorder()

def on_start():
    recorder.start_recording()
    status_label.config(text="Recording...")

def on_stop():
    recorder.stop_recording()
    recorder.save_recording("recorded_audio.wav")  # Automatically save on stop
    status_label.config(text="Recording stopped and saved.")

def on_save():
    recorder.save_recording("recorded_audio.wav")

def on_close():
    recorder.stop_recording()
    recorder.terminate()
    root.destroy()

root = tk.Tk()
root.title("Realtime Audio Recorder")

tk.Button(root, text="Start Recording", command=on_start, width=30).pack(pady=10)
tk.Button(root, text="Stop Recording", command=on_stop, width=30).pack(pady=10)
#tk.Button(root, text="Save to File", command=on_save, width=50).pack(pady=10)
status_label = tk.Label(root, text="")
status_label.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
def uploading_file():
    with open("recorded_audio.wav", "rb") as f:
        uploaded_file = f.read()
    return uploaded_file
