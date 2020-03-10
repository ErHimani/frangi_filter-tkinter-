import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import numpy as np
from skimage.filters import frangi, hessian



class App:

    def __init__(self, window, window_title, video_source=0):
        self.x = 500000
        self.x1 = 200
        self.y1 = 115
        self.x2 = 440
        self.y2 = 365
        self.window = window

        self.window.title(window_title)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        # self.canvas = tkinter.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas = tkinter.Canvas(window,width=self.vid.width, height=self.vid.height)

        self.canvas.pack()


        # Button that lets the user take a snapshot
        # self.icon = PIL.ImageTk.PhotoImage(file="images.jpg")
        self.btn_snapshot = tkinter.Button(window, text="Snapshot",width=50,command=self.snapshot,bg="purple",fg="white")
        self.btn_snapshot.pack()


        self.btn_snapshot = tkinter.Button(window, text="Thickness", width=50, command=self.thick,bg="lightyellow")
        self.btn_snapshot.pack()

        self.btn_snapshot = tkinter.Button(window, text="Thinness", width=50, command=self.thin, bg="light green")
        self.btn_snapshot.pack()

        # self.btn_snapshot = tkinter.Button(window, text="Zoomin", width=50, command=self.zoomin)
        # self.btn_snapshot.pack()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            frame = frame[115:365, 200:440]
            # frame = cv2.rotate(frame, rotateCode=cv2.ROTATE_90_COUNTERCLOCKWISE)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            hist = cv2.equalizeHist(gray)

            size = np.size(hist)
            skel = np.zeros(hist.shape, np.uint8)

            clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8, 8))
            c = clahe.apply(hist)

            clamp = np.uint8(np.interp(c, [80, 180], [0, 255]))
            equ = clahe.apply(clamp)

            # r, buf = cv2.imencode('.jpg', equ)

            threshold = cv2.adaptiveThreshold(c, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, 5)

            kernel = np.ones((2, 2), np.uint8)

            opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

            negative = 255 - opening

            element = cv2.getStructuringElement(cv2.MORPH_CROSS, (10, 10))

            eroded = cv2.erode(negative, element)
            tempp = cv2.dilate(eroded, element)
            # temp = cv2.subtract( negative, tempp)
            # skel = cv2.bitwise_or(skel, temp)

            image = opening
            frang = frangi(image) * self.x
            elem = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2))

            erod = cv2.erode(frang, elem)

            cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", erod)


    def thick(self):
        self.x=self.x*2
    def thin(self):
        self.x=self.x/2

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:

            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))

            self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

            frame = frame[self.y1:self.y2, self.x1:self.x2]

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            hist = cv2.equalizeHist(gray)

            size = np.size(hist)
            skel = np.zeros(hist.shape, np.uint8)

            clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8, 8))
            c = clahe.apply(hist)

            clamp = np.uint8(np.interp(c, [80, 180], [0, 255]))
            equ = clahe.apply(clamp)


            threshold = cv2.adaptiveThreshold(c, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 55, 5)

            kernel = np.ones((2, 2), np.uint8)

            opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

            negative = 255 - opening

            element = cv2.getStructuringElement(cv2.MORPH_CROSS, (10, 10))

            eroded = cv2.erode(negative, element)
            # tempp = cv2.dilate(eroded, element)


            image = opening
            frang = frangi(image)*self.x
            elem = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 2))
            erod = cv2.erode(frang, elem)
            self.a = erod
            self.p = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.a))
            self.canvas.create_image(193,115, image=self.p, anchor=tkinter.NW)
        self.window.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        #self.vid.set(cv2.CAP_PROP_EXPOSURE, -8.0)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # self.vid.set(3,640)
        # self.vid.set(4,480)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        # else:
        #      return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the Application object
App(tkinter.Tk(), "Frangi Filter Demo")
