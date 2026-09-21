from __future__ import annotations

import queue
import sys
import threading

import numpy as np
import pygame
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_LINES,
    GL_MODELVIEW,
    GL_PROJECTION,
    glBegin,
    glClear,
    glColor3f,
    glEnable,
    glEnd,
    glLoadIdentity,
    glMatrixMode,
    glMultMatrixf,
    glTranslatef,
    glVertex3fv,
)
from OpenGL.GLU import gluPerspective
from pygame.locals import DOUBLEBUF, OPENGL

from echoglove.imu_reader import quaternion_stream

# Unit cube: 8 vertices centered at origin
_VERTICES = np.array(
    [
        [-1, -1, -1], [ 1, -1, -1], [ 1,  1, -1], [-1,  1, -1],
        [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1],
    ],
    dtype=np.float32,
)

# 12 edges grouped by the axis they run along, so each direction is a
# different color and the cube's orientation is readable at a glance.
_EDGES_BY_AXIS = {
    "x": [(0, 1), (2, 3), (4, 5), (6, 7)],
    "y": [(1, 2), (3, 0), (5, 6), (7, 4)],
    "z": [(0, 4), (1, 5), (2, 6), (3, 7)],
}

_AXIS_COLORS = {
    "x": (1.0, 0.35, 0.35),  # red
    "y": (0.35, 1.0, 0.45),  # green
    "z": (0.45, 0.6, 1.0),   # blue
}

# Body axes drawn from the center outward — these stick out past the cube face
# and mark which end of each axis is positive.
_ORIGIN = np.array([0, 0, 0], dtype=np.float32)
_AXIS_TIPS = {
    "x": np.array([1.7, 0, 0], dtype=np.float32),
    "y": np.array([0, 1.7, 0], dtype=np.float32),
    "z": np.array([0, 0, 1.7], dtype=np.float32),
}


def _quat_to_matrix(w: float, x: float, y: float, z: float) -> np.ndarray:
    """Convert unit quaternion to 3x3 rotation matrix."""
    return np.array(
        [
            [1 - 2*(y*y + z*z),   2*(x*y - z*w),     2*(x*z + y*w)],
            [    2*(x*y + z*w), 1 - 2*(x*x + z*z),     2*(y*z - x*w)],
            [    2*(x*z - y*w),     2*(y*z + x*w), 1 - 2*(x*x + y*y)],
        ],
        dtype=np.float32,
    )


class _SerialReaderThread(threading.Thread):
    def __init__(self, port: str, baud: int, q: queue.Queue) -> None:
        super().__init__(daemon=True)
        self._port = port
        self._baud = baud
        self._q = q
        self._stop = threading.Event()

    def run(self) -> None:
        try:
            for quat in quaternion_stream(self._port, self._baud):
                if self._stop.is_set():
                    break
                if self._q.full():
                    try:
                        self._q.get_nowait()
                    except queue.Empty:
                        pass
                self._q.put(quat)
        except Exception:
            pass

    def stop(self) -> None:
        self._stop.set()


def run_viewer(port: str, baud: int = 115200) -> None:
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("EchoGlove — IMU Viewer")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 800 / 600, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    q: queue.Queue = queue.Queue(maxsize=10)
    reader = _SerialReaderThread(port, baud, q)
    reader.start()

    current_quat = (1.0, 0.0, 0.0, 0.0)
    clock = pygame.time.Clock()

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Drain queue — keep only the latest quaternion
            while not q.empty():
                try:
                    current_quat = q.get_nowait()
                except queue.Empty:
                    break

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            glTranslatef(0.0, 0.0, -5.0)

            w, x, y, z = current_quat
            rot = _quat_to_matrix(w, x, y, z)
            m = np.eye(4, dtype=np.float32)
            m[:3, :3] = rot
            glMultMatrixf(m.T)  # OpenGL expects column-major

            glBegin(GL_LINES)
            for axis, edges in _EDGES_BY_AXIS.items():
                glColor3f(*_AXIS_COLORS[axis])
                for i, j in edges:
                    glVertex3fv(_VERTICES[i])
                    glVertex3fv(_VERTICES[j])
            for axis, tip in _AXIS_TIPS.items():
                glColor3f(*_AXIS_COLORS[axis])
                glVertex3fv(_ORIGIN)
                glVertex3fv(tip)
            glEnd()

            pygame.display.flip()
            clock.tick(60)
    finally:
        reader.stop()
        pygame.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python -m echoglove.viewer /dev/tty.usbmodemXXXX")
        raise SystemExit(2)
    run_viewer(sys.argv[1])
