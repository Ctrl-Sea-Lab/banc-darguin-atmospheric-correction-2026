#!/usr/bin/env python3
"""Generate an illustrative marine habitat trend at an explicitly staged path."""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path


WIDTH = 960
HEIGHT = 576
WHITE = (255, 255, 255)
INK = (35, 52, 58)
GRID = (218, 226, 226)
TEAL = (0, 109, 119)


def set_pixel(image: bytearray, x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        offset = (y * WIDTH + x) * 3
        image[offset : offset + 3] = bytes(color)


def line(
    image: bytearray,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    thickness: int = 1,
) -> None:
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    error = dx + dy
    while True:
        for offset_x in range(-(thickness // 2), thickness // 2 + 1):
            for offset_y in range(-(thickness // 2), thickness // 2 + 1):
                set_pixel(image, x0 + offset_x, y0 + offset_y, color)
        if x0 == x1 and y0 == y1:
            return
        doubled = 2 * error
        if doubled >= dy:
            error += dy
            x0 += sx
        if doubled <= dx:
            error += dx
            y0 += sy


def circle(
    image: bytearray, center: tuple[int, int], radius: int, color: tuple[int, int, int]
) -> None:
    center_x, center_y = center
    for y in range(center_y - radius, center_y + radius + 1):
        for x in range(center_x - radius, center_x + radius + 1):
            if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2:
                set_pixel(image, x, y, color)


def png_chunk(name: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(name + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + name + payload + struct.pack(">I", checksum)


def write_png(output: Path) -> None:
    image = bytearray(WHITE * (WIDTH * HEIGHT))
    left, right, top, bottom = 110, 900, 65, 500
    for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = round(bottom - fraction * (bottom - top))
        line(image, (left, y), (right, y), GRID)
    line(image, (left, top), (left, bottom), INK, 3)
    line(image, (left, bottom), (right, bottom), INK, 3)

    cover = [42, 45, 47, 46, 51, 55, 58]
    low, high = 35, 65
    points = []
    for index, value in enumerate(cover):
        x = round(left + index * (right - left) / (len(cover) - 1))
        y = round(bottom - (value - low) * (bottom - top) / (high - low))
        points.append((x, y))
    for start, end in zip(points, points[1:]):
        line(image, start, end, TEAL, 5)
    for point in points:
        circle(image, point, 8, TEAL)

    scanlines = b"".join(
        b"\x00" + bytes(image[row * WIDTH * 3 : (row + 1) * WIDTH * 3])
        for row in range(HEIGHT)
    )
    header = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    output.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(scanlines, level=9))
        + png_chunk(b"IEND", b"")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    write_png(arguments.output)
    print(arguments.output)


if __name__ == "__main__":
    main()
