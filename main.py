import cv2
import tkinter as tk
from PIL import Image, ImageTk
from tracker import Tracker
from metrics import Metrics
import time

LANGS = {
    "TR": {"t1": "TOPLAM SÜRE", "t2": "EKRAN SÜRESİ", "t3": "DIŞARI SÜRESİ", "t4": "POSTÜR", "t5": "GÖZ KIRPMA", "t6": "ODAKLANMA %", "btn": "HARİTAYI AÇ", "ok": "DÜZGÜN", "bad": "BOZUK"},
    "EN": {"t1": "TOTAL TIME", "t2": "ON SCREEN", "t3": "OFF SCREEN", "t4": "POSTURE", "t5": "BLINKS", "t6": "FOCUS %", "btn": "OPEN MAP", "ok": "GOOD", "bad": "BAD"}
}

THEMES = {
    "dark": {"bg": "#020617", "panel": "#0F172A", "fg": "#38BDF8", "txt": "white"},
    "light": {"bg": "#F8FAFC", "panel": "#FFFFFF", "fg": "#0F172A", "txt": "#1E293B"}
}

class OdakAnalizElite:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OdakTakip")
        self.cur_lang, self.cur_theme = "TR", "dark"
        self.tracker, self.metrics = Tracker(), Metrics()
        self.cap = cv2.VideoCapture(0)
        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        T = THEMES[self.cur_theme]
        self.root.configure(bg=T["bg"])
        self.cam_lbl = tk.Label(self.root, bg="black")
        self.cam_lbl.pack(side="left", expand=True, padx=20, pady=20)
        self.panel = tk.Frame(self.root, bg=T["panel"], width=350)
        self.panel.pack(side="right", fill="y", padx=20, pady=20); self.panel.pack_propagate(False)

        self.labels = {}
        for key in ["t1", "t2", "t3", "t4", "t5", "t6"]:
            f = tk.Frame(self.panel, bg=T["panel"])
            f.pack(fill="x", padx=30, pady=8)
            t_lbl = tk.Label(f, text="", bg=T["panel"], fg="#64748B", font=("Arial", 8, "bold"))
            t_lbl.pack(anchor="w")
            v_lbl = tk.Label(f, text="--", bg=T["panel"], fg=T["txt"], font=("Arial", 16, "bold"))
            v_lbl.pack(anchor="w")
            self.labels[key] = (t_lbl, v_lbl)

        self.btn_map = tk.Button(self.panel, text="", command=self.show_map, bg="#38BDF8", fg="white", font=("Arial", 10, "bold"), pady=10)
        self.btn_map.pack(fill="x", padx=30, pady=20)
        
        ctrl = tk.Frame(self.panel, bg=T["panel"])
        ctrl.pack(side="bottom", pady=20)
        tk.Button(ctrl, text="TR/EN", command=self.toggle_lang).pack(side="left", padx=5)
        tk.Button(ctrl, text="☀/🌙", command=self.toggle_theme).pack(side="left", padx=5)
        self.refresh_ui_text()

    def refresh_ui_text(self):
        L = LANGS[self.cur_lang]
        self.btn_map.config(text=L["btn"])
        for key in ["t1", "t2", "t3", "t4", "t5", "t6"]: self.labels[key][0].config(text=L[key])

    def toggle_lang(self): self.cur_lang = "EN" if self.cur_lang == "TR" else "TR"; self.refresh_ui_text()
    def toggle_theme(self): 
        self.cur_theme = "light" if self.cur_theme == "dark" else "dark"
        for w in self.root.winfo_children(): w.destroy()
        self.setup_ui()

    def show_map(self):
        win = tk.Toplevel(self.root)
        canvas = tk.Canvas(win, width=800, height=600, bg="#020617"); canvas.pack()
        if len(self.metrics.gaze_history) > 2: canvas.create_line(self.metrics.gaze_history, fill="#38BDF8", smooth=True)

    def update_loop(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            on_scr, blink, neck, pos = self.tracker.process(frame)
            self.metrics.update(on_scr, pos, neck)
            if blink: self.metrics.blink_count += 1

            L, M = LANGS[self.cur_lang], self.metrics
            def fmt(s): return f"{int(s//60):02d}:{int(s%60):02d}"
            self.labels["t1"][1].config(text=fmt(time.time() - M.start_time))
            self.labels["t2"][1].config(text=fmt(M.on_screen_time))
            self.labels["t3"][1].config(text=fmt(M.off_screen_time))
            self.labels["t4"][1].config(text=L["bad"] if M.is_bad_posture else L["ok"], fg="#F43F5E" if M.is_bad_posture else "#10B981")
            self.labels["t5"][1].config(text=str(M.blink_count))
            self.labels["t6"][1].config(text=f"%{M.focus_percentage}")

            if M.is_bad_posture: cv2.rectangle(frame, (0,0), (frame.shape[1], frame.shape[0]), (0,0,255), 15)
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((800, 600)))
            self.cam_lbl.imgtk = img; self.cam_lbl.config(image=img)
        self.root.after(10, self.update_loop)

if __name__ == "__main__":
    OdakAnalizElite().root.mainloop()