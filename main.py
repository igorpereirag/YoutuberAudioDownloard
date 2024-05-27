import os
import json
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from threading import Thread

def save_config(destination_folder):
    with open('config.json', 'w') as config_file:
        json.dump({'destination_folder': destination_folder}, config_file)

def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            return config.get('destination_folder', '')
    return ''

def update_progress(percent, progress_var, progress_bar):
    progress_var.set(percent)
    progress_bar.update()

def download_audio(url, destination_folder, progress_var, progress_bar, status_label):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(destination_folder, '%(title)s.mp3'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': 'bin',
        'progress_hooks': [lambda d: progress_hook(d, progress_var, progress_bar, status_label)]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Download completo", "O áudio foi baixado com sucesso.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

def progress_hook(d, progress_var, progress_bar, status_label):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percent = int(downloaded_bytes / total_bytes * 100) if total_bytes > 0 else 0
        speed = d.get('speed', 0) or 0
        size_in_mib = total_bytes / 1024 / 1024 if total_bytes > 0 else 0
        speed_in_kib = speed / 1024 if speed > 0 else 0
        update_progress(percent, progress_var, progress_bar)
        status_label.config(text=f"Baixando: {percent}% - Velocidade: {speed_in_kib:.2f} KiB/s - Tamanho: {size_in_mib:.2f} MiB")
    elif d['status'] == 'finished':
        update_progress(100, progress_var, progress_bar)
        status_label.config(text="Conversão para MP3 concluída")

def start_download():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Aviso", "Por favor, insira o link do vídeo.")
        return

    destination_folder = destination_folder_var.get()
    if not destination_folder:
        messagebox.showwarning("Aviso", "Por favor, escolha a pasta de destino.")
        return

    save_config(destination_folder)

    download_thread = Thread(target=download_audio, args=(url, destination_folder, progress_var, progress_bar, status_label))
    download_thread.start()

def select_destination_folder():
    folder = filedialog.askdirectory()
    if folder:
        destination_folder_var.set(folder)

root = tk.Tk()
root.title("YouTube Audio Downloader")
root.geometry("500x320")
root.configure(bg="#333333")  # Cor de fundo em modo dark

frame = tk.Frame(root, bg="#333333")  # Cor de fundo do frame em modo dark
frame.pack(expand=True)

tk.Label(frame, text="Link do Vídeo:", bg="#333333", fg="white").pack(pady=5)
url_entry = tk.Entry(frame, width=60)
url_entry.pack(pady=5)

tk.Label(frame, text="Pasta de Destino:", bg="#333333", fg="white").pack(pady=5)
destination_folder_var = tk.StringVar()
destination_folder_var.set(load_config())

destination_frame = tk.Frame(frame, bg="#333333")  # Cor de fundo do frame de destino em modo dark
destination_frame.pack(pady=5)
tk.Entry(destination_frame, textvariable=destination_folder_var, width=50).pack(side=tk.LEFT, padx=5)
tk.Button(destination_frame, text="Selecionar", command=select_destination_folder, bg="#006600", fg="white", bd=2).pack(side=tk.LEFT, padx=5)  # Botão com borda verde

tk.Label(frame, text="Progresso:", bg="#333333", fg="white").pack(pady=5)
progress_var = tk.IntVar()
progress_bar = Progressbar(frame, orient=tk.HORIZONTAL, length=400, mode='determinate', maximum=100, variable=progress_var)
progress_bar.pack(pady=5)

status_label = tk.Label(frame, text="Aguardando...", bg="#333333", fg="white")  # Cor do texto em modo dark
status_label.pack(pady=5)

tk.Button(frame, text="Baixar Áudio (MP3)", bg="#006600", fg="white", command=start_download).pack(pady=20)

footer_label = tk.Label(root, text="Desenvolvido por Igor Pereira | GitHub:@igorpereirag", bg="#333333", fg="white")
footer_label.pack(side=tk.BOTTOM)


root.mainloop()
