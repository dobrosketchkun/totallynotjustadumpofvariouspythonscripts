#!/usr/bin/env python3
# pyqt_ffmpeg_cropper.py

import sys, os, random, shlex
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import numpy as np

# ---------- Helpers: image conversion ----------
def cv2_to_qpixmap(frame_bgr):
    h, w, ch = frame_bgr.shape
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    qimg = QtGui.QImage(frame_rgb.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
    return QtGui.QPixmap.fromImage(qimg)

# ---------- Resizable & Draggable Rect ----------
class ResizableRectItem(QtWidgets.QGraphicsRectItem):
    # Regions for resize handles (corners + edges)
    NONE, MOVE, TL, TR, BL, BR, L, R, T, B = range(10)

    def __init__(self, rect, bounds_rect, parent=None):
        super().__init__(rect, parent)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, True)
        self._bounds = QtCore.QRectF(bounds_rect)
        self._drag_region = self.NONE
        self._drag_start_pos = None
        self._start_rect = QtCore.QRectF()
        self.handle = 10.0  # px range around corners/edges
        self.min_size = 8.0

        pen = QtGui.QPen(QtGui.QColor(0, 220, 0), 2)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setBrush(QtGui.QColor(0, 255, 0, 40))

    def set_bounds(self, bounds_rect: QtCore.QRectF):
        """Update clamp bounds (e.g., when the underlying pixmap changes)."""
        self._bounds = QtCore.QRectF(bounds_rect)
        # Make sure current rect is still valid
        r = self._clamp_rect(self.rect())
        # Ensure min size
        if r.width() < self.min_size or r.height() < self.min_size:
            r = QtCore.QRectF(
                max(self._bounds.left(), r.left()),
                max(self._bounds.top(), r.top()),
                max(self.min_size, r.width()),
                max(self.min_size, r.height())
            )
        self.setRect(r.normalized())

    def hoverMoveEvent(self, event):
        region = self._region_at(event.pos())
        cursor = QtCore.Qt.ArrowCursor
        if region in (self.TL, self.BR):
            cursor = QtCore.Qt.SizeFDiagCursor
        elif region in (self.TR, self.BL):
            cursor = QtCore.Qt.SizeBDiagCursor
        elif region in (self.L, self.R):
            cursor = QtCore.Qt.SizeHorCursor
        elif region in (self.T, self.B):
            cursor = QtCore.Qt.SizeVerCursor
        elif region == self.MOVE:
            cursor = QtCore.Qt.SizeAllCursor
        self.setCursor(cursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_region = self._region_at(event.pos())
            self._drag_start_pos = event.scenePos()
            self._start_rect = QtCore.QRectF(self.rect())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_region == self.NONE:
            super().mouseMoveEvent(event)
            return

        delta = event.scenePos() - self._drag_start_pos
        r = QtCore.QRectF(self._start_rect)

        if self._drag_region == self.MOVE:
            r.translate(delta)
            r = self._clamp_rect(r)
        else:
            # Resize around edges/corners
            if self._drag_region in (self.TL, self.L, self.BL):
                new_left = r.left() + delta.x()
                new_left = max(self._bounds.left(), min(new_left, r.right() - self.min_size))
                r.setLeft(new_left)
            if self._drag_region in (self.TR, self.R, self.BR):
                new_right = r.right() + delta.x()
                new_right = min(self._bounds.right(), max(new_right, r.left() + self.min_size))
                r.setRight(new_right)
            if self._drag_region in (self.TL, self.T, self.TR):
                new_top = r.top() + delta.y()
                new_top = max(self._bounds.top(), min(new_top, r.bottom() - self.min_size))
                r.setTop(new_top)
            if self._drag_region in (self.BL, self.B, self.BR):
                new_bottom = r.bottom() + delta.y()
                new_bottom = min(self._bounds.bottom(), max(new_bottom, r.top() + self.min_size))
                r.setBottom(new_bottom)

        self.setRect(r.normalized())
        self.update()

    def mouseReleaseEvent(self, event):
        self._drag_region = self.NONE
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)

    def _clamp_rect(self, r):
        # Ensure rect stays inside bounds
        dx = 0.0
        dy = 0.0
        if r.left() < self._bounds.left():
            dx = self._bounds.left() - r.left()
        if r.right() > self._bounds.right():
            dx = self._bounds.right() - r.right()
        if r.top() < self._bounds.top():
            dy = self._bounds.top() - r.top()
        if r.bottom() > self._bounds.bottom():
            dy = self._bounds.bottom() - r.bottom()
        r = QtCore.QRectF(r)  # copy
        r.translate(dx, dy)
        return r

    def _region_at(self, p):
        r = self.rect()
        x, y = p.x(), p.y()
        left, right, top, bottom = r.left(), r.right(), r.top(), r.bottom()
        h = self.handle

        # Corner zones
        if abs(x - left) <= h and abs(y - top) <= h:
            return self.TL
        if abs(x - right) <= h and abs(y - top) <= h:
            return self.TR
        if abs(x - left) <= h and abs(y - bottom) <= h:
            return self.BL
        if abs(x - right) <= h and abs(y - bottom) <= h:
            return self.BR

        # Edge zones
        if abs(x - left) <= h and top + h < y < bottom - h:
            return self.L
        if abs(x - right) <= h and top + h < y < bottom - h:
            return self.R
        if abs(y - top) <= h and left + h < x < right - h:
            return self.T
        if abs(y - bottom) <= h and left + h < x < right - h:
            return self.B

        # Inside
        if r.contains(p):
            return self.MOVE
        return self.NONE

# ---------- Main Window ----------
class CropperWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt FFmpeg Crop Command Builder")
        self.resize(1200, 800)
        self.video_path = None
        self.frame = None
        self.frame_index = None

        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setCentralWidget(self.view)

        self.pixmap_item = None
        self.rect_item = None

        # ffmpeg process (non-blocking)
        self.ffmpeg_proc = None

        # Toolbar
        tb = self.addToolBar("Main")
        open_act = QtWidgets.QAction("Open Video…", self)
        open_act.triggered.connect(self.open_video)
        tb.addAction(open_act)

        rand_act = QtWidgets.QAction("Random Frame", self)
        rand_act.triggered.connect(self.pick_random_frame)
        tb.addAction(rand_act)

        confirm_act = QtWidgets.QAction("Crop with FFmpeg", self)
        confirm_act.triggered.connect(self.confirm_crop)
        tb.addAction(confirm_act)

        self.status = self.statusBar()
        self.status.showMessage("Open a video to start")

    # --------- Video handling ---------
    def open_video(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open video", "", "Videos (*.mp4 *.mov *.mkv *.avi *.m4v *.webm);;All files (*)")
        if not path:
            return
        self.video_path = path
        self.status.showMessage(f"Opened: {os.path.basename(path)} — Click 'Random Frame'")
        # Reset selection for a NEW video only
        self.rect_item = None
        self.pixmap_item = None
        self.scene.clear()
        self.pick_random_frame()

    def pick_random_frame(self):
        if not self.video_path:
            QtWidgets.QMessageBox.information(self, "No video", "Open a video first.")
            return
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to open video.")
            return

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        idx = random.randint(0, max(0, total - 1))

        # Try fast seek; if it fails, fallback to sequential read
        ok = cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            for _ in range(idx + 1):
                ret, frame = cap.read()
                if not ret:
                    break

        cap.release()
        if not ret:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to read a frame from the video.")
            return

        self.frame_index = idx
        self.frame = frame
        self.show_frame(frame)

    def show_frame(self, frame_bgr):
        pix = cv2_to_qpixmap(frame_bgr)

        # If we already have items, just update the pixmap and bounds, KEEPING the selection
        if self.pixmap_item is not None and self.rect_item is not None:
            self.pixmap_item.setPixmap(pix)
            img_rect = self.pixmap_item.boundingRect()  # scene coords = pixel coords
            self.rect_item.set_bounds(img_rect)
        else:
            # First-time setup (or after opening a new video)
            self.scene.clear()
            self.pixmap_item = self.scene.addPixmap(pix)
            self.pixmap_item.setZValue(0)

            img_rect = self.pixmap_item.boundingRect()  # scene coords = pixel coords
            # Default crop: centered, ~50% of width/height
            w, h = img_rect.width(), img_rect.height()
            default_rect = QtCore.QRectF(w * 0.25, h * 0.25, w * 0.5, h * 0.5)

            self.rect_item = ResizableRectItem(default_rect, img_rect)
            self.scene.addItem(self.rect_item)

        self.view.fitInView(self.pixmap_item, QtCore.Qt.KeepAspectRatio)
        self.status.showMessage(f"Frame {self.frame_index} — drag edges/corners to resize; drag inside to move.")

    # --------- Confirm crop: run ffmpeg asynchronously ----------
    def confirm_crop(self):
        if self.rect_item is None or self.pixmap_item is None or self.frame is None or not self.video_path:
            QtWidgets.QMessageBox.information(self, "Nothing to crop", "Open a video and pick a frame first.")
            return

        # Prevent overlapping runs
        if self.ffmpeg_proc is not None:
            QtWidgets.QMessageBox.information(self, "Busy", "An FFmpeg job is already running.")
            return

        r = self.rect_item.rect().normalized()
        # Ensure within image bounds
        img_rect = self.pixmap_item.boundingRect()
        r = r.intersected(img_rect)

        # Convert to ints and favor even numbers (safer for common codecs)
        def even(n):
            return int(max(2, n)) // 2 * 2

        x = max(0, int(r.left()))
        y = max(0, int(r.top()))
        w = even(int(r.width()))
        h = even(int(r.height()))

        # Clamp so x+w <= width, y+h <= height
        img_w = int(img_rect.width())
        img_h = int(img_rect.height())
        if x + w > img_w:
            w = even(img_w - x)
        if y + h > img_h:
            h = even(img_h - y)

        in_path = self.video_path
        root, ext = os.path.splitext(in_path)
        out_path = f"{root}_cropped{ext or '.mp4'}"

        # Build args list for QProcess (avoid shell quoting issues)
        args = [
            "-y",  # overwrite without asking
            "-i", in_path,
            "-filter:v", f"crop={w}:{h}:{x}:{y}",
            "-c:a", "copy",
            out_path,
        ]

        # Optional: show the full command in console as well
        printable_cmd = "ffmpeg " + " ".join(shlex.quote(a) for a in args)
        print(printable_cmd)

        # Launch non-blocking
        self.ffmpeg_proc = QtCore.QProcess(self)
        self.ffmpeg_proc.setProgram("ffmpeg")
        self.ffmpeg_proc.setArguments(args)
        # Capture stderr for progress text (ffmpeg writes progress to stderr)
        self.ffmpeg_proc.readyReadStandardError.connect(self._on_ffmpeg_stderr)
        self.ffmpeg_proc.readyReadStandardOutput.connect(self._on_ffmpeg_stdout)
        self.ffmpeg_proc.finished.connect(lambda code, status: self._on_ffmpeg_finished(code, status, out_path))
        self.ffmpeg_proc.errorOccurred.connect(self._on_ffmpeg_error)

        self.status.showMessage("Running FFmpeg…")
        self.ffmpeg_proc.start()

        if not self.ffmpeg_proc.waitForStarted(3000):
            self.status.showMessage("Failed to start FFmpeg")
            QtWidgets.QMessageBox.critical(self, "FFmpeg", "Failed to start FFmpeg. Is it installed and on PATH?")
            self.ffmpeg_proc = None
            return

        # Non-blocking: return to the event loop immediately.

    # ---- ffmpeg QProcess handlers ----
    def _on_ffmpeg_stdout(self):
        # ffmpeg usually writes progress to stderr; stdout is often empty
        pass

    def _on_ffmpeg_stderr(self):
        data = bytes(self.ffmpeg_proc.readAllStandardError()).decode(errors="ignore")
        # You can parse progress here if you want; for now just echo the last line to the status bar
        last_line = [line for line in data.splitlines() if line.strip()]
        if last_line:
            self.status.showMessage(last_line[-1][:160])

    def _on_ffmpeg_finished(self, exit_code, exit_status, out_path):
        ok = (exit_status == QtCore.QProcess.NormalExit and exit_code == 0)
        self.ffmpeg_proc = None
        if ok:
            self.status.showMessage(f"FFmpeg finished → {os.path.basename(out_path)}")
            QtWidgets.QMessageBox.information(self, "FFmpeg", f"Done!\n\nOutput:\n{out_path}")
        else:
            self.status.showMessage("FFmpeg failed")
            QtWidgets.QMessageBox.critical(self, "FFmpeg", "FFmpeg failed. Check console for details.")

    def _on_ffmpeg_error(self, err):
        self.status.showMessage(f"FFmpeg error: {err}")
        QtWidgets.QMessageBox.critical(self, "FFmpeg", f"Error running FFmpeg: {err}")
        self.ffmpeg_proc = None

def main():
    app = QtWidgets.QApplication(sys.argv)
    # High-DPI friendliness
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    w = CropperWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
