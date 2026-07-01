import threading
import pygame

from evdev import *

# wrapper class to convert touch input events using evdev (linux only lib) to pygame mouse inputs
class TouchWrapper:

    def __init__(self, device_path, screen_w, screen_h,
                 x_min, x_max, y_min, y_max,
                 swap_xy=False, invert_x=False, invert_y=False):
        
        # Raw device node, e.g. /dev/input/event0 - see TOUCH_DEVICE.
        self.device   = InputDevice(device_path)
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Raw ADC range the touch controller reports (e.g. 0-4095)
        # Found via evtest corner-tap calibration, portrait mode only for testing
        self.x_min, self.x_max = x_min, x_max
        self.y_min, self.y_max = y_min, y_max

        # Axis-correction flags, also derived from the evtest corner test,
        # in case this panel's raw X/Y don't line up with screen X/Y.
        self.swap_xy  = swap_xy
        self.invert_x = invert_x
        self.invert_y = invert_y

        # Latest known raw touch position.
        self._raw_x = 0
        self._raw_y = 0

        # init touch state
        self._touching = False

        # Runs in the background so it doesn't block pygame's main loop -
        # device.read_loop() blocks on a read() syscall per event.
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def _scale(self, raw, raw_min, raw_max, out_max):
        # Linearly maps a raw ADC reading onto a 0..out_max-1 pixel coord.
        span = raw_max - raw_min
        if span <= 0:
            return 0
        
        pct = (raw - raw_min) / span
        return max(0, min(out_max - 1, int(pct * out_max)))

    def _to_screen_pos(self):
        # Converts the latest raw touch reading into a screen pixel (x, y),
        # applying whatever axis correction this panel/orientation needs.
        x = self._scale(self._raw_x, self.x_min, self.x_max, self.screen_w)
        y = self._scale(self._raw_y, self.y_min, self.y_max, self.screen_h)

        if self.swap_xy:
            x, y = y, x

        if self.invert_x:
            x = self.screen_w - 1 - x

        if self.invert_y:
            y = self.screen_h - 1 - y

        return x, y

    def _run(self):
        # BTN_TOUCH can arrive before its matching ABS_X/ABS_Y within the
        # same touch-down report, so resolving position immediately on
        # BTN_TOUCH would use the *previous* touch's coordinates. Instead,
        # just flag what happened and wait for SYN_REPORT (end of this
        # batch of updates) before reading position and posting the event.
        down_pending = False
        up_pending = False

        # for each event in produced kernel events in a row (X update,
        # Y update, pressure update)
        for event in self.device.read_loop():
            if event.type == ecodes.EV_ABS:
                # X and Y arrive as separate events
                if event.code == ecodes.ABS_X:
                    self._raw_x = event.value

                elif event.code == ecodes.ABS_Y:
                    self._raw_y = event.value

            elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
                # value 1 = finger down, 0 = finger lifted.
                # Fire once per press/release to simulate real mouse click
                if event.value == 1 and not self._touching:
                    self._touching = True
                    down_pending = True

                elif event.value == 0 and self._touching:
                    self._touching = False
                    up_pending = True

            elif event.type == ecodes.EV_SYN and event.code == ecodes.SYN_REPORT:
                # batch complete - safe to read the final x/y for this event
                if down_pending:
                    pygame.event.post(pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN, pos=self._to_screen_pos(), button=1))
                    down_pending = False

                if up_pending:
                    pygame.event.post(pygame.event.Event(
                        pygame.MOUSEBUTTONUP, pos=self._to_screen_pos(), button=1))
                    up_pending = False
