import random
import time
import pygame
from pygame.locals import RESIZABLE

from modules.settings import settings
from modules.upgrades import upgrades_menu
import modules.saveprotector as sp

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
WIDTH, HEIGHT = 1280, 720
FPS = 60
AUTOSAVE_SECONDS = 30
MAX_OFFLINE_SECONDS = 8 * 60 * 60
CRIT_CHANCE = 0.08
CRIT_MULTIPLIER = 5
COMBO_TIMEOUT = 1.2
MAX_COMBO_MULTIPLIER = 3.0

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), RESIZABLE)
pygame.display.set_caption("PCB Clicker")
clock = pygame.time.Clock()

# Fonts
my_font = pygame.font.Font("Kavoon-Regular.ttf", 40)
small_font = pygame.font.Font("Kavoon-Regular.ttf", 24)
tiny_font = pygame.font.Font("Kavoon-Regular.ttf", 18)

# Images
pcb_original = pygame.image.load("pcb.jpg").convert()
upgrades_image = pygame.transform.smoothscale(
    pygame.image.load("Upgrades.png").convert_alpha(), (50, 50)
)
settings_image = pygame.transform.smoothscale(
    pygame.image.load("Settings.png").convert_alpha(), (50, 50)
)

# ------------------------------------------------------------
# GAME STATE
# ------------------------------------------------------------
pcb = 0.0
pcb_per_second = 0.0
pcb_per_click = 1

auto_solderer_cost = 50
mechanical_arm_cost = 100
worker_cost = 500

bg_color = (20, 20, 25)
menu_open = False
upgrades_open = False

# Stats / progression
total_pcbs_earned = 0.0
total_clicks = 0
critical_clicks = 0
play_time = 0.0

# Combo
combo = 0
combo_timer = 0.0
combo_multiplier = 1.0

# Small visual effects
floating_texts = []
click_particles = []
pcb_bump = 0.0

# Notifications
notifications = []
unlocked_achievements = set()

# Autosave
last_autosave = time.time()


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def format_number(value):
    """Turn 1234567 into 1.23M, etc."""
    value = float(value)
    suffixes = ["", "K", "M", "B", "T", "Qa", "Qi"]
    index = 0
    while abs(value) >= 1000 and index < len(suffixes) - 1:
        value /= 1000.0
        index += 1

    if index == 0:
        return str(int(value))
    return f"{value:.2f}{suffixes[index]}"


def add_notification(text, kind="success", seconds=2.4):
    notifications.append({"text": text, "kind": kind, "timer": seconds})
    if len(notifications) > 4:
        notifications.pop(0)


def add_floating_text(text, pos, critical=False):
    floating_texts.append({
        "text": text,
        "x": float(pos[0]),
        "y": float(pos[1]),
        "life": 0.8,
        "critical": critical,
    })


def spawn_click_particles(pos):
    for _ in range(10):
        click_particles.append({
            "x": float(pos[0]),
            "y": float(pos[1]),
            "vx": random.uniform(-110, 110),
            "vy": random.uniform(-150, -40),
            "life": random.uniform(0.35, 0.7),
        })


def get_layout():
    """Rects are recalculated so the main screen behaves better when resized."""
    width, height = screen.get_size()

    pcb_size = max(210, min(320, int(min(width, height) * 0.42)))
    pcb_rect = pygame.Rect(
        int(width * 0.22 - pcb_size / 2),
        int(height * 0.56 - pcb_size / 2),
        pcb_size,
        pcb_size,
    )

    upgrades_rect = pygame.Rect(width - 230, 50, 50, 50)
    settings_rect = pygame.Rect(width - 130, 50, 50, 50)

    back_rect = pygame.Rect(50, 50, 150, 50)
    back_from_upg = pygame.Rect(50, height - 120, 150, 50)

    menu_width = max(300, width - 100)
    mint_btn = pygame.Rect(50, 150, menu_width, 60)
    sky_btn = pygame.Rect(50, 230, menu_width, 60)
    sand_btn = pygame.Rect(50, 310, menu_width, 60)
    save_rect = pygame.Rect(50, 450, menu_width, 60)
    import_rect = pygame.Rect(50, 530, menu_width, 60)

    # Matches the three visible upgrade rows in the upgrade menu.
    upgrade_1_rect = pygame.Rect(50, 150, max(300, width - 100), 80)
    upgrade_2_rect = pygame.Rect(50, 250, max(300, width - 100), 120)
    upgrade_3_rect = pygame.Rect(50, 390, max(300, width - 100), 120)

    return {
        "pcb": pcb_rect,
        "upgrades": upgrades_rect,
        "settings": settings_rect,
        "back": back_rect,
        "back_upgrades": back_from_upg,
        "mint": mint_btn,
        "sky": sky_btn,
        "sand": sand_btn,
        "save": save_rect,
        "import": import_rect,
        "upgrade_1": upgrade_1_rect,
        "upgrade_2": upgrade_2_rect,
        "upgrade_3": upgrade_3_rect,
    }


def make_save_data():
    return {
        "save_version": 2,
        "pcb": pcb,
        "bg": list(bg_color),
        "click_power": pcb_per_click,
        "pcb_per_second": pcb_per_second,
        "upg1_cost": auto_solderer_cost,
        "upg2_cost": mechanical_arm_cost,
        "upg3_cost": worker_cost,
        "total_pcbs_earned": total_pcbs_earned,
        "total_clicks": total_clicks,
        "critical_clicks": critical_clicks,
        "play_time": play_time,
        "achievements": list(unlocked_achievements),
        "saved_at": time.time(),
    }


def save_game(show_message=True):
    sp.safesave(make_save_data())
    if show_message:
        add_notification("GAME SAVED!")


def load_game():
    global pcb, bg_color, pcb_per_click, pcb_per_second
    global auto_solderer_cost, mechanical_arm_cost, worker_cost
    global total_pcbs_earned, total_clicks, critical_clicks, play_time
    global unlocked_achievements

    try:
        data = sp.safeload()
        if not data:
            add_notification("Save file is corrupted or was changed.", "error", 3.5)
            return

        pcb = float(data.get("pcb", 0))
        pcb_per_click = int(data.get("click_power", 1))
        pcb_per_second = float(data.get("pcb_per_second", 0))
        bg_color = tuple(data.get("bg", (20, 20, 25)))

        auto_solderer_cost = int(data.get("upg1_cost", 50))
        mechanical_arm_cost = int(data.get("upg2_cost", 100))
        worker_cost = int(data.get("upg3_cost", 500))

        total_pcbs_earned = float(data.get("total_pcbs_earned", pcb))
        total_clicks = int(data.get("total_clicks", 0))
        critical_clicks = int(data.get("critical_clicks", 0))
        play_time = float(data.get("play_time", 0))
        unlocked_achievements = set(data.get("achievements", []))

        # Offline production. Capped so leaving the game for weeks doesn't explode progress.
        saved_at = float(data.get("saved_at", time.time()))
        offline_seconds = min(max(0, time.time() - saved_at), MAX_OFFLINE_SECONDS)
        offline_gain = pcb_per_second * offline_seconds
        if offline_gain >= 1:
            pcb += offline_gain
            total_pcbs_earned += offline_gain
            add_notification(
                f"Offline production: +{format_number(offline_gain)} PCBs",
                "info",
                4.0,
            )
        else:
            add_notification("GAME LOADED!")

    except FileNotFoundError:
        add_notification("No save file found.", "error")
    except (KeyError, TypeError, ValueError) as exc:
        print(f"Could not load save: {exc}")
        add_notification("Save data could not be loaded.", "error", 3.5)


def check_achievements():
    achievements = {
        "first_click": (total_clicks >= 1, "First Contact - build your first PCB"),
        "100_pcbs": (total_pcbs_earned >= 100, "Tiny Factory - make 100 PCBs"),
        "1k_pcbs": (total_pcbs_earned >= 1_000, "Production Line - make 1,000 PCBs"),
        "10k_pcbs": (total_pcbs_earned >= 10_000, "PCB Empire - make 10,000 PCBs"),
        "10_pps": (pcb_per_second >= 10, "Automation - reach 10 PCB/s"),
        "100_clicks": (total_clicks >= 100, "Click Technician - click 100 times"),
        "first_crit": (critical_clicks >= 1, "Lucky Joint - land a critical click"),
    }

    for achievement_id, (condition, text) in achievements.items():
        if condition and achievement_id not in unlocked_achievements:
            unlocked_achievements.add(achievement_id)
            add_notification(f"ACHIEVEMENT: {text}", "achievement", 4.5)


def perform_click(pos):
    global pcb, total_pcbs_earned, total_clicks, critical_clicks
    global combo, combo_timer, combo_multiplier, pcb_bump

    combo += 1
    combo_timer = COMBO_TIMEOUT
    combo_multiplier = min(MAX_COMBO_MULTIPLIER, 1.0 + combo * 0.025)

    critical = random.random() < CRIT_CHANCE
    crit_mult = CRIT_MULTIPLIER if critical else 1
    amount = pcb_per_click * combo_multiplier * crit_mult

    pcb += amount
    total_pcbs_earned += amount
    total_clicks += 1
    if critical:
        critical_clicks += 1

    pcb_bump = 1.0
    spawn_click_particles(pos)
    prefix = "CRIT! +" if critical else "+"
    add_floating_text(f"{prefix}{format_number(amount)}", pos, critical)


def buy_upgrade(which):
    global pcb, pcb_per_second
    global auto_solderer_cost, mechanical_arm_cost, worker_cost

    if which == 1:
        cost = auto_solderer_cost
        gain = 1
        name = "Auto solderer"
    elif which == 2:
        cost = mechanical_arm_cost
        gain = 4
        name = "Mechanical arm"
    else:
        cost = worker_cost
        gain = 12
        name = "Worker"

    if pcb < cost:
        add_notification(f"Need {format_number(cost - pcb)} more PCBs!", "error")
        return

    pcb -= cost
    pcb_per_second += gain

    if which == 1:
        auto_solderer_cost = int(auto_solderer_cost * 1.50)
        next_cost = auto_solderer_cost
    elif which == 2:
        mechanical_arm_cost = int(mechanical_arm_cost * 1.55)
        next_cost = mechanical_arm_cost
    else:
        worker_cost = int(worker_cost * 1.60)
        next_cost = worker_cost

    add_notification(
        f"{name} bought! +{gain}/s | Next: {format_number(next_cost)}",
        "success",
        3.0,
    )


def update_effects(dt):
    global pcb_bump

    pcb_bump = max(0.0, pcb_bump - dt * 5)

    for item in floating_texts[:]:
        item["y"] -= 55 * dt
        item["life"] -= dt
        if item["life"] <= 0:
            floating_texts.remove(item)

    for particle in click_particles[:]:
        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt
        particle["vy"] += 280 * dt
        particle["life"] -= dt
        if particle["life"] <= 0:
            click_particles.remove(particle)

    for notification in notifications[:]:
        notification["timer"] -= dt
        if notification["timer"] <= 0:
            notifications.remove(notification)


def draw_panel(surface, rect, fill=(28, 28, 34), border=(70, 70, 80)):
    pygame.draw.rect(surface, fill, rect, border_radius=16)
    pygame.draw.rect(surface, border, rect, 2, border_radius=16)


def draw_main_screen(layout):
    screen.fill(bg_color)
    width, height = screen.get_size()

    # Top resource display
    score = my_font.render(f"{format_number(pcb)} PCBs", True, (255, 255, 255))
    screen.blit(score, (60, 42))

    pps = small_font.render(f"{format_number(pcb_per_second)} PCB/s", True, (190, 220, 255))
    screen.blit(pps, (65, 94))

    # PCB button hover + click bump
    mouse_pos = pygame.mouse.get_pos()
    base_rect = layout["pcb"]
    hover = base_rect.collidepoint(mouse_pos)
    scale_mult = 1.04 if hover else 1.0
    scale_mult += pcb_bump * 0.06

    draw_size = int(base_rect.width * scale_mult)
    pcb_image = pygame.transform.smoothscale(pcb_original, (draw_size, draw_size))
    pcb_draw_rect = pcb_image.get_rect(center=base_rect.center)
    screen.blit(pcb_image, pcb_draw_rect)

    if hover:
        pygame.draw.rect(screen, (255, 255, 255), pcb_draw_rect, 3, border_radius=14)

    # Right-side stats panel
    panel_w = min(390, max(300, int(width * 0.31)))
    panel = pygame.Rect(width - panel_w - 55, 150, panel_w, min(390, height - 220))
    draw_panel(screen, panel)

    title = small_font.render("FACTORY STATUS", True, (255, 255, 255))
    screen.blit(title, (panel.x + 25, panel.y + 22))

    stats = [
        f"Click power: {format_number(pcb_per_click)}",
        f"Combo: x{combo_multiplier:.2f}",
        f"Total clicks: {format_number(total_clicks)}",
        f"Critical clicks: {format_number(critical_clicks)}",
        f"Lifetime PCBs: {format_number(total_pcbs_earned)}",
        f"Achievements: {len(unlocked_achievements)}/7",
    ]

    for i, line in enumerate(stats):
        surf = tiny_font.render(line, True, (220, 220, 225))
        screen.blit(surf, (panel.x + 25, panel.y + 72 + i * 38))

    # Combo bar
    bar_rect = pygame.Rect(panel.x + 25, panel.bottom - 58, panel.width - 50, 18)
    pygame.draw.rect(screen, (55, 55, 65), bar_rect, border_radius=9)
    combo_ratio = max(0.0, min(1.0, combo_timer / COMBO_TIMEOUT))
    if combo_ratio > 0:
        fill_rect = bar_rect.copy()
        fill_rect.width = int(bar_rect.width * combo_ratio)
        pygame.draw.rect(screen, (120, 210, 255), fill_rect, border_radius=9)

    # Toolbar icons
    screen.blit(upgrades_image, layout["upgrades"])
    screen.blit(settings_image, layout["settings"])

    # Hints
    hint = tiny_font.render("SPACE = click   U = upgrades   S = settings   ESC = back", True, (180, 180, 190))
    screen.blit(hint, (60, height - 42))

    # Particles
    for particle in click_particles:
        radius = max(2, int(5 * particle["life"] / 0.7))
        pygame.draw.circle(screen, (110, 220, 255), (int(particle["x"]), int(particle["y"])), radius)

    # Floating click numbers
    for item in floating_texts:
        color = (255, 220, 80) if item["critical"] else (120, 255, 160)
        surf = small_font.render(item["text"], True, color)
        surf.set_alpha(max(0, min(255, int(255 * item["life"] / 0.8))))
        screen.blit(surf, (int(item["x"]), int(item["y"])))


def draw_notifications():
    width, height = screen.get_size()
    y = height - 90

    colors = {
        "success": (80, 220, 130),
        "error": (255, 100, 100),
        "info": (100, 190, 255),
        "achievement": (255, 210, 80),
    }

    for notification in reversed(notifications):
        color = colors.get(notification["kind"], (255, 255, 255))
        text = tiny_font.render(notification["text"], True, color)
        box = text.get_rect()
        box.inflate_ip(28, 18)
        box.right = width - 35
        box.bottom = y

        pygame.draw.rect(screen, (22, 22, 28), box, border_radius=10)
        pygame.draw.rect(screen, color, box, 2, border_radius=10)
        screen.blit(text, (box.x + 14, box.y + 9))
        y -= box.height + 10


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------
running = True

while running:
    dt = clock.tick(FPS) / 1000.0
    dt = min(dt, 0.1)  # avoids giant jumps after dragging/freezing the window
    play_time += dt

    layout = get_layout()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            try:
                save_game(show_message=False)
            except Exception as exc:
                print(f"Autosave on exit failed: {exc}")
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if menu_open:
                    menu_open = False
                elif upgrades_open:
                    upgrades_open = False
                else:
                    running = False

            elif event.key == pygame.K_u and not menu_open:
                upgrades_open = not upgrades_open

            elif event.key == pygame.K_s and not upgrades_open:
                menu_open = not menu_open

            elif event.key == pygame.K_SPACE and not menu_open and not upgrades_open:
                perform_click(layout["pcb"].center)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if upgrades_open:
                if layout["back_upgrades"].collidepoint(event.pos):
                    upgrades_open = False
                elif layout["upgrade_1"].collidepoint(event.pos):
                    buy_upgrade(1)
                elif layout["upgrade_2"].collidepoint(event.pos):
                    buy_upgrade(2)
                elif layout["upgrade_3"].collidepoint(event.pos):
                    buy_upgrade(3)

            elif menu_open:
                if layout["back"].collidepoint(event.pos):
                    menu_open = False
                elif layout["save"].collidepoint(event.pos):
                    save_game()
                elif layout["import"].collidepoint(event.pos):
                    load_game()
                elif layout["mint"].collidepoint(event.pos):
                    bg_color = (20, 60, 40)
                    add_notification("Mint theme selected", "info")
                elif layout["sky"].collidepoint(event.pos):
                    bg_color = (20, 40, 60)
                    add_notification("Sky theme selected", "info")
                elif layout["sand"].collidepoint(event.pos):
                    bg_color = (40, 20, 40)
                    add_notification("Sand theme selected", "info")

            else:
                if layout["upgrades"].collidepoint(event.pos):
                    upgrades_open = True
                elif layout["settings"].collidepoint(event.pos):
                    menu_open = True
                elif layout["pcb"].collidepoint(event.pos):
                    perform_click(event.pos)

    # Smooth passive production instead of only adding once per second.
    passive_gain = pcb_per_second * dt
    pcb += passive_gain
    total_pcbs_earned += passive_gain

    # Combo decay
    if combo_timer > 0:
        combo_timer -= dt
    else:
        combo = 0
        combo_multiplier = 1.0

    update_effects(dt)
    check_achievements()

    # Autosave every 30 seconds.
    if time.time() - last_autosave >= AUTOSAVE_SECONDS:
        try:
            save_game(show_message=False)
            last_autosave = time.time()
        except Exception as exc:
            print(f"Autosave failed: {exc}")

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------
    if menu_open:
        settings(screen)
    elif upgrades_open:
        upgrades_menu(
            screen,
            my_font,
            pcb,
            pcb_per_click,
            auto_solderer_cost,
            mechanical_arm_cost,
            worker_cost,
        )
    else:
        draw_main_screen(layout)

    # Notifications are drawn on top of every menu.
    draw_notifications()

    pygame.display.flip()

pygame.quit()
