# game_loader_ui.py: A PyGame-based UI for a classic game loader application

import pygame  # For creating the game window and handling graphics
import sys     # For system-specific parameters and functions
import os      # For file and directory operations
import json    # For reading and writing game metadata
import asyncio # For asynchronous programming
import aiofiles  # For asynchronous file operations
from PIL import Image  # For image processing
import io  # For handling byte streams
from typing import Dict, List, Optional, Tuple  # For type hinting

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600  # Define the window size
screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Classic Computing")  # Set the window title

# Define colors (RGB tuples)
BACKGROUND_COLOR: Tuple[int, int, int] = (200, 200, 200)  # Light gray for retro look
TEXT_COLOR: Tuple[int, int, int] = (0, 0, 0)  # Black
BUTTON_COLOR: Tuple[int, int, int] = (180, 180, 180)  # Slightly darker gray for buttons
TILE_COLOR: Tuple[int, int, int] = (220, 220, 220)  # Even lighter gray for tiles
TITLE_BAR_GRADIENT_START: Tuple[int, int, int] = (100, 100, 100)  # Dark gray
TITLE_BAR_GRADIENT_END: Tuple[int, int, int] = (180, 180, 180)  # Light gray
TOOLBAR_COLOR: Tuple[int, int, int] = (220, 220, 220)  # Light gray
STATUS_BAR_COLOR: Tuple[int, int, int] = (180, 180, 180)  # Medium gray
ICON_COLOR: Tuple[int, int, int] = (0, 0, 255)  # Blue for icons

# Define fonts
FONT_SMALL: pygame.font.Font = pygame.font.Font(None, 24)  # Small font for general use
FONT_MEDIUM: pygame.font.Font = pygame.font.Font(None, 32)  # Medium font for titles

# Grid layout settings
GRID_ROWS, GRID_COLS = 4, 5  # Define the grid size for game tiles
TILE_WIDTH, TILE_HEIGHT = 120, 100  # Define the size of each tile
TILE_MARGIN = 10  # Space between tiles
GRID_TOP = 100  # Vertical offset for the grid, adjusted for title bar and toolbar

# Thumbnail cache to store loaded images
thumbnail_cache: Dict[str, pygame.Surface] = {}


async def scan_and_update_games(directory: str) -> None:
    """
    Scan the given directory for game files and update the game metadata JSON file.

    This function walks through the directory tree, identifies game files (exe, app, sh),
    looks for corresponding thumbnail images, and creates a list of game metadata.
    The metadata is then written to a JSON file for later use by the game loader.

    Args:
        directory (str): The root directory to scan for game files.

    Returns:
        None
    """
    games: List[Dict[str, str]] = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a game executable
            if file.endswith((".exe", ".app", ".sh")):
                game_path = os.path.join(root, file)
                game_name = os.path.splitext(file)[0]
                # Look for a corresponding thumbnail image
                thumbnail_path = os.path.join(root, f"{game_name}.png")
                games.append(
                    {
                        "name": game_name,
                        "path": game_path,
                        "thumbnail": (
                            thumbnail_path if os.path.exists(thumbnail_path) else ""
                        ),
                    }
                )

    try:
        # Write the game metadata to a JSON file
        async with aiofiles.open("game_metadata.json", "w") as f:
            await f.write(json.dumps({"games": games}, indent=2))
    except IOError as e:
        print(f"Error updating game metadata: {e}")


async def load_thumbnail(path: str) -> Optional[pygame.Surface]:
    """
    Asynchronously load and cache a thumbnail image.

    Args:
        path (str): The file path of the thumbnail image.

    Returns:
        Optional[pygame.Surface]: The loaded thumbnail as a Pygame surface, or None if loading fails.
    """
    # Return None for empty paths
    if not path or path == "":
        return None

    # Return cached thumbnail if available
    if path in thumbnail_cache:
        return thumbnail_cache[path]

    try:
        # Asynchronously read the image file
        async with aiofiles.open(path, "rb") as f:
            img_data = await f.read()

        # Open the image using PIL
        image = Image.open(io.BytesIO(img_data))

        # Resize the image to fit the tile dimensions
        image.thumbnail((TILE_WIDTH, TILE_HEIGHT))

        # Convert PIL image to Pygame surface
        mode = image.mode
        size = image.size
        data = image.tobytes()
        thumbnail = pygame.image.fromstring(data, size, mode).convert_alpha()

        # Cache the thumbnail for future use
        thumbnail_cache[path] = thumbnail
        return thumbnail
    except Exception as e:
        print(f"Error loading thumbnail: {path}. Error: {e}")
        return None


def draw_title_bar(surface: pygame.Surface, width: int) -> None:
    """
    Draw the title bar of the application window.

    Args:
        surface (pygame.Surface): The surface to draw on.
        width (int): The width of the surface.

    This function creates a gradient title bar, adds window control buttons,
    and displays the application title.
    """
    # Draw gradient title bar
    for i in range(30):  # 30px height for title bar
        # Calculate color for each line of the gradient
        color = [
            start + (end - start) * i / 30
            for start, end in zip(TITLE_BAR_GRADIENT_START, TITLE_BAR_GRADIENT_END)
        ]
        pygame.draw.line(surface, color, (0, i), (width, i))

    # Add window control buttons (placeholders)
    pygame.draw.rect(surface, (255, 0, 0), (width - 90, 5, 20, 20))  # Close button
    pygame.draw.rect(surface, (255, 255, 0), (width - 60, 5, 20, 20))  # Minimize button
    pygame.draw.rect(surface, (0, 255, 0), (width - 30, 5, 20, 20))  # Maximize button

    # Add title text
    title_font = pygame.font.Font(None, 24)
    title_text = title_font.render("Classic Computing", True, TEXT_COLOR)
    surface.blit(title_text, (10, 5))  # Position the title text


def draw_toolbar(surface: pygame.Surface, width: int) -> None:
    """
    Draw the toolbar on the given surface.

    Args:
        surface (pygame.Surface): The surface to draw on.
        width (int): The width of the toolbar.

    This function draws a rectangular toolbar and adds placeholder icons.
    In a real application, these would be replaced with actual pixelated icons.
    """
    # Draw the toolbar background
    pygame.draw.rect(surface, TOOLBAR_COLOR, (0, 30, width, 40))

    # Add placeholder icons
    # TODO: Replace these with actual pixelated icons
    for i in range(5):
        icon_x = 10 + i * 40
        pygame.draw.rect(surface, ICON_COLOR, (icon_x, 35, 30, 30))

def draw_status_bar(surface: pygame.Surface, width: int, height: int) -> None:
    """
    Draw the status bar at the bottom of the screen.

    Args:
        surface (pygame.Surface): The surface to draw on.
        width (int): The width of the screen.
        height (int): The height of the screen.

    Returns:
        None
    """
    # Draw the status bar background
    pygame.draw.rect(surface, STATUS_BAR_COLOR, (0, height - 30, width, 30))

    # Create and render the status text
    status_font = pygame.font.Font(None, 18)
    status_text = status_font.render("Ready", True, TEXT_COLOR)

    # Draw the status text on the surface
    surface.blit(status_text, (10, height - 25))


def draw_tile(row: int, col: int, title: str) -> None:
    """
    Draw a single game tile on the screen.

    Args:
        row (int): The row index of the tile in the grid.
        col (int): The column index of the tile in the grid.
        title (str): The title of the game to be displayed on the tile.

    This function calculates the position of the tile, draws the tile background,
    a placeholder icon, and the game title.
    """
    # Calculate tile position
    x = col * (TILE_WIDTH + TILE_MARGIN) + TILE_MARGIN
    y = (
        row * (TILE_HEIGHT + TILE_MARGIN) + TILE_MARGIN + GRID_TOP + 70
    )  # Adjusted for title bar and toolbar

    # Draw tile background
    pygame.draw.rect(screen, TILE_COLOR, (x, y, TILE_WIDTH, TILE_HEIGHT))

    # Draw pixelated icon (placeholder)
    icon_size = 32
    pygame.draw.rect(
        screen,
        ICON_COLOR,
        (x + (TILE_WIDTH - icon_size) // 2, y + 10, icon_size, icon_size),
    )

    # Draw title text
    text_surface = FONT_SMALL.render(title, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(
        center=(x + TILE_WIDTH // 2, y + TILE_HEIGHT - 15)
    )
    screen.blit(text_surface, text_rect)


async def main() -> None:
    """
    Main function that runs the game loader application.

    This function initializes the game data, sets up the main game loop,
    handles events, and updates the display.
    """
    clock: pygame.time.Clock = pygame.time.Clock()

    # Load actual game data from JSON file
    try:
        async with aiofiles.open("game_metadata.json", "r") as f:
            content: str = await f.read()
            game_data: Dict[str, List[Dict[str, str]]] = json.loads(content)
            games: List[Dict[str, str]] = game_data.get("games", [])
    except IOError:
        print("Error loading game metadata. Using sample data.")
        # Generate sample data if unable to load from file
        games = [
            {"name": f"Game {i+1}", "thumbnail": ""}
            for i in range(GRID_ROWS * GRID_COLS)
        ]

    running: bool = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the background
        screen.fill(BACKGROUND_COLOR)

        # Draw UI elements
        draw_title_bar(screen, WIDTH)
        draw_toolbar(screen, WIDTH)
        draw_status_bar(screen, WIDTH, HEIGHT)

        # Draw grid layout for game tiles
        for i, game in enumerate(games[: GRID_ROWS * GRID_COLS]):
            # Calculate position for each tile
            row: int = i // GRID_COLS
            col: int = i % GRID_COLS
            x: int = col * (TILE_WIDTH + TILE_MARGIN) + TILE_MARGIN
            y: int = row * (TILE_HEIGHT + TILE_MARGIN) + TILE_MARGIN + GRID_TOP + 70

            # Load and draw thumbnail
            thumbnail: Optional[pygame.Surface] = await load_thumbnail(game.get("thumbnail", ""))
            if thumbnail:
                screen.blit(thumbnail, (x, y))
            else:
                # Draw placeholder if thumbnail not available
                pygame.draw.rect(
                    screen, ICON_COLOR, (x + (TILE_WIDTH - 32) // 2, y + 10, 32, 32)
                )

            # Draw the game tile with its name
            draw_tile(row, col, game["name"])

        # Update the entire display
        pygame.display.flip()

        # Cap the frame rate to 60 FPS
        clock.tick(60)

        # Allow other asynchronous tasks to run
        await asyncio.sleep(0)

    # Quit Pygame when the main loop exits
    pygame.quit()


# Entry point of the script
if __name__ == "__main__":
    # Define an asynchronous function to run the application
    async def run_app():
        # Scan for games and update the metadata
        await scan_and_update_games("/home/ubuntu/test_games")
        print("Game metadata updated.")
        # Run the main application loop
        await main()

    # Use asyncio to run the asynchronous application
    asyncio.run(run_app())
