# main.py
import cv2
import tkinter as tk
from PIL import Image, ImageTk
from tracker import Tracker
from metrics import Metrics

cap = cv2.VideoCapture(0)
tracker = Tracker()
metrics = Metrics()

root = tk.Tk()
root.title("FocusSense – Akıllı Ders Asistanı")
root.geometry("1200x700")
root.configure(bg="#020617")

cam_lbl = tk.Label(root)
cam_lbl.pack(side="left", expand=True, padx=20)

panel = tk.Frame(root, bg="#0F172A", width=300)
panel.pack(side="right", fill="y")

lbl_time = tk.Label(panel, fg="white", bg="#0F172A", font=("Arial", 14))
lbl_focus = tk.Label(panel, fg="#10B981", bg="#0F172A", font=("Arial", 28, "bold"))
lbl_posture = tk.Label(panel, bg="#0F172A", font=("Arial", 14))
lbl_break = tk.Label(panel, fg="#F43F5E", bg="#0F172A", font=("Arial", 12, "bold"))

for l in [lbl_time, lbl_focus, lbl_posture, lbl_break]:
    l.pack(pady=15)

def loop():
    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)

    on_screen, blink, neck = tracker.process(frame)
    metrics.update(on_screen, blink, neck)

    lbl_time.config(text=f"Süre: {metrics.get_time()}")
    lbl_focus.config(text=f"FocusScore: {metrics.focus_score}")
    lbl_posture.config(
        text="Postür: BOZUK" if metrics.bad_posture else "Postür: DÜZGÜN",
        fg="#F43F5E" if metrics.bad_posture else "#10B981"
    )
    lbl_break.config(
        text="⚠ Kısa mola önerilir" if metrics.break_suggested else ""
    )

    img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
    cam_lbl.imgtk = img
    cam_lbl.config(image=img)

    root.after(10, loop)

loop()
root.mainloop()
cap.release()
