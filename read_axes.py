import pygame
import sys
import time

pygame.init()
pygame.joystick.init()

count = pygame.joystick.get_count()
if count == 0:
    print("Aucun joystick detecte.")
    sys.exit(1)

# Auto-selection du 3dRudder
joy = None
for i in range(count):
    j = pygame.joystick.Joystick(i)
    j.init()
    print(f"  [{i}] {j.get_name()} — {j.get_numaxes()} axes")
    if "3drudder" in j.get_name().lower() or "3DRUDDER" in j.get_name():
        joy = j

if joy is None:
    print("\n3dRudder non trouve. Joystick 0 utilise par defaut.")
    joy = pygame.joystick.Joystick(0)
    joy.init()

n = joy.get_numaxes()
print(f"\nLecture de '{joy.get_name()}' ({n} axes) — Ctrl+C pour stopper\n")
header = "".join(f"  Axe{i:>2}" for i in range(n))
print(header)
print("-" * (7 * n))

try:
    while True:
        pygame.event.pump()
        axes = [joy.get_axis(i) for i in range(n)]
        row = "".join(f"{v:>7.3f}" for v in axes)
        print(f"\r{row}", end="", flush=True)
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nArret.")
finally:
    pygame.quit()
