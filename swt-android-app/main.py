#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SWT 货运管理系统 - Kivy Android 版本
完整的移动端 UI 实现
"""
import kivy
kivy.require('2.2.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock

import os
import json
import threading
import datetime


try:
    import pymysql
    from dbutils.pooled_db import PooledDB
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


KV = """
<NavButton>:
    size_hint_y: None
    height: '50dp'
    background_color: 0.15, 0.15, 0.15, 1
    color: 0.7, 0.7, 0.7, 1

<NavButtonSelected>:
    size_hint_y: None
    height: '50dp'
    background_color: 0.1, 0.56, 1, 1
    color: 1, 1, 1, 1

<Card>:
    background_color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size

<SectionTitle>:
    size_hint_y: None
    height: '40dp'
    font_size: '16sp'
    bold: True
    color: 0.15, 0.15, 0.15, 1

<SWTApp>:
    orientation: 'vertical'
    
    # Header
    BoxLayout:
        size_hint_y: None
        height: '56dp'
        padding: 15, 0
        canvas:
            Color:
                rgba: 0.96, 0.96, 0.96, 1
            Rectangle:
                size: self.size
        
        Label:
            id: header_title
            text: "SWT 货运系统"
            font_size: '20sp'
            bold: True
            color: 0.1, 0.1, 0.1, 1
    
    # Main Content
    BoxLayout:
        orientation: 'horizontal'
        
        # Navigation Sidebar
        BoxLayout:
            size_hint_x: None
            width: '80dp'
            orientation: 'vertical'
            padding: 5
            spacing: 3
            canvas:
                Color:
                    rgba: 0.08, 0.1, 0.12, 1
                Rectangle:
                    size: self.size
            
            NavButton:
                id: btn_keyword
                text: "检测"
                on_press: root.switch_screen('keyword')
            
            NavButton:
                id: btn_customer
                text: "客户"
                on_press: root.switch_screen('customer')
            
            NavButton:
                id: btn_driver
                text: "司机"
                on_press: root.switch_screen('driver')
            
            NavButton:
                id: btn_stats
                text: "统计"
                on_press: root.switch_screen('stats')
            
            Widget:
            
            NavButton:
                id: btn_settings
                text: "设置"
                on_press: root.switch_screen('settings')
        
        # Screen Container
        ScreenManager:
            id: sm
            transition: NoTransition()
            
            Screen:
                name: 'keyword'
                KeywordScreen:
            
            Screen:
                name: 'customer'
                CustomerScreen:
            
            Screen:
                name: 'driver'
                DriverScreen:
            
            Screen:
                name: 'stats'
                StatsScreen:
            
            Screen:
                name: 'settings'
                SettingsScreen:
"""


class NavButton(Button):
    pass


class NavButtonSelected(Button):
    pass


class Card(BoxLayout):
    pass


class SectionTitle(Label):
    pass


class KeywordScreen(Screen):
    pass


class CustomerScreen(Screen):
    pass


class DriverScreen(Screen):
    pass


class StatsScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class SWTApp(App):
    title = "SWT 货运系统"
    current_screen = StringProperty('keyword')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = self.load_config()
        self.db_pool = None
        self.conn = None
        self.cursor = None
        
        if DB_AVAILABLE:
            Clock.schedule_once(lambda dt: self.init_db(), 1)
    
    def load_config(self):
        default_config = {
            'db_host': '192.168.0.120',
            'db_port': '3306',
            'db_user': 'mysql',
            'db_password': 'mysql',
            'db_name': 'SWT',
            'export_dir': '/storage/emulated/0/Download/SWT',
            'summary_dir': '/storage/emulated/0/Download/SWT'
        }
        
        for key in ['db_host', 'db_port', 'db_user', 'db_password', 'db_name', 'export_dir', 'summary_dir']:
            if key not in default_config:
                default_config[key] = ''
        
        config_file = 'swt_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    for k, v in default_config.items():
                        if k not in loaded:
                            loaded[k] = v
                    return loaded
            except:
                pass
        return default_config
    
    def save_config(self):
        try:
            with open('swt_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Save config failed: {e}")
    
    def init_db(self):
        if not DB_AVAILABLE:
            print("pymysql not available")
            return
            
        try:
            self.db_pool = PooledDB(
                creator=pymysql,
                maxconnections=10,
                mincached=2,
                maxcached=5,
                blocking=True,
                ping=1,
                host=self.config.get('db_host', '192.168.0.120'),
                port=int(self.config.get('db_port', 3306)),
                user=self.config.get('db_user', 'mysql'),
                password=self.config.get('db_password', 'mysql'),
                database=self.config.get('db_name', 'SWT'),
                charset='utf8mb4'
            )
            self.conn = self.db_pool.connection()
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            print("Database connected successfully")
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.db_pool = None
    
    def reconnect_db(self):
        """Reconnect to database"""
        try:
            if self.conn:
                self.conn.close()
        except:
            pass
        
        self.init_db()
    
    def test_db_connection(self, host, port, user, password, db_name):
        """Test database connection"""
        if not DB_AVAILABLE:
            return False, "pymysql 未安装"
            
        try:
            test_conn = pymysql.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=db_name,
                charset='utf8mb4',
                connect_timeout=5
            )
            test_conn.close()
            return True, "连接成功"
        except Exception as e:
            return False, str(e)
    
    def switch_screen(self, screen_name):
        """Switch screen and update nav"""
        self.current_screen = screen_name
        
        sm = self.root.ids.sm
        sm.current = screen_name
        
        titles = {
            'keyword': '检测关键字',
            'customer': '客户管理',
            'driver': '司机管理',
            'stats': '公司统计',
            'settings': '系统设置'
        }
        self.root.ids.header_title.text = titles.get(screen_name, 'SWT 货运系统')
        
        for btn_id in ['btn_keyword', 'btn_customer', 'btn_driver', 'btn_stats', 'btn_settings']:
            btn = self.root.ids.get(btn_id)
            if btn:
                btn.background_color = [0.15, 0.15, 0.15, 1]
                btn.color = [0.7, 0.7, 0.7, 1]
        
        active_btn = self.root.ids.get(f'btn_{screen_name}')
        if active_btn:
            active_btn.background_color = [0.1, 0.56, 1, 1]
            active_btn.color = [1, 1, 1, 1]
    
    def build(self):
        Window.size = (360, 800)
        return Builder.load_string(KV)


if __name__ == '__main__':
    SWTApp().run()