# Flower Snatcher
#### This Python script is a reflex game for two players who are trying to “steal” a flower. The goal is to use the `A` and `L` keys on the keyboard to steal the flower as quickly as possible after it appears on the screen. 

***
### GUI interface preview:

When you start the game, this main menu with game settings will appear. You can turn on soothing music to create a relaxing atmosphere, or change the language to English or Czech.:

<img width="437,5" height="327" alt="home" src="https://github.com/user-attachments/assets/449da021-b6cc-47e8-8acb-3adf2c7d10f6" />

Press the `Play` button to start the game. Press the `Escape` button to exit.:

<img width="437,5" height="327" alt="game" src="https://github.com/user-attachments/assets/e309e672-df0d-4208-9d52-f16345092b8c" />

When the game ends, this message announcing the winner will appear.:

<img width="437,5" height="327" alt="winner" src="https://github.com/user-attachments/assets/377feb25-d331-4afe-8499-a4ea285a932c" />

***
### Top 5 interesting things in the Source Code:

#### 1. Music is prepared to loop more smoothly
The code trims quiet parts from the beginning and end of the music, then joins two copies of the remaining music. That helps reduce silence between repeats.

```python
trimmed_audio = raw_audio[first_frame * frame_size:last_frame * frame_size]
return pygame.mixer.Sound(buffer=trimmed_audio + trimmed_audio)
```

#### 2. Music is optional
If Pygame cannot initialize the mixer, the game records that music is unavailable and skips loading it.

```python
try:
    pygame.mixer.init()
    audio_available = True
except pygame.error:
    audio_available = False
```

#### 3. One translation lookup updates text throughout the game
The selected language chooses the matching text dictionary. Winner messages also use placeholders to insert the player number and score.


```python
"winner": "Player {player} wins with {score} points!"

def text(key):
    return translations[selected_language][key]
```

#### 4. The flower is clamped inside the window
When the window is resized, the flower’s position is adjusted so its image stays within the visible area.

```python
flower_position = (
    max(flower_width // 2, min(flower_position[0], canvas_width - flower_width // 2)),
    max(flower_height // 2, min(flower_position[1], canvas_height - flower_height // 2))
)
```

#### 5. The flower reappears after a random delay at a new size
After a successful catch, the next flower appears 100–3000 milliseconds later. Its size is randomly changed to one of the other supported sizes.

```python
next_flower_time = pygame.time.get_ticks() + random.randint(100, 3000)

flower_size = random.choice([size for size in [1, 2, 3, 4] if size != flower_size])
```
