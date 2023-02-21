class PyMenu:
    def __init__(self, options_dict, menu_title, escape_text):
        self.options_dict = options_dict
        self.menu_title = menu_title
        self.escape_text = escape_text
        self.id_focus = 0
    
    def display_menu(self):
        vocalizza(self.menu_title)
        for key in self.options_dict:
            vocalizza(key)
        vocalizza(self.escape_text)
        self.id_focus = 0
    
    def navigate_menu(self, direction):
        if direction == "up":
            if self.id_focus > 0:
                self.id_focus -= 1
                vocalizza(list(self.options_dict.keys())[self.id_focus])
            else:
                self.id_focus = len(self.options_dict) - 1
                vocalizza(list(self.options_dict.keys())[self.id_focus])
        elif direction == "down":
            if self.id_focus < len(self.options_dict) - 1:
                self.id_focus += 1
                vocalizza(list(self.options_dict.keys())[self.id_focus])
            else:
                self.id_focus = 0
                vocalizza(list(self.options_dict.keys())[self.id_focus])
    
    def execute_selected_option(self):
        selected_option = list(self.options_dict.values())[self.id_focus]
        selected_option()
