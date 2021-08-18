from PIL import Image, ImageFilter
import numpy as np
import os

from movie_creator.thumbnail_creator.design_engine.design_engine_utility import DesignEngineUtility


class ForegroundProtocolHandler:
    def __init__(self):
        self.design_engine_utility = DesignEngineUtility()

        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Import secrets
        DB_DIR = os.path.join(BASE_DIR, '../../')
        self.base_asset_path = f'{DB_DIR}/temperary_database'
    
    def attach_shadow(self, asset_image):
        # variables for blur mask
        radius = 3
        diam = 3 * radius
        mask_opacity = 90
        gaussian_p = 1.5
        blur_color = (0, 0, 0, 0)

        # Create blur mask
        back = Image.new('RGBA', (asset_image.width + diam, asset_image.height + diam), blur_color)
        back.paste(asset_image, (radius, radius))

        mask = Image.new('L', (asset_image.width + diam, asset_image.height + diam), mask_opacity)
        blck = Image.new('L', (asset_image.width - diam, asset_image.height - diam), 0)
        mask.paste(blck, (diam, diam))

        # Blur image and paste blurred edge according to mask
        blur = back.filter(ImageFilter.GaussianBlur(radius / gaussian_p))
        back.paste(blur, mask=mask)

        return back

    def mask_image_in_frame(self, attaching_image, asset_image, mask_color):
        # Create canvas that possess mask color
        asset_image_array = np.asarray(asset_image)
        pixels_mask = np.all(asset_image_array == mask_color, axis=-1)

        mask_canvas = Image.new('RGBA',
                                size=(asset_image.width, asset_image.height),
                                color=(255, 255, 255) + (0,))

        mask_canvas_array = np.asarray(mask_canvas)
        mask_canvas_array[pixels_mask] = [255, 255, 255, 255]
        mask_canvas = Image.fromarray(mask_canvas_array)

        # Get area of pixel mask
        rows = np.any(pixels_mask, axis=1)
        cols = np.any(pixels_mask, axis=0)

        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        # Resize attaching mask to fill empty space
        attaching_image = attaching_image.resize((int((cmax - cmin) * 1.2), int((rmax - rmin) * 1.2)))

        # Get x, y point to be pasted
        pasting_x = int(cmin + (cmax - cmin) / 2 - attaching_image.width / 2)
        pasting_y = int(rmin + (rmax - rmin) / 2 - attaching_image.height / 2)

        # Attach attaching image to transparent background image
        attaching_image_with_transparent_background = self.design_engine_utility.alpha_merging(canvas=Image.new('RGBA',
                                                                                                                size=(asset_image.width, asset_image.height),
                                                                                                                color=(255, 255, 255) + (0,)),
                                                                                               asset_image=attaching_image,
                                                                                               x=pasting_x,
                                                                                               y=pasting_y)

        # Create hole to asset image (with mask canvas that possessed specific pixel value)
        asset_image_with_hole = Image.composite(Image.new('RGBA',
                                                          size=(asset_image.width, asset_image.height),
                                                          color=(255, 255, 255) + (0,)),
                                                asset_image,
                                                mask_canvas)

        # Composite images in masked area
        image_with_frame = Image.alpha_composite(attaching_image_with_transparent_background, asset_image_with_hole)

        return image_with_frame

    def design_album_with_record(self, track_cover_image):
        # Covering area
        covering_area = 0.5

        # Load asset image
        asset_image = Image.open(fp=f'{self.base_asset_path}/asset_images/record_cd/record_ver_3.png')

        # Convert images to RGBA
        asset_image = asset_image.convert('RGBA')
        track_cover_image = track_cover_image.convert('RGBA')

        # Attach shadow to track cover
        track_cover_image = self.attach_shadow(track_cover_image)

        if track_cover_image.height != 400:
            track_cover_image = track_cover_image.resize((400, 400))

        # Resize asset image (이상적인건, resize 가 일어나지 않게 하는 것)
        if track_cover_image.height != asset_image.height:
            asset_image = asset_image.resize((int(asset_image.width * (track_cover_image.height / asset_image.height)), track_cover_image.height))

        image_with_frame = self.mask_image_in_frame(mask_color=[0, 0, 0, 51],
                                                    attaching_image=track_cover_image,
                                                    asset_image=asset_image)

        # Set dummy canvas
        dummy_canvas = Image.new('RGBA',
                                 (int(asset_image.width + (track_cover_image.width * covering_area)), int(track_cover_image.height)),
                                 (255, 255, 255) + (0,))

        # Attach each images to canvas
        record_cd_attached_canvas = self.design_engine_utility.alpha_merging(canvas=dummy_canvas,
                                                                             asset_image=image_with_frame,
                                                                             x=(dummy_canvas.width - asset_image.width) - 1,
                                                                             y=0)

        album_cover_attached_canvas = self.design_engine_utility.alpha_merging(canvas=record_cd_attached_canvas,
                                                                               asset_image=track_cover_image,
                                                                               x=0,
                                                                               y=0)

        # Attach preset shadow above stretched canvas
        shadow_preset_image = Image.open(fp=f'{self.base_asset_path}/asset_images/shadow/transparent_shadow.png')
        shadow_preset_image = shadow_preset_image.resize((int(dummy_canvas.width * 0.9), int(dummy_canvas.height * 0.03)))

        stretched_dummy_canvas = Image.new('RGBA',
                                 (dummy_canvas.width, int(dummy_canvas.height + (shadow_preset_image.height // 2))),
                                 (255, 255, 255) + (0,))

        stretched_shadow_attached_canvas = self.design_engine_utility.alpha_merging(canvas=stretched_dummy_canvas,
                                                                                    asset_image=shadow_preset_image,
                                                                                    x=(stretched_dummy_canvas.width // 2) - (shadow_preset_image.width // 2),
                                                                                    y=dummy_canvas.height - (shadow_preset_image.height // 2) - 2)

        # Concentrate each canvas
        composite_canvas = self.design_engine_utility.alpha_merging(canvas=stretched_shadow_attached_canvas,
                                                                    asset_image=album_cover_attached_canvas,
                                                                    x=0,
                                                                    y=0)

        return composite_canvas

    def design_main_component(self, design_pattern, track_cover_image):
        if design_pattern == 'album_with_record':
            return self.design_album_with_record(track_cover_image=track_cover_image)


if __name__ == "__main__":
    protocol_handler = ForegroundProtocolHandler()

    cover_image = Image.open(fp=f'{protocol_handler.base_asset_path}/album_cover_images/20412824.jpg')

    protocol_handler.design_main_component(design_pattern='album_with_record',
                                           track_cover_image=cover_image)