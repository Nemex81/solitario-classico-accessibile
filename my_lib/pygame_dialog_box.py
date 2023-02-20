import time, pygame
import pygame_menu
import accessible_output2.outputs.auto

# inizializzo l'engine per la vocalizzazione
engine = accessible_output2.outputs.auto.Auto()
# inizializzo pygame
pygame.init()
pygame.font.init()

# globals
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
max_char = 38
font = 'C:/Windows/Fonts/arial.ttf'
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


class PygameDialogBox:
    def __init__(self):
        self.answare = ""
        self.question = ""

    def vocalizza(self, string):
        if string:
            engine.speak(string, interrupt=True)

    def create_dialog_box(self, question):
        menu = pygame_menu.Menu(
            title=question,
            width=400,
            height=300,
            theme=pygame_menu.themes.THEME_DARK
        )
        menu.add_text_input('Answer: ', default='')
        menu.add_button('OK', self.on_input_box_close, menu.get_input_data)
        menu.add_button('Cancel', pygame_menu.events.BACK)
        menu.enable()
        self.vocalizza(question)
        menu.mainloop(screen)

    def create_question_box(self, question):
        menu = pygame_menu.Menu(
            title='Conferma',
            width=400,
            height=300,
            theme=pygame_menu.themes.THEME_DARK
        )
        menu.add_label(question)
        menu.add_button('OK', self.on_question_box_close, True)
        menu.add_button('Cancel', self.on_question_box_close, False)
        menu.enable()
        self.vocalizza(question)
        menu.mainloop(screen)

    def create_alert_box(self, message, title):
        # create menu
        menu = pygame_menu.Menu(title=title, width=300, height=300, theme=pygame_menu.themes.THEME_DARK)

        # add message label
        menu.add.label(message, max_char=-1, font_size=20, font_name=pygame_menu.font.get_font(font, 20))

        # create OK button
        ok_button = menu.add.button('OK')
        ok_button.set_onreturn(lambda: pygame_menu.events.EXIT)

        # open menu
        menu.enable()
        self.vocalizza(message)
        time.sleep(.5)
        menu.mainloop(pygame.display.set_mode((0, 0), pygame.FULLSCREEN))

    def create_duble_input_box(self):
        # create menu
        menu = pygame_menu.Menu(
            title=self.question,
            width=400,
            height=300,
            theme=pygame_menu.themes.THEME_DARK
        )

        # create X text
        menu.add_label('X:')

        # create X input
        menu.add_text_input('Answer X: ', default='')

        # create Y text
        menu.add_label('Y:')

        # create Y input
        menu.add_text_input('Answer Y: ', default='')

        # create OK button
        menu.add_button('OK', self.on_input_box_close, menu.get_input_data)

        # create Cancel button
        menu.add_button('Cancel', pygame_menu.events.BACK)

        # open menu
        menu.enable()
        self.vocalizza(self.question)
        menu.mainloop(screen)

    def on_input_box_close(self, result):
        if result:
            self.answare = result
        else:
            self.answare = ""
        pygame_menu.events.BACK

    def on_question_box_close(self, result):
        self.answare = result
        pygame_menu.events.BACK

#@@@# Start del modulo
if __name__ == "__main__":
    dialog_box = PygameDialogBox()
    #dialog_box.create_alert_box("Hello, world!", "Title")
    #dialog_box.create_dialog_box("What's your name?")
    #dialog_box.create_question_box("Are you sure?")
    #dialog_box.create_duble_input_box()
