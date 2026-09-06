import pygame


def upgrades_menu(screen, my_font, pcb_count, pcb_per_second, auto_solderer_cost, mechanical_arm_cost, worker_cost):
    screen.fill((25, 25, 35))

    # Show stats at the top
    stats_text = my_font.render(f"PCBs: {pcb_count} | Power: {pcb_per_second}", True, (255, 255, 255))
    screen.blit(stats_text, (50, 20))

    # Auto Solderer Button
    button1_rect = pygame.Rect(50, 150, 1180, 80)
    pygame.draw.rect(screen, (60, 60, 60), button1_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), button1_rect, 2, border_radius=10)

    upg_text = my_font.render(f"Auto Solderer | Cost: {auto_solderer_cost} PCBs | +1 PCB/sec", True, (200, 200, 200))
    screen.blit(upg_text, (80, 165))

    #Mechanical Arm button
    button2_rect = pygame.Rect(50, 250, 1180, 80)
    pygame.draw.rect(screen, (60, 60, 60), button2_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), button2_rect, 2, border_radius=10)

    upg2_text = my_font.render(f"Mechanical Arm | Cost: {mechanical_arm_cost} PCBs | +4 PCB/sec", True, (200, 200, 200))
    screen.blit(upg2_text, (80, 265))

    #Workers button
    button3_rect = pygame.Rect(50, 250, 1180, 80)
    pygame.draw.rect(screen, (60, 60, 60), button3_rect, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), button3_rect, 2, border_radius=10)

    upg3_text = my_font.render(f"Worker | Cost: {worker_cost} PCBs | +10 PCB/sec", True, (200, 200, 200))
    screen.blit(upg2_text, (80, 365))

    # Back Button
    pygame.draw.rect(screen, (150, 0, 0), (50, 600, 150, 50), border_radius=5)
    back_txt = my_font.render("BACK", True, (255, 255, 255))
    screen.blit(back_txt, (75, 602))
