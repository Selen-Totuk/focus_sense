import time

class Metrics:
    def __init__(self):
        self.start_time = time.time()
        self.on_screen_time = 0
        self.off_screen_time = 0
        self.blink_count = 0
        self.last_update = time.time()
        self.gaze_history = []
        self.ref_neck_dist = None
        self.calib_frames = []
        self.is_bad_posture = False
        self.focus_percentage = 100

    def update(self, is_on_screen, pos, neck_val):
        now = time.time()
        delta = now - self.last_update
        self.last_update = now

        if is_on_screen:
            self.on_screen_time += delta
            # Bakış Haritası Kaydı
            self.gaze_history.append((pos[0] * 800, pos[1] * 600))
            if len(self.gaze_history) > 1000: self.gaze_history.pop(0)
        else:
            self.off_screen_time += delta

        # Postür Kalibrasyonu ve Kontrolü
        if neck_val:
            if self.ref_neck_dist is None:
                self.calib_frames.append(neck_val)
                if len(self.calib_frames) > 50:
                    self.ref_neck_dist = sum(self.calib_frames) / len(self.calib_frames)
            else:
                self.is_bad_posture = neck_val > (self.ref_neck_dist * 1.25)
        
        # --- ODAKLANMA YÜZDESİ HESAPLAMA ---
        total = self.on_screen_time + self.off_screen_time
        if total > 0:
            # Temel Puan: Ekrana bakma oranı
            score = (self.on_screen_time / total) * 100
            # Ceza: Postür bozukluğu (-15 puan)
            if self.is_bad_posture: score -= 15
            # Ceza: Aşırı göz kırpma (Yorgunluk belirtisi)
            elapsed_min = (time.time() - self.start_time) / 60
            if elapsed_min > 0:
                bpm = self.blink_count / elapsed_min
                if bpm > 25: score -= 10
            
            self.focus_percentage = max(0, min(100, int(score)))