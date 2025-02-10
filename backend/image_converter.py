
import os
import cairosvg
import argparse

def convert_svg_to_image(input_dir, output_format='png'):
    if output_format not in ['png', 'jpg']:
        raise ValueError("Invalid output format. Choose 'png' or 'jpg'.")

    output_dir = os.path.join(input_dir, f"converted_{output_format}")
    os.makedirs(output_dir, exist_ok=True)
    files = []
    for filename in os.listdir(input_dir):

        files.append(filename)
        input_path = os.path.join(input_dir, filename)
        output_filename = os.path.splitext(filename)[0] + f".{output_format}"
        output_path = os.path.join(output_dir, output_filename)

        try:
            cairosvg.svg2png(url=input_path, write_to=output_path) if output_format == 'png' else cairosvg.svg2png(url=input_path, write_to=output_path)
            print(f"Converted: {input_path} -> {output_path}")
        except Exception as e:
            print(f"Error converting {filename}: {e}")


    return files

