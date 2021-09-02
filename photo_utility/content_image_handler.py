import cv2
import os
from PIL import Image, ImageDraw
import numpy as np
from math import pow


class ContentImageHandler:
    def __init__(self, target_ratio, kernel_size, threshold_ratio):
        # Set media loading path
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.MEDIA_DB_DIR = os.path.join(BASE_DIR, 'test_database')

        # Set target size
        self.target_ratio = target_ratio

        # Set kernel, threshold ratio
        self.kernel_size = kernel_size
        self.threshold_ratio = threshold_ratio

    def scan_image(self, image_copy):
        # Convert image to grayscale
        image = image_copy.convert('L')

        image_array = np.array(image, 'uint8')

        # Array to get mean of variance
        variance_holder = list()

        # List to hold scanning box
        scanning_box_area_list = list()

        # Scan image by kernel
        scan_unit_size = image_array.shape[0] // self.kernel_size

        for scan_index in range(scan_unit_size):
            # Scan each area of array
            scanning_box = image_array[scan_index * self.kernel_size: ((scan_index + 1) * self.kernel_size) if (scan_index + 1) * self.kernel_size < image_array.shape[0] else image_array.shape[0], :]

            # Set area of scanning box
            scanning_box_area = {"x": 0,
                                 "y": scan_index * self.kernel_size,
                                 "width": scanning_box.shape[1],
                                 "height": scanning_box.shape[0]}

            scanning_box_area_list.append(scanning_box_area)

            # Append variance
            variance_holder.append(np.var(scanning_box))

        # Get mean of variance
        np_variance_holder = np.array(variance_holder)
        mean_of_variance = np.mean(np_variance_holder)

        # Get threshold
        threshold = mean_of_variance * self.threshold_ratio

        # Get index of lower than threshold
        index_list_lower_threshold = list(np.where(np_variance_holder < threshold)[0])

        # Concat lower threshold boxes
        concat_box_list = list()
        concat_box = None

        for list_index, lower_threshold_index in enumerate(index_list_lower_threshold):
            selected_box = scanning_box_area_list[lower_threshold_index]

            # Concat box if its approximate
            if list_index + 1 < len(index_list_lower_threshold):
                if lower_threshold_index + 1 == index_list_lower_threshold[list_index + 1]:
                    if concat_box is None:
                        concat_box = selected_box

                    # merge box
                    concat_box["height"] += scanning_box_area_list[list_index + 1]["height"]

                else:
                    if concat_box is not None:
                        concat_box_list.append(concat_box)
                        concat_box = None

            else:
                if concat_box is not None:
                    concat_box_list.append(concat_box)

        return concat_box_list

    @staticmethod
    def find_closest_area_index(previous_closest_index, concat_box_list, target_end):
        previous_closest_index += 1 if previous_closest_index != 0 else 0

        minimum_area_index = None
        minimum_area_sum = None

        # Scan concat box list and get lowest
        for concat_box_index, concat_box in enumerate(concat_box_list[previous_closest_index:]):
            # Calculate area sum
            area_sum = pow(target_end - (concat_box["y"] + concat_box["height"]), 2)

            # Update min area sum
            if minimum_area_sum is None:
                minimum_area_sum = area_sum
                minimum_area_index = concat_box_index

            else:
                if area_sum < minimum_area_sum:
                    minimum_area_sum = area_sum
                    minimum_area_index = concat_box_index

        if len(concat_box_list[previous_closest_index:]) != 0:
            closest_area_index = minimum_area_index + previous_closest_index

        else:
            closest_area_index = 0

        return closest_area_index

    def slice_image(self, image_copy, concat_box_list):
        # Set target height
        target_height = int(self.target_ratio * image_copy.width)

        # Hold sliced images
        sliced_image_list = list()

        # Scan image copy
        slice_unit = image_copy.height // target_height

        # Memorize prev sliced concat box index
        previous_closest_index = 0
        previous_closest_area = {"x": 0, "y": 0, "width": 0, "height": 0}

        for slice_unit_index in range(slice_unit):
            target_end = (slice_unit_index + 1) * target_height if slice_unit_index + 1 < slice_unit else image_copy.height

            # Find closest area to slice
            closest_area_index = self.find_closest_area_index(concat_box_list=concat_box_list,
                                                              target_end=target_end,
                                                              previous_closest_index=previous_closest_index)
            closest_area = concat_box_list[closest_area_index]

            # Get sliced image
            sliced_image = image_copy.crop(
                (
                    # Set x
                    0,

                    # Set y
                    previous_closest_area["y"] + (previous_closest_area["height"] // 2),

                    # Set x + width
                    image_copy.width,

                    # Set y + height
                    closest_area["y"] + (closest_area["height"] // 2))
            )

            print(target_end)
            print(closest_area_index)
            print(closest_area)
            print(previous_closest_area["y"] + (previous_closest_area["height"] // 2))
            print(closest_area["y"] + (closest_area["height"] // 2))
            print("=" * 50)

            # Update previous data
            previous_closest_index = closest_area_index
            previous_closest_area = closest_area

            sliced_image_list.append(sliced_image)

        return sliced_image_list

    def image_slice_process(self, image_copy):
        # Scan and get sliced image
        concat_box_list = self.scan_image(image_copy=image_copy)

        # Slice scanned image
        sliced_image_list = self.slice_image(image_copy=image_copy,
                                             concat_box_list=concat_box_list)

        return sliced_image_list


if __name__ == "__main__":
    handler = ContentImageHandler(target_ratio=1.1,
                                  kernel_size=2,
                                  threshold_ratio=0.01)
    #handler.scan_image(file_name=f"1.jpg", kernel_size=2, threshold_ratio=0.01)
    #handler.detect_rectangle(file_name=f"1.jpg", kernel_size=1)
    #handler.detect_horizontal_line(file_name=f"1.jpg")
    handler.image_slice_process(file_name=f"8.jpg")

    '''
    for i in range(8):
        if i + 1 == 4: continue
        handler.scan_image(file_name=f"{i+1}.jpg")
        #handler.detect_rectangle(file_name=f"{i+1}.jpg")
    
    '''
