#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Statistics Screen UI - Complete implementation
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
import os


class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.stats_data = {}
        Clock.schedule_once(self._init_ui)
    
    def _init_ui(self, dt):
        self.build_ui()
        self.load_stats()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='[b]公司统计概览[/b]', markup=True, size_hint_y=None, height=40))
        
        stats_grid = GridLayout(cols=2, size_hint_y=None, height=120, spacing=5)
        
        self.total_customers_label = Label(text='客户数: 0', color=[0.1, 0.56, 1, 1])
        self.total_drivers_label = Label(text='司机数: 0', color=[0.32, 0.77, 0.1, 1])
        self.total_invoices_label = Label(text='总发票: 0', color=[0.98, 0.68, 0.08, 1])
        self.monthly_invoices_label = Label(text='本月发票: 0', color=[0.96, 0.27, 0.18, 1])
        
        stats_grid.add_widget(self.total_customers_label)
        stats_grid.add_widget(self.total_drivers_label)
        stats_grid.add_widget(self.total_invoices_label)
        stats_grid.add_widget(self.monthly_invoices_label)
        
        layout.add_widget(stats_grid)
        
        layout.add_widget(Label(text='[b]客户月度汇总导出[/b]', markup=True, size_hint_y=None, height=40))
        
        date_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        date_box.add_widget(Label(text='年月:', size_hint_x=None, width=50))
        
        self.year_spin = Spinner(text='2026', values=[str(y) for y in range(2020, 2031)], size_hint_x=None, width=80)
        self.month_spin = Spinner(text='03', values=[f'{m:02d}' for m in range(1, 13)], size_hint_x=None, width=60)
        
        date_box.add_widget(self.year_spin)
        date_box.add_widget(Label(text='年', size_hint_x=None, width=30))
        date_box.add_widget(self.month_spin)
        date_box.add_widget(Label(text='月', size_hint_x=None, width=30))
        
        layout.add_widget(date_box)
        
        export_customer_btn = Button(text='导出客户汇总', background_color=[0.1, 0.56, 1, 1], size_hint_y=None, height=45)
        export_customer_btn.bind(on_press=self.export_customer_summary)
        layout.add_widget(export_customer_btn)
        
        layout.add_widget(Label(text='[b]司机月度统计导出[/b]', markup=True, size_hint_y=None, height=40))
        
        export_driver_btn = Button(text='导出司机统计', background_color=[0.32, 0.77, 0.1, 1], size_hint_y=None, height=45)
        export_driver_btn.bind(on_press=self.export_driver_stats)
        layout.add_widget(export_driver_btn)
        
        self.status_label = Label(text='', size_hint_y=None, height=80, text_size=(None, None), halign='left')
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def load_stats(self):
        if not self.app.cursor:
            return
        
        try:
            self.app.cursor.execute("SELECT COUNT(*) as cnt FROM CUST_MASTER")
            result = self.app.cursor.fetchone()
            self.stats_data['total_customers'] = result[0] if result else 0
            self.total_customers_label.text = f"客户数: {self.stats_data['total_customers']}"
            
            self.app.cursor.execute("SELECT COUNT(*) as cnt FROM DRIVER_MASTER")
            result = self.app.cursor.fetchone()
            self.stats_data['total_drivers'] = result[0] if result else 0
            self.total_drivers_label.text = f"司机数: {self.stats_data['total_drivers']}"
            
            self.app.cursor.execute("SELECT COUNT(*) as cnt FROM INVOICE_MASTER")
            result = self.app.cursor.fetchone()
            self.stats_data['total_invoices'] = result[0] if result else 0
            self.total_invoices_label.text = f"总发票: {self.stats_data['total_invoices']}"
            
            self.app.cursor.execute("""
                SELECT COUNT(*) FROM INVOICE_MASTER 
                WHERE YEAR(INVDATE) = YEAR(CURDATE()) AND MONTH(INVDATE) = MONTH(CURDATE())
            """)
            result = self.app.cursor.fetchone()
            self.stats_data['monthly_invoices'] = result[0] if result else 0
            self.monthly_invoices_label.text = f"本月发票: {self.stats_data['monthly_invoices']}"
            
        except Exception as e:
            print(f"Load stats failed: {e}")
    
    def export_customer_summary(self, instance):
        year = int(self.year_spin.text)
        month = int(self.month_spin.text)
        
        if not self.app.cursor:
            self.status_label.text = "错误: 数据库未连接"
            return
        
        try:
            summary_dir = self.app.config.get('summary_dir', '/storage/emulated/0/Download/SWT')
            os.makedirs(summary_dir, exist_ok=True)
            
            self.app.cursor.execute(f"""
                SELECT 
                    c.CUSTCODE as 客户编码,
                    c.NAME as 客户名称,
                    COUNT(i.INVOICECODE) as 发票数,
                    COALESCE(SUM(i.TOTAMT), 0) as 总金额,
                    COALESCE(SUM(i.BAL), 0) as 应收金额
                FROM CUST_MASTER c
                LEFT JOIN INVOICE_MASTER i ON c.CUSTCODE = i.CUSTCODE 
                    AND YEAR(i.INVDATE) = {year} AND MONTH(i.INVDATE) = {month}
                GROUP BY c.CUSTCODE, c.NAME
                HAVING 发票数 > 0
                ORDER BY 总金额 DESC
            """)
            data = self.app.cursor.fetchall()
            
            filename = f"{summary_dir}/客户月度汇总_{year}{month:02d}.csv"
            
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
    
    def export_driver_stats(self, instance):
        year = int(self.year_spin.text)
        month = int(self.month_spin.text)
        
        if not self.app.cursor:
            self.status_label.text = "错误: 数据库未连接"
            return
        
        try:
            summary_dir = self.app.config.get('summary_dir', '/storage/emulated/0/Download/SWT')
            os.makedirs(summary_dir, exist_ok=True)
            
            self.app.cursor.execute(f"""
                SELECT 
                    d.DRIVERCODE as 司机编码,
                    d.NAME as 司机名称,
                    COUNT(i.INVOICECODE) as 发票数,
                    COALESCE(SUM(i.TOTAMT), 0) as 营业额,
                    COALESCE(SUM(i.DRIVER_FEE), 0) as 司机费用
                FROM DRIVER_MASTER d
                LEFT JOIN INVOICE_MASTER i ON d.DRIVERCODE = i.DRIVER_REC
                    AND YEAR(i.INVDATE) = {year} AND MONTH(i.INVDATE) = {month}
                GROUP BY d.DRIVERCODE, d.NAME
                HAVING 发票数 > 0
                ORDER BY 营业额 DESC
            """)
            data = self.app.cursor.fetchall()
            
            filename = f"{summary_dir}/司机月度统计_{year}{month:02d}.csv"
            
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