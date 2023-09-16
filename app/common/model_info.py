import time
import threading


class ModelInfo(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        time.sleep(1)
        self.class_list = []
        self.color_list = []

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(ModelInfo, "_instance"):
            with ModelInfo._instance_lock:
                if not hasattr(ModelInfo, "_instance"):
                    ModelInfo._instance = ModelInfo(*args, **kwargs)
        return ModelInfo._instance

    def generate_random_colors(self):
        print("generate_random_colors start!")
        import random

        num_colors = len(self.class_list)
        print(num_colors)
        self.color_list = []
        for _ in range(num_colors):
            print("random")
            # Generate random RGB values in the range [0, 255]
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)

            # Append the RGB color as a tuple to the colors list
            try:
                self.color_list.append((red, green, blue))
            except Exception as e:
                print(e)
        print("color_list length = " + str(len(self.color_list)))
