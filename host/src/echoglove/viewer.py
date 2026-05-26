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
    glBegin,
    glClear,
    glColor3f,
    glEnable,
    glEnd,
    glLoadIdentity,
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

# 12 edges connecting the 8 vertices
_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # back face
    (4, 5), (5, 6), (6, 7), (7, 4),  # front face
    (0, 4), (1, 5), (2, 6), (3, 7),  # connecting edges
]


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

    gluPerspective(45, 800 / 600, 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5.0)
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

            rotated = _VERTICES @ rot.T

            glBegin(GL_LINES)
            glColor3f(0.0, 1.0, 0.0)
            for i, j in _EDGES:
                glVertex3fv(rotated[i])
                glVertex3fv(rotated[j])
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
