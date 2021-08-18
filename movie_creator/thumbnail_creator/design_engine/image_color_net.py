import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import json
from math import sqrt


class ItemColorNet:
    def __init__(self):
        # set num of clusters
        self.num_of_clusters = 5
        self.color_cluster = KMeans(n_clusters=self.num_of_clusters)

        # Load gradient color set
        self.base_path = '/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/temperary_database'

        with open(f'{self.base_path}/gradation_color_set/ver_1.json') as json_file:
            self.gradient_color_set = list()

            primitive_gradient_color_set = json.load(json_file)['gradient_color_set']

            # Convert hex color to rgb
            for primitive_gradient_color in primitive_gradient_color_set:
                start_color_hex = primitive_gradient_color[0].lstrip('#')
                start_color_rgb = tuple(int(start_color_hex[i:i+2], 16) for i in (0, 2, 4))

                end_color_hex = primitive_gradient_color[1].lstrip('#')
                end_color_rgb = tuple(int(end_color_hex[i:i + 2], 16) for i in (0, 2, 4))

                self.gradient_color_set.append([start_color_rgb, end_color_rgb])

    def get_closest_color_from_gradation_palette(self, rgb):
        r, g, b = rgb
        color_diffs = []

        for color_set_index, color_combination in enumerate(self.gradient_color_set):
            for combination_num, color in enumerate(color_combination):
                cr, cg, cb = color
                color_diff = sqrt(abs(r - cr) ** 2 + abs(g - cg) ** 2 + abs(b - cb) ** 2)
                color_diffs.append((color_diff, color, color_combination[0] if combination_num == 1 else color_combination[1]))

        minimum_color_set = min(color_diffs)

        return minimum_color_set

    def get_clustered_color(self, pil_image):
        # Reshape image to 1 dimension
        image = np.array(pil_image).reshape((pil_image.height * pil_image.width, 3))

        # cluster pixels in image & get the color of background
        self.color_cluster.fit(image)

        # set labels for rgb pixel
        labels = list(self.color_cluster.labels_)

        # set centroids
        centroid = self.color_cluster.cluster_centers_

        # calculate each percent of labels
        percent = []

        for i in range(len(centroid)):
            j = labels.count(i)
            j = j / (len(labels))
            percent.append(j)

        # get top 2 color
        sorted_percent = sorted(percent, reverse=True)

        prime_color_index = np.where(np.array(percent) == sorted_percent[0])
        sub_color_index = np.where(np.array(percent) == sorted_percent[1])

        prime_color_value = np.round(centroid[prime_color_index], 0)[0]
        sub_color_value = np.round(centroid[sub_color_index], 0)[0]

        color_set = {"prime_color": prime_color_value, "sub_color": sub_color_value}

        return color_set


if __name__ == "__main__":
    net = ItemColorNet()

    b_path = '/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/temperary_database'

    album_cover_image = Image.open(fp=f'{b_path}/album_cover_images/4061560.jpg')

    album_cover_image.show()

    color_set = net.get_clustered_color(pil_image=album_cover_image)

    prime_color = color_set['prime_color']
    sub_color = color_set['sub_color']

    prime_color_pil = Image.new(mode='RGBA', size=(300, 300), color=(int(prime_color[0]), int(prime_color[1]), int(prime_color[2])))
    sub_color_pil = Image.new(mode='RGBA', size=(300, 300), color=(int(sub_color[0]), int(sub_color[1]), int(sub_color[2])))

    prime_color_pil.show()

    import time

    #time.sleep(3)
    #sub_color_pil.show()

    color_combination = net.get_closest_color_from_gradation_palette(rgb=prime_color)

    print(color_combination)

    a_color_pil = Image.new(mode='RGBA', size=(300, 300), color=color_combination[1])
    b_color_pil = Image.new(mode='RGBA', size=(300, 300), color=color_combination[2])

    a_color_pil.show()
    b_color_pil.show()


