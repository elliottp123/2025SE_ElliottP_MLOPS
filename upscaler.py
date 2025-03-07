import os
from PIL import Image

input_folder = 'upsacle'
output_folder = "output_gifs"
scale_factor = 2  # 512 -> 1024

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".gif"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        with Image.open(input_path) as img:
            frames = []
            for frame in range(img.n_frames):
                img.seek(frame)
                resized_frame = img.resize(
                    (img.width * scale_factor, img.height * scale_factor),
                    resample=Image.NEAREST  # Maintains dithering
                )
                frames.append(resized_frame.convert("P", palette=Image.ADAPTIVE))

            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                loop=img.info.get("loop", 0),
                duration=img.info.get("duration", 100),
                optimize=True
            )

print("Scaling complete.")
