import random
import os
from image_gen import generate_bingo_card

def test_image_generation():
    # Read tasks from the provided task file
    try:
        with open("tasks.txt", "r", encoding="utf-8") as f:
            all_tasks = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("task file not found. Ensure you run this script from the repo root.")
        return

    if len(all_tasks) < 25:
        print("Not enough tasks in task file.")
        return

    selected_tasks = random.sample(all_tasks, 25)

    print("Testing image generation...")
    output_file = "test_output.png"
    generate_bingo_card(selected_tasks, output_file)

    if os.path.exists(output_file):
        print(f"Image successfully generated to {output_file}!")
        print("Please review the image to ensure the text fits correctly in the grid.")
    else:
        print("Failed to generate image.")

if __name__ == "__main__":
    test_image_generation()
