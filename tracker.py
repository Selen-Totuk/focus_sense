import cv2
import mediapipe as mp

class Tracker:
    def __init__(self):
        # Yüz ve Vücut modellerini en yüksek hassasiyette başlatıyoruz
        self.face = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.pose = mp.solutions.pose.Pose()
        self.is_blinking = False
        self.smooth_gaze = [0.5, 0.5]

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_res = self.face.process(rgb)
        pose_res = self.pose.process(rgb)
        
        on_scr, blink, neck, pos = False, False, None, (0.5, 0.5)

        if face_res.multi_face_landmarks:
            lms = face_res.multi_face_landmarks[0].landmark
            gx = (lms[468].x + lms[473].x) / 2
            gy = (lms[468].y + lms[473].y) / 2
            pos = (gx, gy)
            
            # Bakış yumuşatma (Titremeyi engellemek için)
            self.smooth_gaze[0] = 0.2 * gx + 0.8 * self.smooth_gaze[0]
            self.smooth_gaze[1] = 0.2 * gy + 0.8 * self.smooth_gaze[1]
            
            # Odak merkezi kontrolü
            on_scr = (0.35 < self.smooth_gaze[0] < 0.65) and (0.30 < self.smooth_gaze[1] < 0.70)
            
            # EAR (Eye Aspect Ratio) ile Göz Kırpma Tespiti
            ear = (abs(lms[159].y - lms[145].y) + abs(lms[386].y - lms[374].y)) / 2
            if ear < 0.021:
                self.is_blinking = True
            elif self.is_blinking and ear > 0.025:
                blink, self.is_blinking = True, False

        if pose_res.pose_landmarks:
            p = pose_res.pose_landmarks.landmark
            # Burun-Omuz dikey mesafesi (Postür analizi için)
            neck = abs(p[0].y - p[11].y)

        return on_scr, blink, neck, pos