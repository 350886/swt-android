#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Settings Screen UI - Complete implementation
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.clock import Clock
import threading


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.connection_result = (False, "")
        Clock.schedule_once(self._init_ui)
    
    def _init_ui(self, dt):
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='[b]数据库连接设置[/b]', markup=True, size_hint_y=None, height=40))
        
        form_grid = GridLayout(cols=2, size_hint_y=None, height=200, spacing=8)
        
        form_grid.add_widget(Label(text='服务器地址:', size_hint_x=None, width=100))
        self.host_input = TextInput(text=self.app.config.get('db_host', '192.168.0.120'), multiline=False)
        form_grid.add_widget(self.host_input)
        
        form_grid.add_widget(Label(text='端口:', size_hint_x=None, width=100))
        self.port_input = TextInput(text=self.app.config.get('db_port', '3306'), multiline=False)
        form_grid.add_widget(self.port_input)
        
        form_grid.add_widget(Label(text='用户名:', size_hint_x=None, width=100))
        self.user_input = TextInput(text=self.app.config.get('db_user', 'mysql'), multiline=False)
        form_grid.add_widget(self.user_input)
        
        form_grid.add_widget(Label(text='密码:', size_hint_x=None, width=100))
        self.password_input = TextInput(text=self.app.config.get('db_password', 'mysql'), multiline=False, password=True)
        form_grid.add_widget(self.password_input)
        
        form_grid.add_widget(Label(text='数据库名:', size_hint_x=None, width=100))
        self.dbname_input = TextInput(text=self.app.config.get('db_name', 'SWT'), multiline=False)
        form_grid.add_widget(self.dbname_input)
        
        layout.add_widget(form_grid)
        
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        test_btn = Button(text='测试连接', background_color=[0.1, 0.56, 1, 1])
        test_btn.bind(on_press=self.test_connection)
        btn_box.add_widget(test_btn)
        
        save_btn = Button(text='保存设置', background_color=[0.32, 0.77, 0.1, 1])
        save_btn.bind(on_press=self.save_settings)
        btn_box.add_widget(save_btn)
        
        layout.add_widget(btn_box)
        
        self.status_label = Label(text='请配置数据库连接信息', size_hint_y=None, height=60, text_size=(None, None), halign='left')
        layout.add_widget(self.status_label)
        
        layout.add_widget(Label(text='[b]导出目录设置[/b]', markup=True, size_hint_y=None, height=40))
        
        dir_grid = GridLayout(cols=2, size_hint_y=None, height=100, spacing=8)
        
        dir_grid.add_widget(Label(text='客户月结单:', size_hint_x=None, width=100))
        self.export_dir_input = TextInput(text=self.app.config.get('export_dir', '/storage/emulated/0/Download/SWT'), multiline=False)
        dir_grid.add_widget(self.export_dir_input)
        
        dir_grid.add_widget(Label(text='汇总表目录:', size_hint_x=None, width=100))
        self.summary_dir_input = TextInput(text=self.app.config.get('summary_dir', '/storage/emulated/0/Download/SWT'), multiline=False)
        dir_grid.add_widget(self.summary_dir_input)
        
        layout.add_widget(dir_grid)
        
        layout.add_widget(Label(text='[b]关于[/b]', markup=True, size_hint_y=None, height=40))
        
        about_label = Label(text='SWT 货运管理系统 v1.0\n适用于 Android 设备', size_hint_y=None, height=60, text_size=(None, None), halign='left')
        layout.add_widget(about_label)
        
        self.add_widget(layout)
    
    def test_connection(self, instance):
        self.status_label.text = "正在测试连接..."
        
        host = self.host_input.text.strip()
        port = self.port_input.text.strip()
        user = self.user_input.text.strip()
        password = self.password_input.text.strip()
        db_name = self.dbname_input.text.strip()
        
        def run_test():
            self.connection_result = self.app.test_db_connection(host, port, user, password, db_name)
        
        thread = threading.Thread(target=run_test)
        thread.start()
        thread.join()
        
        success, message = self.connection_result
        if success:
            self.status_label.text = f"✅ {message}"
        else:
            self.status_label.text = f"❌ 连接失败: {message}"
    
    def save_settings(self, instance):
        self.status_label.text = "正在保存..."
        
        host = self.host_input.text.strip()
        port = self.port_input.text.strip()
        user = self.user_input.text.strip()
        password = self.password_input.text.strip()
        db_name = self.dbname_input.text.strip()
        export_dir = self.export_dir_input.text.strip()
        summary_dir = self.summary_dir_input.text.strip()
        
        success, message = self.test_connection(instance)
        
        if not success:
            self.status_label.text = f"❌ 保存失败: {message}"
            return
        
        try:
            self.app.config['db_host'] = host
            self.app.config['db_port'] = port
            self.app.config['db_user'] = user
            self.app.config['db_password'] = password
            self.app.config['db_name'] = db_name
            self.app.config['export_dir'] = export_dir
            self.app.config['summary_dir'] = summary_dir
            
            self.app.save_config()
            
            self.app.reconnect_db()
            
            self.status_label.text = "✅ 设置已保存并重新连接数据库"
        except Exception as e:
            self.status_label.text = f"❌ 保存失败: {e}"