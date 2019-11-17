import tkinter as tk   # python3
#import Tkinter as tk   # python

TITLE_FONT = ("Helvetica", 18, "bold")

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        title = tk.Label(self, text="뉴스 감성분석을 통한 주가예측 시스템", font=TITLE_FONT)
        title.pack(side="top", fill="x", pady=10)

        title = tk.Label(self, text="주식종목을 입력해주세요 : ")
        title.pack(side="left", fill="y", pady=10)

        entry1 = tk.Entry(self)
        entry1.pack(fill="x", padx=5, expand=True)


        button1 = tk.Button(self, text="주가 예측 수행",
                             command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="분석 결과 보기",
                             command=lambda: controller.show_frame("PageTwo"))
        button1.pack(side="left", padx=5, pady=5, expand=True)
        button2.pack(side="left", padx=5, pady=5, expand=True)


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 1", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 2", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()