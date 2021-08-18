import cv2


class ObjectAreaGetter:
    def __init__(self):
        pass

    def match_area(self, screen_path, template_path):
        ############################
        # Get Exact Area of button #
        ############################

        # Load screen image
        primitive_screen_image = cv2.imread(screen_path)
        screen_image = cv2.imread(screen_path, cv2.IMREAD_GRAYSCALE)

        # Load template image
        template_image = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

        # Get result
        match_result = cv2.matchTemplate(screen_image, template_image, cv2.TM_SQDIFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)
        x, y = min_loc
        h, w = template_image.shape

        checked_screen_image = cv2.rectangle(primitive_screen_image, (x, y), (x + w, y + h), (0, 0, 255), 1)
        cv2.imshow("checked_screen_image", checked_screen_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

