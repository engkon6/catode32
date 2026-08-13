"""
input.py - Button input handling with support for analog joystick and resistor ladder buttons.
"""

from machine import Pin, ADC
import time
import config

class InputHandler:
    """Handles button inputs with debouncing and state tracking, now supporting analog inputs."""
    
    def __init__(self):
        self.adc = {
            'joy_x': ADC(Pin(config._ESP32_C3_CONFIG['JOY_X'])),
            'joy_y': ADC(Pin(config._ESP32_C3_CONFIG['JOY_Y'])),
            'btn_ladder': ADC(Pin(config._ESP32_C3_CONFIG['BTN_LADDER']))
        }
        
        # Joystick configuration
        self.joy_x_min = 500
        self.joy_x_max = 3500
        self.joy_y_min = 500
        self.joy_y_max = 3500
        self.joy_center = 2000
        self.joy_threshold = 1000
        
        # Button ranges
        self.button_ranges = {
            'a': (890, 920),      # K1
            'b': (1810, 1850),    # K2
            'menu1': (2760, 2800) # K3
        }
        
        # Digital buttons (if any, though not used in your setup)
        self.buttons = {}
        
        # Track button states for debouncing
        self.button_states = {}
        self.last_press_time = {}
        self.debounce_time_ms = 150 # Increased for analog stability
        
        # All virtual button names the game expects
        self.all_btns = ['up', 'down', 'left', 'right', 'a', 'b', 'menu1', 'menu2']
        
        # Initialize state tracking
        for btn_name in self.all_btns:
            self.button_states[btn_name] = False
            self.last_press_time[btn_name] = 0
            
    def _read_adc(self, adc):
        # 12-bit ADC (0-4095)
        return adc.read_u16() >> 4

    def is_pressed(self, button_name):
        """Check if a button is currently pressed (raw state)"""
        if button_name in ['up', 'down', 'left', 'right']:
            x = self._read_adc(self.adc['joy_x'])
            y = self._read_adc(self.adc['joy_y'])
            
            if button_name == 'up': return y > (self.joy_center + self.joy_threshold)
            if button_name == 'down': return y < (self.joy_center - self.joy_threshold)
            if button_name == 'left': return x < (self.joy_center - self.joy_threshold)
            if button_name == 'right': return x > (self.joy_center + self.joy_threshold)
            
        elif button_name in self.button_ranges:
            val = self._read_adc(self.adc['btn_ladder'])
            r = self.button_ranges[button_name]
            return r[0] <= val <= r[1]
            
        return False
    
    def was_just_pressed(self, button_name):
        """Check if a button was just pressed (with debouncing)"""
        current_time = time.ticks_ms()
        is_currently_pressed = self.is_pressed(button_name)
        was_previously_pressed = self.button_states.get(button_name, False)
        time_since_last = time.ticks_diff(current_time, self.last_press_time.get(button_name, 0))
        
        if is_currently_pressed and not was_previously_pressed:
            if time_since_last > self.debounce_time_ms:
                self.button_states[button_name] = True
                self.last_press_time[button_name] = current_time
                return True
        
        if not is_currently_pressed and was_previously_pressed:
            self.button_states[button_name] = False
        
        return False
    
    def get_direction(self):
        dx = 0
        dy = 0
        if self.is_pressed('up'): dy -= 1
        if self.is_pressed('down'): dy += 1
        if self.is_pressed('left'): dx -= 1
        if self.is_pressed('right'): dx += 1
        return (dx, dy)
    
    def any_button_pressed(self):
        return any(self.is_pressed(btn) for btn in self.all_btns)
    
    def get_pressed_buttons(self):
        return [name for name in self.all_btns if self.is_pressed(name)]

    def consume_all(self):
        now = time.ticks_ms()
        for btn_name in self.all_btns:
            self.button_states[btn_name] = self.is_pressed(btn_name)
            self.last_press_time[btn_name] = now
