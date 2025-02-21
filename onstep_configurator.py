import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import requests
import os
import sys

class OnStepConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("OnStepX Configurator")
        self.root.geometry("600x600")

        self.config_vars = {}
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        self.create_scrollable_tab("Controller", self.create_controller_tab)
        self.create_scrollable_tab("Mount", self.create_mount_tab)
        self.create_scrollable_tab("Rotator", self.create_rotator_tab)
        self.create_scrollable_tab("Focusers", self.create_focuser_tab)
        self.create_scrollable_tab("Auxiliary", self.create_aux_tab)

        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Save Preset", command=self.save_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Preset", command=self.load_preset).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Fetch from GitHub", command=self.fetch_from_github).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generate Config", command=self.generate_config).pack(side=tk.LEFT, padx=5)

        self.output_text = tk.Text(root, height=15)
        self.output_text.pack(pady=10, padx=10, fill=tk.BOTH)

    def create_scrollable_tab(self, tab_name, content_method):
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=tab_name)
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_mouse_wheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        canvas.bind("<MouseWheel>", on_mouse_wheel)
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        canvas.focus_set()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        content_method(scrollable_frame)

    def create_controller_tab(self, frame):
        row = 0
        tk.Label(frame, text="Pinmap:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['PINMAP'] = tk.StringVar(value="BTT_SKR_PRO")
        ttk.Combobox(frame, textvariable=self.config_vars['PINMAP'], 
                     values=["OFF", "BTT_SKR_PRO", "MiniPCB", "MiniPCB2", "MaxPCB2", "MaxESP3", "CNC3", "STM32Blue"]).grid(row=row, column=1)
        row += 1

        baud_options = ["9600", "19200", "57600", "115200", "230400", "460800"]
        for port, default in [('A', '9600'), ('B', '230400'), ('C', 'OFF'), ('D', 'OFF'), ('E', 'OFF')]:
            tk.Label(frame, text=f"Serial {port} Baud:").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[f'SERIAL_{port}_BAUD_DEFAULT'] = tk.StringVar(value=default)
            ttk.Combobox(frame, textvariable=self.config_vars[f'SERIAL_{port}_BAUD_DEFAULT'], 
                        values=["OFF"] + baud_options).grid(row=row, column=1)
            row += 1
        
        tk.Label(frame, text="Serial B ESP Flashing:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['SERIAL_B_ESP_FLASHING'] = tk.StringVar(value="ON")
        ttk.Combobox(frame, textvariable=self.config_vars['SERIAL_B_ESP_FLASHING'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Serial Radio:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['SERIAL_RADIO'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['SERIAL_RADIO'], 
                    values=["OFF", "BLUETOOTH", "WIFI_ACCESS_POINT", "WIFI_STATION"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="WiFi Module:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['WIFI_MODULE'] = tk.StringVar(value="CH_PD")
        ttk.Combobox(frame, textvariable=self.config_vars['WIFI_MODULE'], values=["OFF", "CH_PD"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Status LED:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['STATUS_LED'] = tk.StringVar(value="ON")
        ttk.Combobox(frame, textvariable=self.config_vars['STATUS_LED'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Reticle LED Default:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['RETICLE_LED_DEFAULT'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['RETICLE_LED_DEFAULT'], 
                     values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        for param in ['RETICLE_LED_MEMORY', 'RETICLE_LED_INVERT']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Weather Sensor:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['WEATHER'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['WEATHER'], 
                    values=["OFF", "BME280", "BME280_0x76", "BME280_SPI", "BMP280", "BMP280_0x76", "BMP280_SPI"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Step Wave Form:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['STEP_WAVE_FORM'] = tk.StringVar(value="PULSE")
        ttk.Combobox(frame, textvariable=self.config_vars['STEP_WAVE_FORM'], values=["SQUARE", "PULSE"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="NV Driver:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['NV_DRIVER'] = tk.StringVar(value="NV_AT24C32")
        ttk.Combobox(frame, textvariable=self.config_vars['NV_DRIVER'], values=["NV_DEFAULT", "NV_AT24C32"]).grid(row=row, column=1)

    def create_mount_tab(self, frame):
        row = 0
        driver_options = ["OFF", "A4988", "DRV8825", "LV8729", "S109", "TMC2130", "TMC5160", "TMC2209"]

        tk.Label(frame, text="Axis 1 Driver Model:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['AXIS1_DRIVER_MODEL'] = tk.StringVar(value="TMC2130")
        ttk.Combobox(frame, textvariable=self.config_vars['AXIS1_DRIVER_MODEL'], values=driver_options).grid(row=row, column=1)
        row += 1

        for param, default in [
            ('AXIS1_STEPS_PER_DEGREE', '24888'),
            ('AXIS1_LIMIT_MIN', '-180'),
            ('AXIS1_LIMIT_MAX', '180'),
            ('AXIS1_DRIVER_MICROSTEPS', '16'),
            ('AXIS1_DRIVER_MICROSTEPS_GOTO', '1'),
            ('AXIS1_DRIVER_IHOLD', '500'),
            ('AXIS1_DRIVER_IRUN', '800'),
            ('AXIS1_DRIVER_IGOTO', '1200')
        ]:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value=default)
            tk.Entry(frame, textvariable=self.config_vars[param]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS1_REVERSE', 'AXIS1_POWER_DOWN', 'AXIS1_SENSE_HOME']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Axis 1 Driver Status:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['AXIS1_DRIVER_STATUS'] = tk.StringVar(value="ON")
        ttk.Combobox(frame, textvariable=self.config_vars['AXIS1_DRIVER_STATUS'], values=["OFF", "ON", "HIGH", "LOW"]).grid(row=row, column=1)
        row += 1

        for param in ['AXIS1_DRIVER_DECAY', 'AXIS1_DRIVER_DECAY_GOTO']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "STEALTHCHOP", "SPREADCYCLE"]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS1_SENSE_LIMIT_MIN', 'AXIS1_SENSE_LIMIT_MAX']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="LIMIT_SENSE")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "HIGH", "LOW", "LIMIT_SENSE"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Axis 2 Driver Model:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['AXIS2_DRIVER_MODEL'] = tk.StringVar(value="TMC2130")
        ttk.Combobox(frame, textvariable=self.config_vars['AXIS2_DRIVER_MODEL'], values=driver_options).grid(row=row, column=1)
        row += 1

        for param, default in [
            ('AXIS2_STEPS_PER_DEGREE', '24888'),
            ('AXIS2_LIMIT_MIN', '-90'),
            ('AXIS2_LIMIT_MAX', '90'),
            ('AXIS2_DRIVER_MICROSTEPS', '16'),
            ('AXIS2_DRIVER_MICROSTEPS_GOTO', '1'),
            ('AXIS2_DRIVER_IHOLD', '500'),
            ('AXIS2_DRIVER_IRUN', '800'),
            ('AXIS2_DRIVER_IGOTO', '1200')
        ]:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value=default)
            tk.Entry(frame, textvariable=self.config_vars[param]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS2_REVERSE', 'AXIS2_POWER_DOWN', 'AXIS2_SENSE_HOME']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Axis 2 Driver Status:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['AXIS2_DRIVER_STATUS'] = tk.StringVar(value="ON")
        ttk.Combobox(frame, textvariable=self.config_vars['AXIS2_DRIVER_STATUS'], values=["OFF", "ON", "HIGH", "LOW"]).grid(row=row, column=1)
        row += 1

        for param in ['AXIS2_DRIVER_DECAY', 'AXIS2_DRIVER_DECAY_GOTO']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "STEALTHCHOP", "SPREADCYCLE"]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS2_SENSE_LIMIT_MIN', 'AXIS2_SENSE_LIMIT_MAX']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="LIMIT_SENSE")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "HIGH", "LOW", "LIMIT_SENSE"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Mount Type:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['MOUNT_TYPE'] = tk.StringVar(value="GEM")
        ttk.Combobox(frame, textvariable=self.config_vars['MOUNT_TYPE'], 
                    values=["GEM", "GEM_TA", "GEM_TAC", "FORK", "FORK_TA", "FORK_TAC", "ALTAZM", "ALTAZM_UNL"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Mount Coords:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['MOUNT_COORDS'] = tk.StringVar(value="TOPOCENTRIC")
        ttk.Combobox(frame, textvariable=self.config_vars['MOUNT_COORDS'], 
                    values=["TOPOCENTRIC", "TOPO_STRICT", "OBSERVED_PLACE"]).grid(row=row, column=1)
        row += 1

        for param in ['MOUNT_COORDS_MEMORY', 'MOUNT_ENABLE_IN_STANDBY']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Time Location Source:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['TIME_LOCATION_SOURCE'] = tk.StringVar(value="DS3231")
        ttk.Combobox(frame, textvariable=self.config_vars['TIME_LOCATION_SOURCE'], 
                    values=["OFF", "DS3231", "SD3031", "TEENSY", "GPS", "NTP"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="PPS Sense:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['TIME_LOCATION_PPS_SENSE'] = tk.StringVar(value="HIGH")
        ttk.Combobox(frame, textvariable=self.config_vars['TIME_LOCATION_PPS_SENSE'], 
                    values=["OFF", "HIGH", "LOW", "BOTH"]).grid(row=row, column=1)
        row += 1

        for param in ['STATUS_MOUNT_LED', 'STATUS_BUZZER_DEFAULT', 'STATUS_BUZZER_MEMORY']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Status Buzzer:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['STATUS_BUZZER'] = tk.StringVar(value="OFF")
        tk.Entry(frame, textvariable=self.config_vars['STATUS_BUZZER']).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="ST4 Interface:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['ST4_INTERFACE'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['ST4_INTERFACE'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        for param in ['ST4_HAND_CONTROL', 'ST4_HAND_CONTROL_FOCUSER']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="ON")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Guide Time Limit:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['GUIDE_TIME_LIMIT'] = tk.StringVar(value="10")
        tk.Entry(frame, textvariable=self.config_vars['GUIDE_TIME_LIMIT']).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Guide Disable Backlash:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['GUIDE_DISABLE_BACKLASH'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['GUIDE_DISABLE_BACKLASH'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Limit Sense:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['LIMIT_SENSE'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['LIMIT_SENSE'], values=["OFF", "HIGH", "LOW"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Limit Strict:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['LIMIT_STRICT'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['LIMIT_STRICT'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        for param in ['PARK_SENSE', 'PARK_SIGNAL', 'PARK_STATUS', 'PARK_STRICT']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "HIGH", "LOW"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="PEC Steps Per Worm Rotation:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['PEC_STEPS_PER_WORM_ROTATION'] = tk.StringVar(value="0")
        tk.Entry(frame, textvariable=self.config_vars['PEC_STEPS_PER_WORM_ROTATION']).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="PEC Sense:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['PEC_SENSE'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['PEC_SENSE'], values=["OFF", "HIGH", "LOW"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="PEC Buffer Size Limit:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['PEC_BUFFER_SIZE_LIMIT'] = tk.StringVar(value="720")
        tk.Entry(frame, textvariable=self.config_vars['PEC_BUFFER_SIZE_LIMIT']).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Track Backlash Rate:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['TRACK_BACKLASH_RATE'] = tk.StringVar(value="2")
        tk.Entry(frame, textvariable=self.config_vars['TRACK_BACKLASH_RATE']).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Track Autostart:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['TRACK_AUTOSTART'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['TRACK_AUTOSTART'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Track Compensation Default:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['TRACK_COMPENSATION_DEFAULT'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['TRACK_COMPENSATION_DEFAULT'], 
                    values=["OFF", "REFRACTION", "REFRACTION_DUAL", "MODEL", "MODEL_DUAL"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Track Compensation Memory:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['TRACK_COMPENSATION_MEMORY'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['TRACK_COMPENSATION_MEMORY'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Slew Rate Base Desired:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['SLEW_RATE_BASE_DESIRED'] = tk.StringVar(value="1")
        tk.Entry(frame, textvariable=self.config_vars['SLEW_RATE_BASE_DESIRED']).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Slew Rate Memory:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['SLEW_RATE_MEMORY'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['SLEW_RATE_MEMORY'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        for param, default in [
            ('SLEW_ACCELERATION_DIST', '5.0'),
            ('SLEW_RAPID_STOP_DIST', '2.0'),
            ('GOTO_OFFSET', '0.25')
        ]:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value=default)
            tk.Entry(frame, textvariable=self.config_vars[param]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Goto Feature:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['GOTO_FEATURE'] = tk.StringVar(value="ON")
        ttk.Combobox(frame, textvariable=self.config_vars['GOTO_FEATURE'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Goto Offset Align:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['GOTO_OFFSET_ALIGN'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['GOTO_OFFSET_ALIGN'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        for param in ['MFLIP_SKIP_HOME', 'MFLIP_AUTOMATIC_DEFAULT', 'MFLIP_AUTOMATIC_MEMORY', 
                     'MFLIP_PAUSE_HOME_DEFAULT', 'MFLIP_PAUSE_HOME_MEMORY', 'PIER_SIDE_SYNC_CHANGE_SIDES']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Pier Side Preferred Default:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['PIER_SIDE_PREFERRED_DEFAULT'] = tk.StringVar(value="BEST")
        ttk.Combobox(frame, textvariable=self.config_vars['PIER_SIDE_PREFERRED_DEFAULT'], 
                    values=["BEST", "EAST", "WEST"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Pier Side Preferred Memory:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['PIER_SIDE_PREFERRED_MEMORY'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['PIER_SIDE_PREFERRED_MEMORY'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Align Auto Home:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['ALIGN_AUTO_HOME'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['ALIGN_AUTO_HOME'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Align Model Memory:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['ALIGN_MODEL_MEMORY'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['ALIGN_MODEL_MEMORY'], values=["OFF", "ON"]).grid(row=row, column=1)
        row += 1

        tk.Label(frame, text="Align Max Stars:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['ALIGN_MAX_STARS'] = tk.StringVar(value="AUTO")
        ttk.Combobox(frame, textvariable=self.config_vars['ALIGN_MAX_STARS'], 
                    values=["AUTO", "1", "3", "4", "5", "6", "7", "8", "9"]).grid(row=row, column=1)

    def create_rotator_tab(self, frame):
        row = 0
        driver_options = ["OFF", "A4988", "DRV8825", "LV8729", "S109", "TMC2130", "TMC5160", "TMC2209"]

        tk.Label(frame, text="Axis 3 Driver Model:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['AXIS3_DRIVER_MODEL'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['AXIS3_DRIVER_MODEL'], values=driver_options).grid(row=row, column=1)
        row += 1

        for param, default in [
            ('AXIS3_SLEW_RATE_BASE_DESIRED', '1.0'),
            ('AXIS3_STEPS_PER_DEGREE', '64.0'),
            ('AXIS3_LIMIT_MIN', '0'),
            ('AXIS3_LIMIT_MAX', '360')
        ]:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value=default)
            tk.Entry(frame, textvariable=self.config_vars[param]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS3_REVERSE', 'AXIS3_POWER_DOWN', 'AXIS3_SENSE_HOME']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Axis 3 Driver Status:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['AXIS3_DRIVER_STATUS'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['AXIS3_DRIVER_STATUS'], values=["OFF", "ON", "HIGH", "LOW"]).grid(row=row, column=1)
        row += 1

        for param in ['AXIS3_DRIVER_MICROSTEPS', 'AXIS3_DRIVER_MICROSTEPS_GOTO', 'AXIS3_DRIVER_IHOLD', 
                     'AXIS3_DRIVER_IRUN', 'AXIS3_DRIVER_IGOTO']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            tk.Entry(frame, textvariable=self.config_vars[param]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS3_DRIVER_DECAY', 'AXIS3_DRIVER_DECAY_GOTO']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "STEALTHCHOP", "SPREADCYCLE"]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS3_SENSE_LIMIT_MIN', 'AXIS3_SENSE_LIMIT_MAX']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "HIGH", "LOW"]).grid(row=row, column=1)

    def create_focuser_tab(self, frame):
        row = 0
        driver_options = ["OFF", "A4988", "DRV8825", "LV8729", "S109", "TMC2130", "TMC5160", "TMC2209"]

        tk.Label(frame, text="Axis 4 Driver Model:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['AXIS4_DRIVER_MODEL'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['AXIS4_DRIVER_MODEL'], values=driver_options).grid(row=row, column=1)
        row += 1

        for param, default in [
            ('AXIS4_SLEW_RATE_BASE_DESIRED', '500'),
            ('AXIS4_SLEW_RATE_MINIMUM', '20'),
            ('AXIS4_STEPS_PER_MICRON', '0.5'),
            ('AXIS4_LIMIT_MIN', '0'),
            ('AXIS4_LIMIT_MAX', '50')
        ]:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value=default)
            tk.Entry(frame, textvariable=self.config_vars[param]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS4_REVERSE', 'AXIS4_POWER_DOWN', 'AXIS4_SENSE_HOME']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Axis 4 Driver Status:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['AXIS4_DRIVER_STATUS'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['AXIS4_DRIVER_STATUS'], values=["OFF", "ON", "HIGH", "LOW"]).grid(row=row, column=1)
        row += 1

        for param in ['AXIS4_DRIVER_MICROSTEPS', 'AXIS4_DRIVER_MICROSTEPS_GOTO', 'AXIS4_DRIVER_IHOLD', 
                     'AXIS4_DRIVER_IRUN', 'AXIS4_DRIVER_IGOTO']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            tk.Entry(frame, textvariable=self.config_vars[param]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS4_DRIVER_DECAY', 'AXIS4_DRIVER_DECAY_GOTO']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "STEALTHCHOP", "SPREADCYCLE"]).grid(row=row, column=1)
            row += 1

        for param in ['AXIS4_SENSE_LIMIT_MIN', 'AXIS4_SENSE_LIMIT_MAX']:
            tk.Label(frame, text=param.replace('_', ' ')+":").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[param] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[param], values=["OFF", "HIGH", "LOW"]).grid(row=row, column=1)
            row += 1

        tk.Label(frame, text="Focuser Temperature:").grid(row=row, column=0, padx=5, pady=5)
        self.config_vars['FOCUSER_TEMPERATURE'] = tk.StringVar(value="OFF")
        ttk.Combobox(frame, textvariable=self.config_vars['FOCUSER_TEMPERATURE'], values=["OFF", "THERMISTOR"]).grid(row=row, column=1)

    def create_aux_tab(self, frame):
        row = 0
        purpose_options = ["OFF", "SWITCH", "MOMENTARY_SWITCH", "ANALOG_OUT", "DEW_HEATER", "INTERVALOMETER"]

        for i in range(1, 9):
            tk.Label(frame, text=f"Feature {i} Purpose:").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[f'FEATURE{i}_PURPOSE'] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[f'FEATURE{i}_PURPOSE'], values=purpose_options).grid(row=row, column=1)
            row += 1

            tk.Label(frame, text=f"Feature {i} Name:").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[f'FEATURE{i}_NAME'] = tk.StringVar(value=f"FEATURE{i}")
            tk.Entry(frame, textvariable=self.config_vars[f'FEATURE{i}_NAME']).grid(row=row, column=1)
            row += 1

            for param in ['TEMP', 'PIN', 'VALUE_DEFAULT']:
                tk.Label(frame, text=f"Feature {i} {param}:").grid(row=row, column=0, padx=5, pady=5)
                self.config_vars[f'FEATURE{i}_{param}'] = tk.StringVar(value="OFF")
                tk.Entry(frame, textvariable=self.config_vars[f'FEATURE{i}_{param}']).grid(row=row, column=1)
                row += 1

            tk.Label(frame, text=f"Feature {i} Value Memory:").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[f'FEATURE{i}_VALUE_MEMORY'] = tk.StringVar(value="OFF")
            ttk.Combobox(frame, textvariable=self.config_vars[f'FEATURE{i}_VALUE_MEMORY'], values=["OFF", "ON"]).grid(row=row, column=1)
            row += 1

            tk.Label(frame, text=f"Feature {i} On State:").grid(row=row, column=0, padx=5, pady=5)
            self.config_vars[f'FEATURE{i}_ON_STATE'] = tk.StringVar(value="HIGH")
            ttk.Combobox(frame, textvariable=self.config_vars[f'FEATURE{i}_ON_STATE'], values=["HIGH", "LOW"]).grid(row=row, column=1)
            row += 1

    def fetch_from_github(self):
        repo_owner = "Mr-Royce"  # Replace with your GitHub username
        repo_name = "onstep-configurator"  # Replace with your repo name
        folder_path = "presets"      # Folder in the repo containing config files
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{folder_path}"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            files = response.json()

            config_files = [f["name"] for f in files if f["name"].endswith((".json", ".csv"))]
            if not config_files:
                messagebox.showwarning("No Files", "No configuration files found in the GitHub repository.")
                return

            selection_window = tk.Toplevel(self.root)
            selection_window.title("Select Configuration File")
            selection_window.geometry("300x200")

            tk.Label(selection_window, text="Select a file to load:").pack(pady=5)
            file_var = tk.StringVar(value=config_files[0])
            ttk.Combobox(selection_window, textvariable=file_var, values=config_files).pack(pady=5)

            def load_selected_file():
                selected_file = file_var.get()
                file_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{folder_path}/{selected_file}"
                temp_file = f"temp_{selected_file}"

                file_response = requests.get(file_url)
                file_response.raise_for_status()
                with open(temp_file, 'wb') as f:
                    f.write(file_response.content)

                if selected_file.endswith(".json"):
                    with open(temp_file, 'r') as f:
                        preset = json.load(f)
                    for key, value in preset.items():
                        if key in self.config_vars:
                            self.config_vars[key].set(value)
                elif selected_file.endswith(".csv"):
                    with open(temp_file, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            for key, value in row.items():
                                if key in self.config_vars:
                                    self.config_vars[key].set(value)

                os.remove(temp_file)
                selection_window.destroy()
                messagebox.showinfo("Success", f"Loaded {selected_file} from GitHub!")

            ttk.Button(selection_window, text="Load", command=load_selected_file).pack(pady=10)

        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch files from GitHub: {str(e)}")

    def save_preset(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            preset = {key: var.get() for key, var in self.config_vars.items()}
            with open(file_path, 'w') as f:
                json.dump(preset, f)
            messagebox.showinfo("Success", "Preset saved successfully!")

    def load_preset(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                preset = json.load(f)
            for key, value in preset.items():
                if key in self.config_vars:
                    self.config_vars[key].set(value)
            messagebox.showinfo("Success", "Preset loaded successfully!")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for key, value in row.items():
                        if key in self.config_vars:
                            self.config_vars[key].set(value)
            messagebox.showinfo("Success", "CSV imported successfully!")

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            preset = {key: var.get() for key, var in self.config_vars.items()}
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=preset.keys())
                writer.writeheader()
                writer.writerow(preset)
            messagebox.showinfo("Success", "CSV exported successfully!")

    def generate_config(self):
        config_lines = [
            "/* Configuration for OnStepX */",
            "",
            "// CONTROLLER",
            f"#define PINMAP                        {self.config_vars['PINMAP'].get()}",
            f"#define SERIAL_A_BAUD_DEFAULT        {self.config_vars['SERIAL_A_BAUD_DEFAULT'].get()}",
            f"#define SERIAL_B_BAUD_DEFAULT        {self.config_vars['SERIAL_B_BAUD_DEFAULT'].get()}",
            f"#define SERIAL_B_ESP_FLASHING         {self.config_vars['SERIAL_B_ESP_FLASHING'].get()}",
            f"#define SERIAL_C_BAUD_DEFAULT        {self.config_vars['SERIAL_C_BAUD_DEFAULT'].get()}",
            f"#define SERIAL_D_BAUD_DEFAULT        {self.config_vars['SERIAL_D_BAUD_DEFAULT'].get()}",
            f"#define SERIAL_E_BAUD_DEFAULT        {self.config_vars['SERIAL_E_BAUD_DEFAULT'].get()}",
            f"#define SERIAL_RADIO                  {self.config_vars['SERIAL_RADIO'].get()}",
            f"#define WIFI_MODULE                  {self.config_vars['WIFI_MODULE'].get()}",
            f"#define STATUS_LED                    {self.config_vars['STATUS_LED'].get()}",
            f"#define RETICLE_LED_DEFAULT           {self.config_vars['RETICLE_LED_DEFAULT'].get()}",
            f"#define RETICLE_LED_MEMORY            {self.config_vars['RETICLE_LED_MEMORY'].get()}",
            f"#define RETICLE_LED_INVERT            {self.config_vars['RETICLE_LED_INVERT'].get()}",
            f"#define WEATHER                       {self.config_vars['WEATHER'].get()}",
            f"#define STEP_WAVE_FORM                {self.config_vars['STEP_WAVE_FORM'].get()}",
            f"#define NV_DRIVER                     {self.config_vars['NV_DRIVER'].get()}",
            "",
            "// MOUNT",
            f"#define AXIS1_DRIVER_MODEL            {self.config_vars['AXIS1_DRIVER_MODEL'].get()}",
            f"#define AXIS1_STEPS_PER_DEGREE       {self.config_vars['AXIS1_STEPS_PER_DEGREE'].get()}",
            f"#define AXIS1_REVERSE                 {self.config_vars['AXIS1_REVERSE'].get()}",
            f"#define AXIS1_LIMIT_MIN              {self.config_vars['AXIS1_LIMIT_MIN'].get()}",
            f"#define AXIS1_LIMIT_MAX              {self.config_vars['AXIS1_LIMIT_MAX'].get()}",
            f"#define AXIS1_DRIVER_MICROSTEPS      {self.config_vars['AXIS1_DRIVER_MICROSTEPS'].get()}",
            f"#define AXIS1_DRIVER_MICROSTEPS_GOTO {self.config_vars['AXIS1_DRIVER_MICROSTEPS_GOTO'].get()}",
            f"#define AXIS1_DRIVER_IHOLD           {self.config_vars['AXIS1_DRIVER_IHOLD'].get()}",
            f"#define AXIS1_DRIVER_IRUN            {self.config_vars['AXIS1_DRIVER_IRUN'].get()}",
            f"#define AXIS1_DRIVER_IGOTO           {self.config_vars['AXIS1_DRIVER_IGOTO'].get()}",
            f"#define AXIS1_DRIVER_STATUS          {self.config_vars['AXIS1_DRIVER_STATUS'].get()}",
            f"#define AXIS1_DRIVER_DECAY           {self.config_vars['AXIS1_DRIVER_DECAY'].get()}",
            f"#define AXIS1_DRIVER_DECAY_GOTO      {self.config_vars['AXIS1_DRIVER_DECAY_GOTO'].get()}",
            f"#define AXIS1_POWER_DOWN             {self.config_vars['AXIS1_POWER_DOWN'].get()}",
            f"#define AXIS1_SENSE_HOME             {self.config_vars['AXIS1_SENSE_HOME'].get()}",
            f"#define AXIS1_SENSE_LIMIT_MIN        {self.config_vars['AXIS1_SENSE_LIMIT_MIN'].get()}",
            f"#define AXIS1_SENSE_LIMIT_MAX        {self.config_vars['AXIS1_SENSE_LIMIT_MAX'].get()}",
            "",
            f"#define AXIS2_DRIVER_MODEL            {self.config_vars['AXIS2_DRIVER_MODEL'].get()}",
            f"#define AXIS2_STEPS_PER_DEGREE       {self.config_vars['AXIS2_STEPS_PER_DEGREE'].get()}",
            f"#define AXIS2_REVERSE                 {self.config_vars['AXIS2_REVERSE'].get()}",
            f"#define AXIS2_LIMIT_MIN              {self.config_vars['AXIS2_LIMIT_MIN'].get()}",
            f"#define AXIS2_LIMIT_MAX              {self.config_vars['AXIS2_LIMIT_MAX'].get()}",
            f"#define AXIS2_DRIVER_MICROSTEPS      {self.config_vars['AXIS2_DRIVER_MICROSTEPS'].get()}",
            f"#define AXIS2_DRIVER_MICROSTEPS_GOTO {self.config_vars['AXIS2_DRIVER_MICROSTEPS_GOTO'].get()}",
            f"#define AXIS2_DRIVER_IHOLD           {self.config_vars['AXIS2_DRIVER_IHOLD'].get()}",
            f"#define AXIS2_DRIVER_IRUN            {self.config_vars['AXIS2_DRIVER_IRUN'].get()}",
            f"#define AXIS2_DRIVER_IGOTO           {self.config_vars['AXIS2_DRIVER_IGOTO'].get()}",
            f"#define AXIS2_DRIVER_STATUS          {self.config_vars['AXIS2_DRIVER_STATUS'].get()}",
            f"#define AXIS2_DRIVER_DECAY           {self.config_vars['AXIS2_DRIVER_DECAY'].get()}",
            f"#define AXIS2_DRIVER_DECAY_GOTO      {self.config_vars['AXIS2_DRIVER_DECAY_GOTO'].get()}",
            f"#define AXIS2_POWER_DOWN             {self.config_vars['AXIS2_POWER_DOWN'].get()}",
            f"#define AXIS2_SENSE_HOME             {self.config_vars['AXIS2_SENSE_HOME'].get()}",
            f"#define AXIS2_SENSE_LIMIT_MIN        {self.config_vars['AXIS2_SENSE_LIMIT_MIN'].get()}",
            f"#define AXIS2_SENSE_LIMIT_MAX        {self.config_vars['AXIS2_SENSE_LIMIT_MAX'].get()}",
            "",
            f"#define MOUNT_TYPE                    {self.config_vars['MOUNT_TYPE'].get()}",
            f"#define MOUNT_COORDS                  {self.config_vars['MOUNT_COORDS'].get()}",
            f"#define MOUNT_COORDS_MEMORY           {self.config_vars['MOUNT_COORDS_MEMORY'].get()}",
            f"#define MOUNT_ENABLE_IN_STANDBY       {self.config_vars['MOUNT_ENABLE_IN_STANDBY'].get()}",
            f"#define TIME_LOCATION_SOURCE          {self.config_vars['TIME_LOCATION_SOURCE'].get()}",
            f"#define TIME_LOCATION_PPS_SENSE       {self.config_vars['TIME_LOCATION_PPS_SENSE'].get()}",
            f"#define STATUS_MOUNT_LED             {self.config_vars['STATUS_MOUNT_LED'].get()}",
            f"#define STATUS_BUZZER                {self.config_vars['STATUS_BUZZER'].get()}",
            f"#define STATUS_BUZZER_DEFAULT        {self.config_vars['STATUS_BUZZER_DEFAULT'].get()}",
            f"#define STATUS_BUZZER_MEMORY         {self.config_vars['STATUS_BUZZER_MEMORY'].get()}",
            f"#define ST4_INTERFACE                {self.config_vars['ST4_INTERFACE'].get()}",
            f"#define ST4_HAND_CONTROL             {self.config_vars['ST4_HAND_CONTROL'].get()}",
            f"#define ST4_HAND_CONTROL_FOCUSER     {self.config_vars['ST4_HAND_CONTROL_FOCUSER'].get()}",
            f"#define GUIDE_TIME_LIMIT             {self.config_vars['GUIDE_TIME_LIMIT'].get()}",
            f"#define GUIDE_DISABLE_BACKLASH       {self.config_vars['GUIDE_DISABLE_BACKLASH'].get()}",
            f"#define LIMIT_SENSE                  {self.config_vars['LIMIT_SENSE'].get()}",
            f"#define LIMIT_STRICT                 {self.config_vars['LIMIT_STRICT'].get()}",
            f"#define PARK_SENSE                   {self.config_vars['PARK_SENSE'].get()}",
            f"#define PARK_SIGNAL                  {self.config_vars['PARK_SIGNAL'].get()}",
            f"#define PARK_STATUS                  {self.config_vars['PARK_STATUS'].get()}",
            f"#define PARK_STRICT                  {self.config_vars['PARK_STRICT'].get()}",
            f"#define PEC_STEPS_PER_WORM_ROTATION  {self.config_vars['PEC_STEPS_PER_WORM_ROTATION'].get()}",
            f"#define PEC_SENSE                    {self.config_vars['PEC_SENSE'].get()}",
            f"#define PEC_BUFFER_SIZE_LIMIT        {self.config_vars['PEC_BUFFER_SIZE_LIMIT'].get()}",
            f"#define TRACK_BACKLASH_RATE          {self.config_vars['TRACK_BACKLASH_RATE'].get()}",
            f"#define TRACK_AUTOSTART              {self.config_vars['TRACK_AUTOSTART'].get()}",
            f"#define TRACK_COMPENSATION_DEFAULT   {self.config_vars['TRACK_COMPENSATION_DEFAULT'].get()}",
            f"#define TRACK_COMPENSATION_MEMORY    {self.config_vars['TRACK_COMPENSATION_MEMORY'].get()}",
            f"#define SLEW_RATE_BASE_DESIRED       {self.config_vars['SLEW_RATE_BASE_DESIRED'].get()}",
            f"#define SLEW_RATE_MEMORY             {self.config_vars['SLEW_RATE_MEMORY'].get()}",
            f"#define SLEW_ACCELERATION_DIST       {self.config_vars['SLEW_ACCELERATION_DIST'].get()}",
            f"#define SLEW_RAPID_STOP_DIST         {self.config_vars['SLEW_RAPID_STOP_DIST'].get()}",
            f"#define GOTO_FEATURE                 {self.config_vars['GOTO_FEATURE'].get()}",
            f"#define GOTO_OFFSET                  {self.config_vars['GOTO_OFFSET'].get()}",
            f"#define GOTO_OFFSET_ALIGN            {self.config_vars['GOTO_OFFSET_ALIGN'].get()}",
            f"#define MFLIP_SKIP_HOME              {self.config_vars['MFLIP_SKIP_HOME'].get()}",
            f"#define MFLIP_AUTOMATIC_DEFAULT      {self.config_vars['MFLIP_AUTOMATIC_DEFAULT'].get()}",
            f"#define MFLIP_AUTOMATIC_MEMORY       {self.config_vars['MFLIP_AUTOMATIC_MEMORY'].get()}",
            f"#define MFLIP_PAUSE_HOME_DEFAULT     {self.config_vars['MFLIP_PAUSE_HOME_DEFAULT'].get()}",
            f"#define MFLIP_PAUSE_HOME_MEMORY      {self.config_vars['MFLIP_PAUSE_HOME_MEMORY'].get()}",
            f"#define PIER_SIDE_SYNC_CHANGE_SIDES  {self.config_vars['PIER_SIDE_SYNC_CHANGE_SIDES'].get()}",
            f"#define PIER_SIDE_PREFERRED_DEFAULT  {self.config_vars['PIER_SIDE_PREFERRED_DEFAULT'].get()}",
            f"#define PIER_SIDE_PREFERRED_MEMORY   {self.config_vars['PIER_SIDE_PREFERRED_MEMORY'].get()}",
            f"#define ALIGN_AUTO_HOME              {self.config_vars['ALIGN_AUTO_HOME'].get()}",
            f"#define ALIGN_MODEL_MEMORY           {self.config_vars['ALIGN_MODEL_MEMORY'].get()}",
            f"#define ALIGN_MAX_STARS              {self.config_vars['ALIGN_MAX_STARS'].get()}",
            "",
            "// ROTATOR",
            f"#define AXIS3_DRIVER_MODEL            {self.config_vars['AXIS3_DRIVER_MODEL'].get()}",
            f"#define AXIS3_SLEW_RATE_BASE_DESIRED {self.config_vars['AXIS3_SLEW_RATE_BASE_DESIRED'].get()}",
            f"#define AXIS3_STEPS_PER_DEGREE       {self.config_vars['AXIS3_STEPS_PER_DEGREE'].get()}",
            f"#define AXIS3_REVERSE                 {self.config_vars['AXIS3_REVERSE'].get()}",
            f"#define AXIS3_LIMIT_MIN              {self.config_vars['AXIS3_LIMIT_MIN'].get()}",
            f"#define AXIS3_LIMIT_MAX              {self.config_vars['AXIS3_LIMIT_MAX'].get()}",
            f"#define AXIS3_DRIVER_MICROSTEPS      {self.config_vars['AXIS3_DRIVER_MICROSTEPS'].get()}",
            f"#define AXIS3_DRIVER_MICROSTEPS_GOTO {self.config_vars['AXIS3_DRIVER_MICROSTEPS_GOTO'].get()}",
            f"#define AXIS3_DRIVER_IHOLD           {self.config_vars['AXIS3_DRIVER_IHOLD'].get()}",
            f"#define AXIS3_DRIVER_IRUN            {self.config_vars['AXIS3_DRIVER_IRUN'].get()}",
            f"#define AXIS3_DRIVER_IGOTO           {self.config_vars['AXIS3_DRIVER_IGOTO'].get()}",
            f"#define AXIS3_DRIVER_STATUS          {self.config_vars['AXIS3_DRIVER_STATUS'].get()}",
            f"#define AXIS3_DRIVER_DECAY           {self.config_vars['AXIS3_DRIVER_DECAY'].get()}",
            f"#define AXIS3_DRIVER_DECAY_GOTO      {self.config_vars['AXIS3_DRIVER_DECAY_GOTO'].get()}",
            f"#define AXIS3_POWER_DOWN             {self.config_vars['AXIS3_POWER_DOWN'].get()}",
            f"#define AXIS3_SENSE_HOME             {self.config_vars['AXIS3_SENSE_HOME'].get()}",
            f"#define AXIS3_SENSE_LIMIT_MIN        {self.config_vars['AXIS3_SENSE_LIMIT_MIN'].get()}",
            f"#define AXIS3_SENSE_LIMIT_MAX        {self.config_vars['AXIS3_SENSE_LIMIT_MAX'].get()}",
            "",
            "// FOCUSERS",
            f"#define AXIS4_DRIVER_MODEL            {self.config_vars['AXIS4_DRIVER_MODEL'].get()}",
            f"#define AXIS4_SLEW_RATE_BASE_DESIRED {self.config_vars['AXIS4_SLEW_RATE_BASE_DESIRED'].get()}",
            f"#define AXIS4_SLEW_RATE_MINIMUM      {self.config_vars['AXIS4_SLEW_RATE_MINIMUM'].get()}",
            f"#define AXIS4_STEPS_PER_MICRON       {self.config_vars['AXIS4_STEPS_PER_MICRON'].get()}",
            f"#define AXIS4_REVERSE                 {self.config_vars['AXIS4_REVERSE'].get()}",
            f"#define AXIS4_LIMIT_MIN              {self.config_vars['AXIS4_LIMIT_MIN'].get()}",
            f"#define AXIS4_LIMIT_MAX              {self.config_vars['AXIS4_LIMIT_MAX'].get()}",
            f"#define AXIS4_DRIVER_MICROSTEPS      {self.config_vars['AXIS4_DRIVER_MICROSTEPS'].get()}",
            f"#define AXIS4_DRIVER_MICROSTEPS_GOTO {self.config_vars['AXIS4_DRIVER_MICROSTEPS_GOTO'].get()}",
            f"#define AXIS4_DRIVER_IHOLD           {self.config_vars['AXIS4_DRIVER_IHOLD'].get()}",
            f"#define AXIS4_DRIVER_IRUN            {self.config_vars['AXIS4_DRIVER_IRUN'].get()}",
            f"#define AXIS4_DRIVER_IGOTO           {self.config_vars['AXIS4_DRIVER_IGOTO'].get()}",
            f"#define AXIS4_DRIVER_STATUS          {self.config_vars['AXIS4_DRIVER_STATUS'].get()}",
            f"#define AXIS4_DRIVER_DECAY           {self.config_vars['AXIS4_DRIVER_DECAY'].get()}",
            f"#define AXIS4_DRIVER_DECAY_GOTO      {self.config_vars['AXIS4_DRIVER_DECAY_GOTO'].get()}",
            f"#define AXIS4_POWER_DOWN             {self.config_vars['AXIS4_POWER_DOWN'].get()}",
            f"#define AXIS4_SENSE_HOME             {self.config_vars['AXIS4_SENSE_HOME'].get()}",
            f"#define AXIS4_SENSE_LIMIT_MIN        {self.config_vars['AXIS4_SENSE_LIMIT_MIN'].get()}",
            f"#define AXIS4_SENSE_LIMIT_MAX        {self.config_vars['AXIS4_SENSE_LIMIT_MAX'].get()}",
            f"#define FOCUSER_TEMPERATURE           {self.config_vars['FOCUSER_TEMPERATURE'].get()}",
            "",
            "// AUXILIARY FEATURES"
        ]

        for i in range(1, 9):
            config_lines.extend([
                f"#define FEATURE{i}_PURPOSE            {self.config_vars[f'FEATURE{i}_PURPOSE'].get()}",
                f"#define FEATURE{i}_NAME              \"{self.config_vars[f'FEATURE{i}_NAME'].get()}\"",
                f"#define FEATURE{i}_TEMP              {self.config_vars[f'FEATURE{i}_TEMP'].get()}",
                f"#define FEATURE{i}_PIN               {self.config_vars[f'FEATURE{i}_PIN'].get()}",
                f"#define FEATURE{i}_VALUE_DEFAULT     {self.config_vars[f'FEATURE{i}_VALUE_DEFAULT'].get()}",
                f"#define FEATURE{i}_VALUE_MEMORY      {self.config_vars[f'FEATURE{i}_VALUE_MEMORY'].get()}",
                f"#define FEATURE{i}_ON_STATE          {self.config_vars[f'FEATURE{i}_ON_STATE'].get()}",
                ""
            ])

        config_lines.extend([
            "#define FileVersionConfig 6",
            "#include \"Extended.config.h\""
        ])

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "\n".join(config_lines))
        messagebox.showinfo("Success", "Configuration generated! Copy the text from the box below into your Arduino IDE.")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def main():
    root = tk.Tk()
    root.iconbitmap(resource_path("telescope.ico"))
    app = OnStepConfigurator(root)
    root.mainloop()

if __name__ == "__main__":
    main()