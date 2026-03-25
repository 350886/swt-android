#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Driver Management Screen UI - Complete implementation
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.app import App
from kivy.clock import Clock


class DriverScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        Clock.schedule_once(self._init_ui)
    
    def _init_ui(self, dt):
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='[b]司机管理[/b]', markup=True, size_hint_y=None, height=40))
        
        load_btn = Button(text='加载司机列表', background_color=[0.1, 0.56, 1, 1], size_hint_y=None, height=45)
        load_btn.bind(on_press=self.load_drivers)
        layout.add_widget(load_btn)
        
        self.drivers_label = Label(text='点击"加载司机列表"查看司机信息', size_hint_y=None, height=150, text_size=(None, None), halign='left')
        layout.add_widget(self.drivers_label)
        
        layout.add_widget(Label(text='[b]司机统计导出[/b]', markup=True, size_hint_y=None, height=40))
        
        date_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        date_box.add_widget(Label(text='年月:', size_hint_x=None, width=50))
        
        self.year_spin = Spinner(text='2026', values=[str(y) for y in range(2020, 2031)], size_hint_x=None, width=80)
        self.month_spin = Spinner(text='03', values=[f'{m:02d}' for m in range(1, 13)], size_hint_x=None, width=60)
        
        date_box.add_widget(self.year_spin)
        date_box.add_widget(Label(text='年', size_hint_x=None, width=30))
        date_box.add_widget(self.month_spin)
        date_box.add_widget(Label(text='月', size_hint_x=None, width=30))
        
        layout.add_widget(date_box)
        
        export_btn = Button(text='导出司机统计', background_color=[0.3, 0.7, 0.3, 1], size_hint_y=None, height=45)
        export_btn.bind(on_press=self.export_driver_stats)
        layout.add_widget(export_btn)
        
        self.status_label = Label(text='', size_hint_y=None, height=60, text_size=(None, None), halign='left')
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def load_drivers(self, instance):
        if not self.app.cursor:
            self.drivers_label.text = "错误: 数据库未连接"
            return
        
        try:
            self.app.cursor.execute("SELECT DRIVERCODE, NAME, TEL FROM DRIVER_MASTER ORDER BY NAME")
            drivers = self.app.cursor.fetchall()
            
            if drivers:
                text = ""
                for d in drivers[:15]:
                    name = d.get('NAME', d.get(1, ''))
                    tel = d.get('TEL', d.get(2, ''))
                    text += f"• {name} - {tel}\n"
                self.drivers_label.text = text
            else:
                self.drivers_label.text = "暂无司机数据"
        except Exception as e:
            self.drivers_label.text = f"加载失败: {e}"
    
    def export_driver_stats(self, instance):
        year = int(self.year_spin.text)
        month = int(self.month_spin.text)
        
        if not self.app.cursor:
            self.status_label.text = "错误: 数据库未连接"
            return
        
        try:
            summary_dir = self.app.config.get('summary_dir', '/storage/emulated/0/Download/SWT')
            import os
            os.makedirs(summary_dir, exist_ok=True)
            
            self.app.cursor.execute(f"""
                SELECT 
                    d.DRIVERCODE,
                    d.NAME,
                    d.TEL,
                    COUNT(i.INVOICECODE) as invoice_count,
                    COALESCE(SUM(i.TOTAMT), 0) as total_amount,
                    COALESCE(SUM(i.DRIVER_FEE), 0) as driver_fee
                FROM DRIVER_MASTER d
                LEFT JOIN INVOICE_MASTER i ON d.DRIVERCODE = i.DRIVER_REC
                    AND YEAR(i.INVDATE) = {year} AND MONTH(i.INVDATE) = {month}
                GROUP BY d.DRIVERCODE, d.NAME, d.TEL
                HAVING invoice_count > 0
                ORDER BY total_amount DESC
            """)
            data = self.app.cursor.fetchall()
            
            filename = f"{summary_dir}/司机统计_{year}{month:02d}.csv"
            
            import csv
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                if data:
                    headers = list(data[0].keys()) if isinstance(data[0], dict) else []
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(data)
            
            self.status_label.text = f"导出完成\n保存位置: {filename}"
        except Exception as e:
            self.status_label.text = f"导出失败: {e}"