import textwrap
from PIL import Image, ImageDraw, ImageFont

def generate_bingo_card(tasks, output_path="output.png"):
    if len(tasks) != 25:
        raise ValueError("Must provide exactly 25 tasks for the bingo board")

    img = Image.open('images.png').convert('RGB')
    draw = ImageDraw.Draw(img)

    start_x = 24
    start_y = 72
    cell_w = 480 / 5  # 96
    cell_h = 482 / 5  # 96.4

    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except IOError:
        font = ImageFont.load_default()

    for i in range(25):
        row = i // 5
        col = i % 5

        # Replace the dash logic and clean text
        task = tasks[i].replace('—', '-')

        x0 = start_x + col * cell_w
        y0 = start_y + row * cell_h

        pad = 6
        box_w = cell_w - (pad * 2)
        box_h = cell_h - (pad * 2)

        chars_per_line = int(box_w / 6)
        max_lines = int(box_h / 12)

        wrapped_text = textwrap.fill(task, width=chars_per_line)
        lines = wrapped_text.split('\n')

        if len(lines) > max_lines:
            lines = lines[:max_lines]
            if len(lines[-1]) > 3:
                lines[-1] = lines[-1][:-3] + '...'
            else:
                lines[-1] = '...'
            wrapped_text = '\n'.join(lines)

        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        text_x = x0 + (cell_w - text_w) / 2
        text_y = y0 + (cell_h - text_h) / 2

        draw.multiline_text((text_x, text_y), wrapped_text, fill="black", font=font, align="center")

    img.save(output_path)
    return output_path
