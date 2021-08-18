import numpy as np
from PIL import Image


class DesignEngineUtility:
    def __init__(self):
        pass

    @staticmethod
    def alpha_merging(canvas, asset_image, x, y):
        # Set plain array to attach assets
        plain_array = np.zeros((canvas.height, canvas.width, 4))

        # Attach image to plain array
        plain_array[y: (y + asset_image.height), x: (x + asset_image.width), :] = np.array(asset_image)

        # Convert array to pil image
        plain_array = np.uint8(plain_array)
        blended_asset_image = Image.fromarray(plain_array)

        # composite images
        after_canvas = Image.alpha_composite(canvas, blended_asset_image)

        return after_canvas

    '''
    # Create canvas that possess mask color
        asset_image_array = np.asarray(asset_image)
        pixels_mask = np.all(asset_image_array == mask_color, axis=-1)

        mask_canvas = Image.new('RGBA',
                                size=(asset_image.width, asset_image.height),
                                color=(255, 255, 255) + (0,))

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

        asset_image_with_hole.show()

        # Composite images in masked area
        image_with_frame = Image.alpha_composite(attaching_image_with_transparent_background, asset_image_with_hole)
        #image_with_frame.show()

        return image_with_frame'''