from PIL import Image
import select
import v4l2capture
import threading
from io import BytesIO

class Camera(object):
    def get_frame(self):
        video = v4l2capture.Video_device("/dev/video0")
        size_x, size_y = video.set_format(352, 288)
        video.create_buffers(1)
        video.queue_all_buffers()
        video.start()
        select.select((video,), (), ())
        image_data = video.read()
        video.close()
        image = Image.fromstring("RGB", (size_x, size_y), image_data)
        with BytesIO() as f:
            image.save(f, format='JPEG')
            return f.getvalue()

