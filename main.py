
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from datetime import date, datetime
import json
import os

# ===== ФОН =====
Window.clearcolor = (0.85, 0.92, 1, 1)

# ===== ШРИФТ =====
FONT = None
if os.path.exists("NotoEmoji-Regular.ttf"):
    try:
        LabelBase.register(name="Emoji", fn_regular="NotoEmoji-Regular.ttf")
        FONT = "Emoji"
    except:
        FONT = None

def make_label(text, **kwargs):
    if FONT:
        kwargs["font_name"] = FONT
    kwargs.setdefault("color", (0, 0, 0, 1))
    return Label(text=text, **kwargs)

def make_label_white(text, **kwargs):
    if FONT:
        kwargs["font_name"] = FONT
    kwargs["color"] = (1, 1, 1, 1)
    return Label(text=text, **kwargs)

# ===== ФАЙЛЫ =====
SAVE_FILE = "save.json"
TASKS_FILE = "tasks.json"

def today():
    return str(date.today())

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_save():
    return load_json(SAVE_FILE, {
        "streak_simple": 0,
        "streak_pro": 0,
        "last_day": "",
        "last_reward_day": "",
        "pro_reward_day": "",
        "sick_day": "",
        "background": 0,
        "multiplier_level": 0,
        "aquarium_level": 0,
        "last_aquarium_time": "",
        "fish": {"common": 0, "rare": 0, "epic": 0, "legend": 0}
    })

def load_tasks():
    return load_json(TASKS_FILE, {})

# ===== ЧЕКБОКС =====
class ColorCheckBox(Widget):
    def __init__(self, checked=False, on_toggle=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_x = 0.15
        self.checked = checked
        self.on_toggle = on_toggle
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *a):
        self.canvas.clear()
        with self.canvas:
            if self.checked:
                Color(0.2, 0.7, 1, 1)
            else:
                Color(0.75, 0.75, 0.75, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

            if self.checked:
                Color(1, 1, 1, 1)
                cx, cy = self.center_x, self.center_y
                w, h = self.width, self.height
                Line(points=[
                    cx - w * 0.20, cy,
                    cx - w * 0.05, cy - h * 0.15,
                    cx + w * 0.20, cy + h * 0.18
                ], width=2.5, cap="round", joint="round")

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.checked = not self.checked
            self.redraw()
            if self.on_toggle:
                self.on_toggle(self.checked)
            return True
        return super().on_touch_down(touch)

# ===== ЭКРАН =====
class CatApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=15, spacing=10, **kwargs)
        self.save = load_save()
        self.tasks_all = load_tasks()
        self.today = today()

        self.fish_labels = {}
        self._last_popup = None
        self.aquarium_row = None
        self.aquarium_label = None

        self.apply_background()
        self.grow_simple_streak()

        # ===== КОТ =====
        self.cat = Image(
            source="cat.jpg",
            size_hint=(1, 0.45),
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={"center_x": 0.5}


            )
        self.add_widget(self.cat)
        self.animate_cat()

        # ===== ИНФО =====
        self.info = make_label(
            text=self.get_info_text(),
            size_hint=(1, 0.08),
            font_size="16sp",
            halign="center",
            valign="middle"
        )
        self.info.bind(size=self.info.setter("text_size"))
        self.add_widget(self.info)

        # ===== РЫБКИ + КНОПКИ =====
        fish_line = BoxLayout(orientation="horizontal", size_hint=(1, 0.14), spacing=5)

        fish_row = BoxLayout(orientation="horizontal", size_hint=(0.6, 1), spacing=5)
        fish_row.add_widget(self.make_fish_widget("fish_common.png", "common"))
        fish_row.add_widget(self.make_fish_widget("fish_rare.png", "rare"))
        fish_row.add_widget(self.make_fish_widget("fish_epic.png", "epic"))
        fish_row.add_widget(self.make_fish_widget("fish_legend.png", "legend"))
        fish_line.add_widget(fish_row)

        self.exchange_btn = Button(
            text="Обмен",
            size_hint=(0.15, None),
            height=dp(50),
            pos_hint={"center_y": 0.5},
            font_size="13sp",
            background_normal="",
            background_down="",
            background_color=(0.3, 0.7, 1, 1),
            color=(1, 1, 1, 1)
        )
        self.exchange_btn.bind(on_press=self.open_exchange)
        fish_line.add_widget(self.exchange_btn)

        self.shop_btn = Button(
            text="Магазин",
            size_hint=(0.25, None),
            height=dp(50),
            pos_hint={"center_y": 0.5},
            font_size="13sp",
            background_normal="",
            background_down="",
            background_color=(0.5, 0.3, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        self.shop_btn.bind(on_press=self.open_shop)
        fish_line.add_widget(self.shop_btn)

        self.add_widget(fish_line)

        # ===== ЗАДАНИЯ + АКВАРИУМ =====
        self.scroll = ScrollView(size_hint=(1, 0.33))
        self.task_box = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.task_box.bind(minimum_height=self.task_box.setter("height"))
        self.scroll.add_widget(self.task_box)
        self.add_widget(self.scroll)

        self.load_today_tasks()

    # ===== ФОН =====
    def apply_background(self):
        bg_id = self.save.get("background", 0)
        colors = {
            0: (0.85, 0.92, 1, 1),
            1: (1.0, 0.8, 0.6, 1),
            2: (0.1, 0.1, 0.2, 1),
            3: (0.4, 0.8, 0.5, 1),
            4: (0.1, 0.05, 0.3, 1),
            5: (0.2, 0.5, 0.8, 1),
            6: (0.6, 0.4, 0.9, 1),
            7: (1.0, 0.4, 0.2, 1),
            8: (0.3, 0.1, 0.5, 1),
            9: (0.9, 0.7, 0.2, 1),
        }
        Window.clearcolor = colors.get(bg_id, colors[0])

    # ===== БОЛЕЗНЬ =====
    def sick_day(self, *args):
        if self.save.get("sick_day") == self.today:
            self.show_float_text("!")
            return

        content = BoxLayout(orientation="vertical", padding=15, spacing=15)
        content.add_widget(make_label_white(
            text="Уверены?\n\nЗадания не будут считаться,\nрыбки не дадут,\nстрик сохранится.",
            size_hint=(1, 0.7),
            font_size="16sp",
            halign="center",
            valign="middle"
        ))

        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, 0.3), spacing=10)

        btn_yes = Button(
            text="Да",
            background_normal="",
            background_down="",
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size="18sp"
        )
        btn_no = Button(
            text="Нет",
            background_normal="",
            background_down="",
            background_color=(0.3, 0.7, 1, 1),
            color=(1, 1, 1, 1),
            font_size="18sp"
        )

        btn_row.add_widget(btn_no)
        btn_row.add_widget(btn_yes)
        content.add_widget(btn_row)

        popup = Popup(


            title="Болезнь",
            title_color=(1, 1, 1, 1),
            content=content,
            size_hint=(0.85, 0.45),
            auto_dismiss=False,
            background_color=(0.15, 0.15, 0.2, 1)
        )

        def do_sick(*a):
            day_tasks = self.tasks_all.get(self.today, [])
            for task in day_tasks:
                task["done"] = False
                task["rewarded"] = True

            save_json(TASKS_FILE, self.tasks_all)

            self.save["sick_day"] = self.today
            self.save["last_day"] = self.today

            save_json(SAVE_FILE, self.save)

            popup.dismiss()
            self.load_today_tasks()
            self.show_popup(
                title="Болезнь",
                text="Стрик сохранён.\nВыздоравливай!",
                on_take=lambda: None
            )

        def do_no(*a):
            popup.dismiss()

        btn_yes.bind(on_press=do_sick)
        btn_no.bind(on_press=do_no)

        self.close_last_popup()
        self._last_popup = popup
        popup.open()

    # ===== АКВАРИУМ =====
    def get_aquarium_price(self, level):
        prices = [
            ("common", 100),
            ("common", 300),
            ("rare", 18),
            ("epic", 1),
            ("epic", 3),
            ("epic", 9),
            ("epic", 27),
            ("legend", 1),
        ]
        if level >= len(prices):
            return None, None
        return prices[level]

    def get_aquarium_rate(self, level):
        rates = [
            ("common", 1),
            ("common", 3),
            ("rare", 1),
            ("rare", 3),
            ("epic", 1),
            ("epic", 3),
            ("legend", 1),
            ("legend", 3),
        ]
        if level == 0 or level > len(rates):
            return None, 0
        return rates[level - 1]

    def collect_aquarium(self, *args):
        lvl = self.save.get("aquarium_level", 0)

        if lvl == 0:
            self.show_float_text("!")
            return

        last_time = self.save.get("last_aquarium_time", "")

        if last_time == "":
            self.save["last_aquarium_time"] = datetime.now().isoformat()
            save_json(SAVE_FILE, self.save)
            return

        try:
            last = datetime.fromisoformat(last_time)
            now = datetime.now()
            hours = (now - last).total_seconds() / 3600

            cur, rate = self.get_aquarium_rate(lvl)
            earned = int(hours * rate)

            if earned > 0:
                self.save["fish"][cur] += earned
                self.save["last_aquarium_time"] = now.isoformat()
                save_json(SAVE_FILE, self.save)
                self.refresh_fish()
                self.info.text = self.get_info_text()

                cur_name = {"common": "обычных", "rare": "редких",
                            "epic": "эпик", "legend": "легенд"}[cur]
                self.show_popup(
                    title="Аквариум",
                    text=f"+{earned} {cur_name}",
                    on_take=lambda: None
                )
            else:
                self.show_float_text("0")
        except:
            self.save["last_aquarium_time"] = datetime.now().isoformat()
            save_json(SAVE_FILE, self.save)

    def buy_aquarium(self, *args):
        lvl = self.save.get("aquarium_level", 0)
        cur, price = self.get_aquarium_price(lvl)

        if cur is None:
            self.show_float_text("MAX")
            return

        if self.save["fish"][cur] >= price:
            self.save["fish"][cur] -= price
            self.save["aquarium_level"] = lvl + 1
            self.save["last_aquarium_time"] = datetime.now().isoformat()
            save_json(SAVE_FILE, self.save)
            self.refresh_fish()
            self.info.text = self.get_info_text()
            self.close_last_popup()
            self.load_today_tasks()
            self.show_popup(
                title="Аквариум!",


                text=f"Уровень {lvl + 1}",
                on_take=lambda: None
            )
        else:
            self.show_float_text("!")

    def make_aquarium_widget(self):
        self.aquarium_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(80),
            spacing=5
        )

        self.aquarium_row.add_widget(Image(
            source="aquarium.png" if os.path.exists("aquarium.png") else "",
            size_hint=(0.3, 1),
            allow_stretch=True,
            keep_ratio=True
        ))

        self.aquarium_label = make_label(
            text="",
            size_hint=(0.4, 1),
            font_size="12sp",
            halign="center",
            valign="middle"
        )
        self.aquarium_label.bind(size=self.aquarium_label.setter("text_size"))
        self.aquarium_row.add_widget(self.aquarium_label)

        btn = Button(
            text="Забрать",
            size_hint=(0.3, 1),
            background_normal="",
            background_down="",
            background_color=(0.2, 0.8, 0.6, 1),
            color=(1, 1, 1, 1),
            font_size="14sp"
        )
        btn.bind(on_press=self.collect_aquarium)
        self.aquarium_row.add_widget(btn)

        self.refresh_aquarium()
        return self.aquarium_row

    def refresh_aquarium(self):
        if self.aquarium_label is None:
            return

        lvl = self.save.get("aquarium_level", 0)
        if lvl == 0:
            text = "Аквариум: не куплен"
        else:
            cur, rate = self.get_aquarium_rate(lvl)
            cur_name = {"common": "обычных", "rare": "редких",
                        "epic": "эпик", "legend": "легенд"}[cur]
            text = f"Аквариум ур.{lvl}\n+{rate} {cur_name}/час"

        self.aquarium_label.text = text

    # ===== МНОЖИТЕЛЬ =====
    def get_multiplier_price(self, level):
        base = 10 * (3 ** level)

        currencies = ["common", "rare", "epic", "legend"]
        currency_idx = 0
        price = base

        while price > 50 and currency_idx < 3:
            price = (price // 50) * 2
            currency_idx += 1

        return currencies[currency_idx], price

    def get_multiplier(self):
        return 2 ** self.save.get("multiplier_level", 0)

    def buy_multiplier(self, *args):
        lvl = self.save.get("multiplier_level", 0)
        if lvl >= 10:
            return

        cur, price = self.get_multiplier_price(lvl)

        if self.save["fish"][cur] >= price:
            self.save["fish"][cur] -= price
            self.save["multiplier_level"] = lvl + 1
            save_json(SAVE_FILE, self.save)
            self.refresh_fish()
            self.close_last_popup()
            self.open_shop()
        else:
            self.show_float_text("!")

    # ===== ПОПАПЫ =====
    def close_last_popup(self):
        if self._last_popup:
            try:
                self._last_popup.dismiss()
            except:
                pass
            self._last_popup = None

    def open_shop(self, *args):
        self.close_last_popup()

        content = BoxLayout(orientation="vertical", padding=10, spacing=6)
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, size_hint_y=None, spacing=6)
        grid.bind(minimum_height=grid.setter("height"))

        # ФОНЫ
        grid.add_widget(make_label_white(
            text="=== ФОНЫ ===",
            size_hint_y=None, height=30,
            font_size="16sp", bold=True
        ))

        backgrounds = [
            (0, "Синий",     "50 обычных"),
            (1, "Закат",     "200 обычных"),
            (2, "Ночь",      "500 обычных"),
            (3, "Лес",       "2 редких"),
            (4, "Космос",    "5 редких"),
            (5, "Вода",      "15 редких"),
            (6, "Аврора",    "3 эпик"),
            (7, "Огонь",     "10 эпик"),
            (8, "Галактика", "1 легенд"),
            (9, "Легенда",   "3 легенд"),
        ]


        for bg_id, name, price in backgrounds:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=5)
            row.add_widget(make_label_white(
                text=f"{name} — {price}",
                size_hint=(0.7, 1),
                font_size="16sp"
            ))
            btn = Button(
                text="Купить",
                size_hint=(0.3, 1),
                background_normal="",
                background_down="",
                background_color=(0.3, 0.7, 1, 1),
                color=(1, 1, 1, 1),
                font_size="14sp"
            )
            btn.bind(on_press=lambda *a, b=bg_id: self.buy_background(b))
            row.add_widget(btn)
            grid.add_widget(row)

        # МНОЖИТЕЛЬ
        grid.add_widget(make_label_white(
            text="=== МНОЖИТЕЛЬ ===",
            size_hint_y=None, height=30,
            font_size="16sp", bold=True
        ))

        lvl = self.save.get("multiplier_level", 0)

        if lvl < 10:
            cur, price = self.get_multiplier_price(lvl)
            next_mult = 2 ** (lvl + 1)
            cur_name = {"common": "обычных", "rare": "редких",
                        "epic": "эпик", "legend": "легенд"}[cur]

            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=60, spacing=5)
            row.add_widget(make_label_white(
                text=f"×{next_mult} — {price} {cur_name}",
                size_hint=(0.7, 1),
                font_size="16sp"
            ))
            btn = Button(
                text="Купить",
                size_hint=(0.3, 1),
                background_normal="",
                background_down="",
                background_color=(0.9, 0.6, 0.1, 1),
                color=(1, 1, 1, 1),
                font_size="14sp"
            )
            btn.bind(on_press=self.buy_multiplier)
            row.add_widget(btn)
            grid.add_widget(row)
        else:
            grid.add_widget(make_label_white(
                text="Множители: МАКС",
                size_hint_y=None, height=50,
                font_size="18sp", bold=True
            ))

        # АКВАРИУМ
        grid.add_widget(make_label_white(
            text="=== АКВАРИУМ ===",
            size_hint_y=None, height=30,
            font_size="16sp", bold=True
        ))

        aq_lvl = self.save.get("aquarium_level", 0)
        aq_cur, aq_price = self.get_aquarium_price(aq_lvl)

        if aq_cur is None:
            grid.add_widget(make_label_white(
                text="Аквариум: МАКС",
                size_hint_y=None, height=50,
                font_size="18sp", bold=True
            ))
        else:
            aq_cur_name = {"common": "обычных", "rare": "редких",
                           "epic": "эпик", "legend": "легенд"}[aq_cur]
            next_lvl = aq_lvl + 1

            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=60, spacing=5)
            row.add_widget(make_label_white(
                text=f"Аквариум ур.{next_lvl} — {aq_price} {aq_cur_name}",
                size_hint=(0.7, 1),
                font_size="14sp"
            ))
            btn = Button(
                text="Купить",
                size_hint=(0.3, 1),
                background_normal="",
                background_down="",
                background_color=(0.2, 0.8, 0.6, 1),
                color=(1, 1, 1, 1),
                font_size="14sp"
            )
            btn.bind(on_press=self.buy_aquarium)
            row.add_widget(btn)
            grid.add_widget(row)

        scroll.add_widget(grid)
        content.add_widget(scroll)

        popup = Popup(
            title="Магазин",
            title_color=(1, 1, 1, 1),
            content=content,
            size_hint=(0.9, 0.8),
            background_color=(0.15, 0.15, 0.2, 1)
        )
        self._last_popup = popup
        popup.open()

    def buy_background(self, bg_id):
        prices = {
            0: ("common", 50),


            1: ("common", 200),
            2: ("common", 500),
            3: ("rare", 2),
            4: ("rare", 5),
            5: ("rare", 15),
            6: ("epic", 3),
            7: ("epic", 10),
            8: ("legend", 1),
            9: ("legend", 3),
        }
        kind, price = prices[bg_id]

        if self.save["fish"][kind] >= price:
            self.save["fish"][kind] -= price
            self.save["background"] = bg_id
            save_json(SAVE_FILE, self.save)
            self.refresh_fish()
            self.apply_background()
            self.close_last_popup()
            self.show_popup("Куплено!", "Фон изменён", on_take=lambda: None)
        else:
            self.show_float_text("!")

    # ===== СТРИК =====
    def grow_simple_streak(self):
        # Болезнь — не трогаем
        if self.save.get("sick_day") == self.today:
            return

        last = self.save["last_day"]

        if last == "":
            self.save["streak_simple"] = 1
            self.save["last_day"] = self.today
            self.save["fish"]["common"] += 2
            save_json(SAVE_FILE, self.save)
            return

        if last == self.today:
            return

        try:
            last_date = datetime.strptime(last, "%Y-%m-%d").date()
            today_date = datetime.strptime(self.today, "%Y-%m-%d").date()

            if (today_date - last_date).days == 1:
                self.save["streak_simple"] += 1
                self.save["last_day"] = self.today
                s = self.save["streak_simple"]
                self.save["fish"]["common"] += 2 + (s // 3)
            else:
                self.save["streak_simple"] = 1
                self.save["streak_pro"] = 0
                self.save["last_day"] = self.today
                self.save["pro_reward_day"] = ""
                self.save["fish"]["common"] += 2

            save_json(SAVE_FILE, self.save)
        except:
            self.save["streak_simple"] = 1
            self.save["streak_pro"] = 0
            self.save["last_day"] = self.today
            save_json(SAVE_FILE, self.save)

    def animate_cat(self):
        left = Animation(pos_hint={"center_x": 0.4}, duration=2)
        right = Animation(pos_hint={"center_x": 0.6}, duration=2)
        left.bind(on_complete=lambda *a: right.start(self.cat))
        right.bind(on_complete=lambda *a: left.start(self.cat))
        left.start(self.cat)

    def make_fish_widget(self, img_file, key):
        box = BoxLayout(orientation="vertical", size_hint=(0.25, 1))
        box.add_widget(Image(
            source=img_file if os.path.exists(img_file) else "",
            size_hint=(1, 0.6),
            allow_stretch=True,
            keep_ratio=True
        ))
        lbl = make_label(
            text=str(self.save["fish"][key]),
            size_hint=(1, 0.4),
            font_size="14sp",
            halign="center"
        )
        lbl.bind(size=lbl.setter("text_size"))
        box.add_widget(lbl)
        self.fish_labels[key] = lbl
        return box

    def refresh_fish(self):
        for key, lbl in self.fish_labels.items():
            lbl.text = str(self.save["fish"][key])

    def get_info_text(self):
        mult = self.get_multiplier()
        mult_text = f" | ×{mult}" if mult > 1 else ""
        return (
            f"Стрик: {self.save['streak_simple']} | "
            f"Про: {self.save['streak_pro']}{mult_text}"
        )

    def load_today_tasks(self):
        self.task_box.clear_widgets()
        day_tasks = self.tasks_all.get(self.today, [])

        if not day_tasks:
            self.task_box.add_widget(make_label(
                text="Нет заданий на сегодня",
                size_hint_y=None, height=40
            ))
        else:
            done_count = sum(1 for t in day_tasks if t.get("done", False))
            total = len(day_tasks)

            self.task_box.add_widget(make_label(
                text=f"Сделано: {done_count}/{total}",
                size_hint_y=None, height=30


                ))

            for i, task in enumerate(day_tasks):
                if "rewarded" not in task:
                    task["rewarded"] = False
                if "done" not in task:
                    task["done"] = False

                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=45)
                row.add_widget(make_label(
                    text=f"{task['name']} — {task['count']}",
                    size_hint_x=0.75
                ))
                cb = ColorCheckBox(
                    checked=task["done"],
                    on_toggle=lambda val, idx=i: self.on_task(idx, val)
                )
                row.add_widget(cb)
                self.task_box.add_widget(row)

            save_json(TASKS_FILE, self.tasks_all)

        # Кнопка Болезнь
        sick_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=5)
        sick_btn = Button(
            text="Болезнь",
            background_normal="",
            background_down="",
            background_color=(0.9, 0.4, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size="14sp"
        )
        sick_btn.bind(on_press=self.sick_day)
        sick_row.add_widget(sick_btn)
        self.task_box.add_widget(sick_row)

        # Аквариум
        self.task_box.add_widget(self.make_aquarium_widget())

    def show_float_text(self, text, color=(1, 0.2, 0.2, 1)):
        lbl = make_label(
            text=text,
            size_hint=(None, None),
            size=(200, 100),
            font_size="48sp",
            color=color,
            bold=True,
            halign="center",
            valign="middle"
        )
        lbl.bind(size=lbl.setter("text_size"))

        popup = Popup(
            title="",
            title_size=0,
            separator_height=0,
            content=lbl,
            size_hint=(None, None),
            size=(200, 100),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            background_color=(0, 0, 0, 0),
            auto_dismiss=False
        )
        popup.open()

        anim = Animation(opacity=0, duration=0.9)
        anim.bind(on_complete=lambda *a: popup.dismiss())
        anim.start(lbl)

    def on_task(self, idx, value):
        task = self.tasks_all[self.today][idx]

        # Болезнь — не даём рыбки
        if self.save.get("sick_day") == self.today:
            task["done"] = value
            save_json(TASKS_FILE, self.tasks_all)
            self.load_today_tasks()
            return

        if value and not task.get("rewarded", False):
            mult = self.get_multiplier()
            self.save["fish"]["common"] += 1 * mult
            save_json(SAVE_FILE, self.save)
            self.refresh_fish()
            self.show_float_text(f"+{mult}", color=(0.1, 0.7, 0.2, 1))
            task["rewarded"] = True

        task["done"] = value
        save_json(TASKS_FILE, self.tasks_all)
        self.load_today_tasks()
        self.check_all_done()

    def check_all_done(self):
        # Болезнь — не трогаем
        if self.save.get("sick_day") == self.today:
            return

        day_tasks = self.tasks_all.get(self.today, [])
        if not day_tasks:
            return

        all_done = all(t.get("done", False) for t in day_tasks)

        if all_done and self.save.get("pro_reward_day") != self.today:
            self.save["pro_reward_day"] = self.today
            self.save["streak_pro"] += 1
            mult = self.get_multiplier()
            reward = (5 + (self.save["streak_pro"] // 2)) * mult

            self.show_popup(
                title="ВСЁ ВЫПОЛНЕНО!",
                text=f"Награда за все задания:\n\n+{reward} обычных",
                on_take=lambda: self.take_reward("common", reward)
            )

        self.check_streak_rewards()

    def check_streak_rewards(self):
        if self.save.get("sick_day") == self.today:
            return

        if self.save.get("last_reward_day") == self.today:
            return


        s = self.save["streak_simple"]
        p = self.save["streak_pro"]

        lines = []
        if p // 10 > 0:
            lines.append(f"+{p // 10} редких (про)")
        if p // 100 > 0:
            lines.append(f"+{p // 100} эпических (про)")
        if p // 500 > 0:
            lines.append(f"+{p // 500} легендарных (про)")
        if s // 20 > 0:
            lines.append(f"+{s // 20} редких (обычный)")
        if s // 200 > 0:
            lines.append(f"+{s // 200} эпических (обычный)")
        if s // 1000 > 0:
            lines.append(f"+{s // 1000} легендарных (обычный)")

        if lines:
            self.show_popup(
                title="НАГРАДА ЗА СТРИК",
                text="\n".join(lines),
                on_take=self.apply_streak_rewards
            )

    def apply_streak_rewards(self):
        s = self.save["streak_simple"]
        p = self.save["streak_pro"]

        self.save["fish"]["rare"] += p // 10 + s // 20
        self.save["fish"]["epic"] += p // 100 + s // 200
        self.save["fish"]["legend"] += p // 500 + s // 1000

        self.save["last_reward_day"] = self.today
        save_json(SAVE_FILE, self.save)
        self.refresh_fish()
        self.info.text = self.get_info_text()

    def take_reward(self, kind, amount):
        self.save["fish"][kind] += amount
        save_json(SAVE_FILE, self.save)
        self.refresh_fish()
        self.info.text = self.get_info_text()

    def show_popup(self, title, text, on_take):
        self.close_last_popup()

        content = BoxLayout(orientation="vertical", padding=15, spacing=15)
        content.add_widget(make_label_white(
            text=text,
            size_hint=(1, 0.7),
            font_size="18sp",
            halign="center",
            valign="middle"
        ))
        btn = Button(
            text="Забрать",
            size_hint=(1, 0.3),
            background_normal="",
            background_down="",
            background_color=(0.3, 0.7, 1, 1),
            color=(1, 1, 1, 1),
            font_size="18sp"
        )

        popup = Popup(
            title=title,
            title_color=(1, 1, 1, 1),
            content=content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False,
            background_color=(0.15, 0.15, 0.2, 1)
        )

        def take_and_close(*a):
            on_take()
            popup.dismiss()

        btn.bind(on_press=take_and_close)
        content.add_widget(btn)
        self._last_popup = popup
        popup.open()

    # ===== ОБМЕН =====
    def open_exchange(self, *args):
        self.close_last_popup()

        content = BoxLayout(orientation="vertical", padding=10, spacing=6)
        self.exchange_labels = {}

        top_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5)
        for key in ["common", "rare", "epic", "legend"]:
            lbl = make_label_white(
                text=str(self.save["fish"][key]),
                size_hint=(0.25, 1),
                font_size="20sp",
                bold=True,
                halign="center",
                valign="middle"
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.exchange_labels[key] = lbl
            top_row.add_widget(lbl)
        content.add_widget(top_row)

        pairs = [
            ("common", "rare", 50),
            ("rare", "epic", 50),
            ("epic", "legend", 50),
        ]

        for low, high, rate in pairs:
            content.add_widget(self.make_exchange_row(low, high, rate, "up"))
            content.add_widget(self.make_exchange_row(high, low, rate, "down"))

        popup = Popup(
            title="Обмен рыбок",
            title_color=(1, 1, 1, 1),
            content=content,
            size_hint=(0.9, 0.8),
            background_color=(0.15, 0.15, 0.2, 1)
        )
        self._last_popup = popup
        self.exchange_popup = popup
        popup.open()

    def refresh_exchange(self):


        if not hasattr(self, "exchange_labels"):
            return
        for key, lbl in self.exchange_labels.items():
            lbl.text = str(self.save["fish"][key])

    def make_exchange_row(self, src, dst, rate, direction):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=55, spacing=5)

        row.add_widget(Image(
            source=f"fish_{src}.png" if os.path.exists(f"fish_{src}.png") else "",
            size_hint=(0.25, 1),
            allow_stretch=True, keep_ratio=True
        ))

        if direction == "up":
            text = f"{rate}=1"
        else:
            text = f"1={rate}"

        btn = Button(
            text=text,
            size_hint=(0.5, 1),
            background_normal="",
            background_down="",
            background_color=(0.3, 0.7, 1, 1),
            color=(1, 1, 1, 1),
            font_size="18sp",
            bold=True
        )

        if direction == "up":
            btn.bind(on_press=lambda *a, s=src, d=dst, r=rate: self.do_up(s, d, r))
        else:
            btn.bind(on_press=lambda *a, s=src, d=dst, r=rate: self.do_down(s, d, r))

        row.add_widget(btn)

        row.add_widget(Image(
            source=f"fish_{dst}.png" if os.path.exists(f"fish_{dst}.png") else "",
            size_hint=(0.25, 1),
            allow_stretch=True, keep_ratio=True
        ))

        return row

    def do_up(self, src, dst, rate):
        if self.save["fish"][src] >= rate:
            self.save["fish"][src] -= rate
            self.save["fish"][dst] += 1
            save_json(SAVE_FILE, self.save)
            self.refresh_fish()
            self.refresh_exchange()
        else:
            self.show_float_text("!")

    def do_down(self, src, dst, rate):
        if self.save["fish"][src] >= 1:
            self.save["fish"][src] -= 1
            self.save["fish"][dst] += rate
            save_json(SAVE_FILE, self.save)
            self.refresh_fish()
            self.refresh_exchange()
        else:
            self.show_float_text("!")

# ===== ЗАПУСК =====
class MyApp(App):
    def build(self):
        return CatApp()

if __name__ == "__main__":
    MyApp().run()