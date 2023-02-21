class PyMenu:
    def __init__(self, items, callback, screen_reader):
        self.items = items
        self.selected_item = 0
        self.callback = callback
        self.screen_reader = screen_reader

    def next_item(self):
        self.selected_item = (self.selected_item + 1) % len(self.items)
        self.screen_reader.vocalizza(self.items[self.selected_item])

    def prev_item(self):
        self.selected_item = (self.selected_item - 1) % len(self.items)
        self.screen_reader.vocalizza(self.items[self.selected_item])

    def execute(self):
        self.callback(self.selected_item)
