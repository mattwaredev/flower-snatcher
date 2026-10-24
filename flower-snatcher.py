import os
import random
import pygame

pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.init()
try:
    pygame.mixer.init()
    audio_available = True
except pygame.error:
    audio_available = False

window = pygame.display.set_mode((1000, 700), pygame.RESIZABLE)
pygame.display.set_caption("Snatch the Flower")
clock = pygame.time.Clock()

flower_source = pygame.image.load(os.path.join(os.path.dirname(__file__), "Flower.png")).convert_alpha()
flower_image = flower_source
flower_size = 1
flower_position = (700, 400)
invalid_presses = 0
flower = None
sound_enabled = False
music_enabled = False
music_file = os.path.join(os.path.dirname(__file__), "Music.mp3")
sound_file = os.path.join(os.path.dirname(__file__), "Sound.mp3")
click_sound = None
music_sound = None
music_channel = None

def load_looping_music(file_path):
    source = pygame.mixer.Sound(file_path)
    raw_audio = source.get_raw()
    frame_size = 4
    silence_threshold = 1000
    first_frame = 0
    last_frame = len(raw_audio) // frame_size
    while first_frame < last_frame:
        frame = raw_audio[first_frame * frame_size:(first_frame + 1) * frame_size]
        if max(abs(int.from_bytes(frame[:2], "little", signed=True)), abs(int.from_bytes(frame[2:], "little", signed=True))) > silence_threshold:
            break
        first_frame += 1
    while last_frame > first_frame:
        frame = raw_audio[(last_frame - 1) * frame_size:last_frame * frame_size]
        if max(abs(int.from_bytes(frame[:2], "little", signed=True)), abs(int.from_bytes(frame[2:], "little", signed=True))) > silence_threshold:
            break
        last_frame -= 1
    trimmed_audio = raw_audio[first_frame * frame_size:last_frame * frame_size]
    return pygame.mixer.Sound(buffer=trimmed_audio + trimmed_audio)

if audio_available:
    click_sound = pygame.mixer.Sound(sound_file)
    click_sound.set_volume(1.0)
    music_sound = load_looping_music(music_file)
    music_sound.set_volume(0.35)
    music_channel = pygame.mixer.Channel(0)
running = True
game_started = False
difficulty_open = False
language_open = False
selected_players = "2 hráči"
selected_language = "Čeština"
player_scores = [0, 0, 0, 0, 0]
next_flower_time = None
game_over_message = None
game_over_time = None

colours = [
    (255, 225, 0), (40, 120, 220), (220, 50, 50), (50, 170, 70),
    (150, 70, 190), (245, 140, 30), (130, 80, 35), (150, 150, 150),
    (220, 220, 220), (235, 190, 30)
]
player_key_sets = {
    "2 hráči": [pygame.K_a, pygame.K_l],
        "3 hráči": [pygame.K_a, pygame.K_g, pygame.K_l],
        "4 hráči": [pygame.K_a, pygame.K_d, pygame.K_j, pygame.K_l],
        "5 hráčů": [pygame.K_a, pygame.K_d, pygame.K_g, pygame.K_j, pygame.K_l]
}
translations = {
    "Čeština": {
        "music": "Hudba", "sounds": "Zvuky", "players": "Hráči", "difficulty": "Obtížnost", "language": "Jazyk",
        "play": "Hrát", "exit": "Ukončit", "welcome": "Vítej!", "two_players": "Tato hra je pro 2 hráče.",
        "player_keys": "Hráč 1 používá klávesu A a hráč 2 klávesu L.", "point": "Hráč, který první chytí květinu, získá bod.",
        "escape": "Stisknutím klávesy Escape hru ukončíš.", "good_luck": "Hodně štěstí a dobře se bav!",
        "winner": "Hráč {player} vyhrál s {score} body!", "no_winner": "Hra skončila bez vítěze."
    },
    "Angličtina": {
        "music": "Music", "sounds": "Sounds", "players": "Players", "difficulty": "Difficulty", "language": "Language",
        "play": "Play", "exit": "Exit", "welcome": "Welcome!", "two_players": "This game is for 2 players.",
        "player_keys": "Player 1 uses the A key and Player 2 uses the L key.", "point": "The first player to catch the flower gets a point.",
        "escape": "Press Escape to end the game.", "good_luck": "Good luck and have fun!",
        "winner": "Player {player} wins with {score} points!", "no_winner": "Game ended with no winner."
    }
}

def text(key):
    return translations[selected_language][key]

try:
    title_font = pygame.font.SysFont("Arial", 36, bold=True)
    message_font = pygame.font.SysFont("Arial", 18)
    button_font = pygame.font.SysFont("Arial", 16)
    large_button_font = pygame.font.SysFont("Arial", 20, bold=True)
except pygame.error:
    title_font = pygame.font.Font(None, 36)
    message_font = pygame.font.Font(None, 18)
    button_font = pygame.font.Font(None, 16)
    large_button_font = pygame.font.Font(None, 20)


def prepare(event=None):
    global player_scores, invalid_presses
    player_scores = [0, 0, 0, 0, 0]
    invalid_presses = 0


def position_menu(event=None):
    return


def keep_flower_visible(event=None):
    global flower_position
    if flower is None:
        return
    flower_width, flower_height = flower_image.get_size()
    canvas_width, canvas_height = window.get_size()
    flower_position = (
        max(flower_width // 2, min(flower_position[0], canvas_width - flower_width // 2)),
        max(flower_height // 2, min(flower_position[1], canvas_height - flower_height // 2))
    )


def start_game(event=None):
    global game_started, flower, flower_position, difficulty_open, language_open
    game_started = True
    difficulty_open = False
    language_open = False
    flower_position = (window.get_width() // 2, window.get_height() // 2)
    flower = flower_image
    keep_flower_visible()


def exit_game(event=None):
    global running
    stop_music()
    running = False


def toggle_sound(event=None):
    global sound_enabled
    sound_enabled = not sound_enabled


def play_click_sound():
    if sound_enabled and click_sound is not None:
        click_sound.play()


def toggle_music(event=None):
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        start_music()
    else:
        stop_music()


def start_music():
    if audio_available and music_channel is not None and music_sound is not None:
        music_channel.play(music_sound, loops=-1)


def stop_music():
    if audio_available and music_channel is not None:
        music_channel.stop()


def toggle_difficulty(event=None):
    global difficulty_open, language_open
    difficulty_open = not difficulty_open
    language_open = False


def toggle_language(event=None):
    global language_open, difficulty_open
    language_open = not language_open
    difficulty_open = False


def select_language(language):
    global selected_language
    selected_language = language


def select_difficulty(event=None, players=None):
    global selected_players
    selected_players = players


def configure_player_keys():
    return


def catch_player(player_number):
    global flower, invalid_presses, next_flower_time
    if flower is None:
        invalid_presses += 1
        if invalid_presses > 3:
            end(winner=1 if player_number != 1 else 2)
        return
    flower = None
    player_scores[player_number - 1] += 1
    next_flower_time = pygame.time.get_ticks() + random.randint(100, 3000)


def catch_Player1(event=None):
    catch_player(1)


def catch_Player2(event=None):
    catch_player(2)


def catch_Player3(event=None):
    catch_player(3)


def catch_Player4(event=None):
    catch_player(4)


def catch_Player5(event=None):
    catch_player(5)


def restart_flower():
    global flower, flower_image, flower_size, flower_position, invalid_presses
    invalid_presses = 0
    flower_size = random.choice([size for size in [1, 2, 3, 4] if size != flower_size])
    source_width, source_height = flower_source.get_size()
    flower_image = pygame.transform.scale(
        flower_source, (source_width // flower_size, source_height // flower_size)
    )
    flower_position = (random.randint(0, window.get_width()), random.randint(0, window.get_height()))
    flower = flower_image
    keep_flower_visible()


def end(event=None, winner=None):
    global game_over_message, game_over_time
    if winner is None:
        winner = player_scores.index(max(player_scores)) + 1
    active_players = len(player_key_sets[selected_players])
    if winner <= active_players:
        game_over_message = text("winner").format(player=winner, score=player_scores[winner - 1])
    else:
        game_over_message = text("no_winner")
    stop_music()
    game_over_time = pygame.time.get_ticks() + 2500


def draw_button(surface, rectangle, text, font, fill=(255, 255, 255)):
    pygame.draw.rect(surface, fill, rectangle)
    pygame.draw.rect(surface, (30, 30, 30), rectangle, 1)
    label = font.render(text, True, (0, 0, 0))
    surface.blit(label, label.get_rect(center=rectangle.center))


def menu_message_lines():
    sentences = [text("welcome"), text("two_players"), text("player_keys"), text("point"), text("escape"), text("good_luck")]
    maximum_width = max(280, window.get_width() - 80)
    lines = []
    for sentence in sentences:
        words = sentence.split()
        current_line = ""
        for word in words:
            candidate = word if not current_line else current_line + " " + word
            if message_font.size(candidate)[0] <= maximum_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
    return lines


def menu_layout():
    center = window.get_width() // 2
    message_lines = menu_message_lines()
    top_y = 115 + len(message_lines) * 22 + 30
    button_width = max(70, min(110, (window.get_width() - 56) // 5))
    button_gap = 8
    total_width = button_width * 5 + button_gap * 4
    first_button_x = (window.get_width() - total_width) // 2
    top_buttons = [
        (pygame.Rect(first_button_x + index * (button_width + button_gap), top_y, button_width, 40), label)
        for index, label in enumerate(["Hudba", "Zvuky", "Hráči", "Obtížnost", "Jazyk"])
    ]
    button_y = top_y + 125 if difficulty_open or language_open else top_y + 75
    play_rectangle = pygame.Rect(center + 5, button_y, 110, 60)
    exit_rectangle = pygame.Rect(center - 115, button_y, 110, 60)
    difficulty_rectangles = [
        pygame.Rect(center - 225 + index * 150, top_y + 50, 110, 40)
        for index in range(4)
    ]
    language_rectangles = [
        pygame.Rect(center - 75 + index * 150, top_y + 50, 140, 40)
        for index in range(2)
    ]
    return top_buttons, play_rectangle, exit_rectangle, difficulty_rectangles, language_rectangles, top_y


def draw_switch(surface, rectangle, enabled):
    switch = pygame.Rect(rectangle.left + 10, rectangle.centery - 9, 32, 18)
    switch_colour = (0, 170, 0) if enabled else (130, 130, 130)
    pygame.draw.rect(surface, switch_colour, switch, border_radius=9)
    pygame.draw.rect(surface, (40, 40, 40), switch, width=1, border_radius=9)
    knob_x = switch.right - 9 if enabled else switch.left + 9
    pygame.draw.circle(surface, (255, 255, 255), (knob_x, switch.centery), 7)
    pygame.draw.circle(surface, (40, 40, 40), (knob_x, switch.centery), 7, width=1)


def draw_menu(surface):
    top_buttons, play_rectangle, exit_rectangle, difficulty_rectangles, language_rectangles, top_y = menu_layout()
    title = title_font.render("Snatch the Flower", True, (0, 0, 0))
    surface.blit(title, title.get_rect(center=(window.get_width() // 2, 60)))
    for index, line in enumerate(menu_message_lines()):
        rendered_line = message_font.render(line, True, (0, 0, 0))
        surface.blit(rendered_line, rendered_line.get_rect(center=(window.get_width() // 2, 115 + index * 22)))
    for index, (rectangle, label) in enumerate(top_buttons):
        label = [text("music"), text("sounds"), text("players"), text("difficulty"), text("language")][index]
        fill = (255, 255, 0) if (index == 2 and difficulty_open) or (index == 4 and language_open) else (255, 255, 255)
        draw_button(surface, rectangle, "" if index < 2 else label, button_font, fill)
        if index == 0:
            draw_switch(surface, rectangle, music_enabled)
            label_surface = button_font.render(text("music"), True, (0, 0, 0))
            surface.blit(label_surface, (rectangle.left + 50, rectangle.centery - label_surface.get_height() // 2))
        elif index == 1:
            draw_switch(surface, rectangle, sound_enabled)
            label_surface = button_font.render(text("sounds"), True, (0, 0, 0))
            surface.blit(label_surface, (rectangle.left + 50, rectangle.centery - label_surface.get_height() // 2))
    if difficulty_open:
        for index, rectangle in enumerate(difficulty_rectangles):
            label = list(player_key_sets)[index]
            fill = (220, 50, 50) if label == selected_players else (255, 255, 255)
            draw_button(surface, rectangle, label, button_font, fill)
    if language_open:
        for index, rectangle in enumerate(language_rectangles):
            language = ["Čeština", "Angličtina"][index]
            fill = (220, 50, 50) if language == selected_language else (255, 255, 255)
            draw_button(surface, rectangle, language, button_font, fill)
    draw_button(surface, exit_rectangle, text("exit"), large_button_font)
    draw_button(surface, play_rectangle, text("play"), large_button_font)


def handle_menu_click(position):
    top_buttons, play_rectangle, exit_rectangle, difficulty_rectangles, language_rectangles, top_y = menu_layout()
    if exit_rectangle.collidepoint(position):
        play_click_sound()
        exit_game()
    elif play_rectangle.collidepoint(position):
        play_click_sound()
        start_game()
    elif top_buttons[0][0].collidepoint(position):
        play_click_sound()
        toggle_music()
    elif top_buttons[4][0].collidepoint(position):
        play_click_sound()
        toggle_language()
    elif top_buttons[1][0].collidepoint(position):
        play_click_sound()
        toggle_sound()
    elif top_buttons[2][0].collidepoint(position):
        play_click_sound()
        toggle_difficulty()
    elif difficulty_open:
        for index, rectangle in enumerate(difficulty_rectangles):
            if rectangle.collidepoint(position):
                play_click_sound()
                select_difficulty(players=list(player_key_sets)[index])
    elif language_open:
        for index, rectangle in enumerate(language_rectangles):
            if rectangle.collidepoint(position):
                select_language(["Čeština", "Angličtina"][index])


prepare()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()
        elif event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            keep_flower_visible()
        elif event.type == pygame.KEYDOWN:
            if game_started and game_over_message is None:
                play_click_sound()
            if event.key == pygame.K_ESCAPE:
                end()
            elif game_started and game_over_message is None and event.key in player_key_sets[selected_players]:
                catch_player(player_key_sets[selected_players].index(event.key) + 1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_started and game_over_message is None:
            handle_menu_click(event.pos)
    if game_over_message is not None:
        if pygame.time.get_ticks() >= game_over_time:
            running = False
        else:
            window.fill((144, 238, 144))
            result = title_font.render(game_over_message, True, (0, 0, 0))
            window.blit(result, result.get_rect(center=(window.get_width() // 2, window.get_height() // 2)))
    else:
        window.fill((144, 238, 144))
        if game_started:
            if flower is None and next_flower_time is not None and pygame.time.get_ticks() >= next_flower_time:
                restart_flower()
            if flower is not None:
                window.blit(flower_image, flower_image.get_rect(center=flower_position))
        else:
            draw_menu(window)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
