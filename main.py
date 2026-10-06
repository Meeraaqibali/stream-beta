# main.py - BETA VERSION 1.0
import re
import urllib.request
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import platform

CATEGORIES = {
    "Movies": "https://iptv-org.github.io/iptv/categories/movies.m3u",
    "Anime": "https://iptv-org.github.io/iptv/categories/animation.m3u",
    "Channels": "https://iptv-org.github.io/iptv/index.m3u",
    "Songs": "https://iptv-org.github.io/iptv/categories/music.m3u"
}

def get_channels(m3u_url):
    try:
        req = urllib.request.Request(m3u_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            text = response.read().decode('utf-8')
            
        lines = text.split('\n')
        channels = []
        for i in range(len(lines)):
            if lines[i].startswith('#EXTINF'):
                name_match = re.search(r',(.+)$', lines[i])
                name = name_match.group(1).strip() if name_match else "Unknown"
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()
                    if url.startswith('http'):
                        channels.append({'name': name, 'url': url})
        return channels
    except Exception as e:
        return [{"name": f"Error: {e}", "url": ""}]

class StreamBeta(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.spinner = Spinner(
            text='Movies',
            values=list(CATEGORIES.keys()),
            size_hint=(1, 0.1),
            background_color=(0, 0.8, 0.8, 1)
        )
        self.spinner.bind(text=self.load_category)
        layout.add_widget(self.spinner)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        self.load_category(None, 'Movies')
        return layout

    def load_category(self, spinner, text):
        self.grid.clear_widgets()
        url = CATEGORIES.get(text)
        channels = get_channels(url)
        for ch in channels:
            btn = Button(
                text=ch['name'],
                size_hint_y=None,
                height=80,
                background_color=(0.2, 0.2, 0.2, 1)
            )
            btn.stream_url = ch['url']
            btn.bind(on_press=self.play_stream)
            self.grid.add_widget(btn)

    def play_stream(self, instance):
        if platform == 'android' and instance.stream_url:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(Uri.parse(instance.stream_url), "video/*")
            current_activity = autoclass('org.kivy.android.PythonActivity').mActivity
            current_activity.startActivity(intent)

if __name__ == '__main__':
    StreamBeta().run()
