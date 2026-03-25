#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Keyword Check Screen UI - Complete implementation
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
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.app import App
from kivy.clock import Clock


class KeywordScreen(Screen):
    rules = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        Clock.schedule_once(self._init_ui)
    
    def _init_ui(self, dt):
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='[b]检测关键字[/b]', markup=True, size_hint_y=None, height=40))
        
        date_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        date_box.add_widget(Label(text='年月:', size_hint_x=None, width=50))
        
        year_spin = Spinner(text='2026', values=[str(y) for y in range(2020, 2031)], size_hint_x=None, width=80)
        month_spin = Spinner(text='03', values=[f'{m:02d}' for m in range(1, 13)], size_hint_x=None, width=60)
        
        date_box.add_widget(year_spin)
        date_box.add_widget(Label(text='年', size_hint_x=None, width=30))
        date_box.add_widget(month_spin)
        date_box.add_widget(Label(text='月', size_hint_x=None, width=30))
        
        check_btn = Button(text='开始检查', background_color=[0.1, 0.56, 1, 1], size_hint_x=None, width=100)
        check_btn.bind(on_press=lambda x: self.run_check(year_spin.text, month_spin.text))
        date_box.add_widget(check_btn)
        
        layout.add_widget(date_box)
        
        self.result_label = Label(text='点击"开始检查"按钮', size_hint_y=None, height=100, text_size=(None, None), halign='left')
        layout.add_widget(self.result_label)
        
        layout.add_widget(Label(text='[b]规则列表[/b]', markup=True, size_hint_y=None, height=40))
        
        rules_btn = Button(text='加载规则', background_color=[0.2, 0.6, 0.2, 1], size_hint_y=None, height=40)
        rules_btn.bind(on_press=lambda x: self.load_rules())
        layout.add_widget(rules_btn)
        
        self.rules_label = Label(text='暂无规则', size_hint_y=None, height=60)
        layout.add_widget(self.rules_label)
        
        form_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.keyword_input = TextInput(hint_text='关键字', size_hint_x=0.4, multiline=False)
        self.replacement_input = TextInput(hint_text='替换值', size_hint_x=0.4, multiline=False)
        
        form_box.add_widget(self.keyword_input)
        form_box.add_widget(self.replacement_input)
        
        add_btn = Button(text='添加', background_color=[0.3, 0.8, 0.3, 1], size_hint_x=None, width=60)
        add_btn.bind(on_press=lambda x: self.add_rule())
        form_box.add_widget(add_btn)
        
        layout.add_widget(form_box)
        
        self.add_widget(layout)
    
    def run_check(self, year, month):
        if not self.app.cursor:
            self.result_label.text = "错误: 数据库未连接"
            return
        
        try:
            self.app.cursor.execute(f"""
                CALL check_unmatched_misc_names({year}, {int(month)})
            """)
            result = self.app.cursor.fetchall()
            
            if result:
                self.result_label.text = f"检查完成，发现 {len(result)} 条未匹配记录"
            else:
                self.result_label.text = "检查完成，所有记录已匹配"
        except Exception as e:
            self.result_label.text = f"检查失败: {e}"
    
    def load_rules(self):
        if not self.app.cursor:
            self.rules_label.text = "错误: 数据库未连接"
            return
        
        try:
            self.app.cursor.execute("""
                SELECT keyword, replacement FROM misc_name_rules ORDER BY sort_order
            """)
            rules = self.app.cursor.fetchall()
            
            if rules:
                text = ""
                for r in rules[:10]:
                    text += f"• {r['keyword']} → {r['replacement']}\n"
                self.rules_label.text = text
            else:
                self.rules_label.text = "暂无规则"
        except Exception as e:
            self.rules_label.text = f"加载失败: {e}"
    
    def add_rule(self):
        keyword = self.keyword_input.text.strip()
        replacement = self.replacement_input.text.strip()
        
        if not keyword or not replacement:
            return
        
        if not self.app.cursor:
            return
        
        try:
            self.app.cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM misc_name_rules")
            sort_order = self.app.cursor.fetchone()[0]
            
            self.app.cursor.execute("""
                INSERT INTO misc_name_rules (sort_order, pattern_type, keyword, replacement, memo)
                VALUES (%s, 'prefix', %s, %s, NULL)
            """, (sort_order, keyword, replacement))
            self.app.conn.commit()
            
            self.keyword_input.text = ''
            self.replacement_input.text = ''
            self.load_rules()
        except Exception as e:
            print(f"Add rule failed: {e}")