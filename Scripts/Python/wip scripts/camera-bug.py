import cv2
def get_available_camera_index(max_index=5):
    idxs = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            cap.release()
            idxs.append(i)
        cap.release()
    return idxs
print(get_available_camera_index())
