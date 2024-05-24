from tkinter import *
from math import ceil
from PIL import ImageTk, Image
from random import randint
from tkinter.messagebox import showinfo
from tkcalendar import *
import pyodbc
import datetime


class Window(Tk):
    def __init__(self):
        super().__init__()

        self.resizable(False, False)
        self.title("Prometheus")
        self.geometry("400x400")

        self.__frame = Planner(self)
        self.__frame.pack()


class Planner(Frame):
    def __init__(self, MASTER):
        super().__init__(MASTER)

        # ONLY CHANGE THIS CODE
        "=============================================================================="
        self.location = r"Planner_Checklist.accdb"
        self.table = "Planner"
        "=============================================================================="

        self.bgc = "#3D617D"
        self.fgc = "#D3FFF3"
        self.actbcol = "#6A94B5"
        self.actfcol = "#D3FFF3"
        self.font = ('Montserrat SemiBold', 9)

        self.__messages = ["I know you can do it!", "Well done!", "Nice going!", "Good job!", "Nicely done!"]

        self.frame1, self.frame2, self.frame3, self.frame4 = None, None, None, None
        self.__database = None
        self.__activities = []
        self.__grouped = []
        self.__n_pages = 0
        self.__current_i = 0
        self.__btn_state = 0
        self.__last_ID = 0

        self.__bg = (Image.open("whitelotus.png"))
        self.__my_canvas = Canvas(self, width=400, height=400)
        self.__my_canvas.pack(fill="both", expand=TRUE)

        self.__resized_image = self.__bg.resize((500, 800))
        self.__new_image = ImageTk.PhotoImage(self.__resized_image)
        self.__my_canvas.create_image(197, 55, image=self.__new_image)

        self.__my_canvas.create_text(200, 25, text="Planner Checklist", fill='#d3fff3',
                                     justify="center", font=('LL Karatula', 24))

        self.__create_button = Button(self, text="Create", activeforeground=self.actfcol,
                                      activebackground=self.actbcol, padx=4, pady=3, width=20,
                                      font=self.font, bg=self.bgc, fg=self.fgc,
                                      command=lambda: self.create())
        self.__my_canvas.create_window(205, 375, anchor="center", window=self.__create_button)

        self.__next = Button(self, text=">>", activeforeground=self.actfcol, activebackground=self.actbcol,
                             command=lambda: self.next(), font=self.font)

        self.__prev = Button(self, text="<<", activeforeground=self.actfcol, activebackground=self.actbcol,
                             command=lambda: self.prev(), font=self.font)

        if self.connect():
            self.display()

        else:
            self.__create_button.config(state=DISABLED)

    def connect(self):
        try:
            connect = pyodbc.connect(fr'Driver={"Microsoft Access Driver (*.mdb, *.accdb)"};DBQ={self.location};')

        except pyodbc.Error as error:
            print(error)

        else:
            self.__database = connect.cursor()
            return True

    def retrieve(self):
        self.__database.execute(f'SELECT * FROM {self.table}')

        list_ = []

        for activity in self.__database.fetchall():
            list_.append(activity)

        self.__activities = list_
        self.__n_pages = ceil((len(self.__activities) / 4))

        try:
            self.__last_ID = self.__activities[-1][0]

        except IndexError:
            self.__last_ID = 0

    def group(self):
        a = 0
        b = 4

        n_collection = len(self.__activities)

        if b > n_collection:
            b = n_collection

        grouped = []

        for x in range(ceil(n_collection / 4)):
            grp_4 = []

            for y in range(a, b):
                grp_4.append(self.__activities[y])

            grouped.append(grp_4)
            a = b
            b += 4

            if b > n_collection:
                b = n_collection

        self.__grouped = grouped

    def destroy_(self):
        frames = [self.frame1, self.frame2, self.frame3, self.frame4]
        for frm in frames:
            if frm is not None:
                frm.destroy()

    def display(self, create=False):
        self.retrieve()
        self.group()

        if create:
            self.__current_i = len(self.__grouped) - 1

        self.state()
        self.destroy_()

        execute = True
        current_grp = None

        try:
            current_grp = self.__grouped[self.__current_i]

        except IndexError:
            try:
                current_grp = self.__grouped[-1]

            except IndexError:
                execute = False
                self.__next.config(state=DISABLED)
                self.__prev.config(state=DISABLED)
                self.__my_canvas.create_text(200, 200, text="No Tasks", fill='#7288B2', justify="center",
                                             font=('LL Karatula', 20), tags="no_task")
                self.__my_canvas.delete("next")
                self.__my_canvas.delete("prev")
                self.__my_canvas.delete("page_num")

        if execute:
            try:
                self.__my_canvas.delete("next")
                self.__my_canvas.delete("prev")
                self.__my_canvas.delete("page_num")
                self.__my_canvas.delete("no_task")

            finally:
                if self.__n_pages != 1:
                    self.__my_canvas.create_window(250, 335, anchor="center", window=self.__next, tags="next")
                    self.__my_canvas.create_window(150, 335, anchor="center", window=self.__prev, tags="prev")
                    self.__my_canvas.create_text(200, 335, text=f"{self.__current_i + 1}/{self.__n_pages}",
                                                 fill="white",
                                                 font=self.font, tags="page_num")

                self.frame1 = Frame(self)
                self.frame2 = Frame(self)
                self.frame3 = Frame(self)
                self.frame4 = Frame(self)

                doneb_font = ('Montserrat SemiBold', 10)
                Button(self.frame1, text="✔", bg="green", fg=self.fgc, font=doneb_font,
                       command=lambda: self.remove(current_grp[0][0], True)).grid(row=1, column=3, rowspan=2, padx=5,
                                                                                  pady=5, sticky="se")
                Button(self.frame2, text="✔", bg="green", fg=self.fgc, font=doneb_font,
                       command=lambda: self.remove(current_grp[1][0], True)).grid(row=1, column=3, rowspan=2, padx=5,
                                                                                  pady=5, sticky="se")
                Button(self.frame3, text="✔", bg="green", fg=self.fgc, font=doneb_font,
                       command=lambda: self.remove(current_grp[2][0], True)).grid(row=1, column=3, rowspan=2, padx=5,
                                                                                  pady=5, sticky="se")
                Button(self.frame4, text="✔", bg="green", fg=self.fgc, font=doneb_font,
                       command=lambda: self.remove(current_grp[3][0], True)).grid(row=1, column=3, rowspan=2, padx=5,
                                                                                  pady=5, sticky="se")

                delb_font = ('Montserrat SemiBold', 5)
                Button(self.frame1, text="❌", bg="red", fg=self.fgc, font=delb_font,
                       command=lambda: self.remove(current_grp[0][0])).grid(row=0, column=3, padx=5, pady=5,
                                                                            sticky="ne")
                Button(self.frame2, text="❌", bg="red", fg=self.fgc, font=delb_font,
                       command=lambda: self.remove(current_grp[1][0])).grid(row=0, column=3, padx=5, pady=5,
                                                                            sticky="ne")
                Button(self.frame3, text="❌", bg="red", fg=self.fgc, font=delb_font,
                       command=lambda: self.remove(current_grp[2][0])).grid(row=0, column=3, padx=5, pady=5,
                                                                            sticky="ne")
                Button(self.frame4, text="❌", bg="red", fg=self.fgc, font=delb_font,
                       command=lambda: self.remove(current_grp[3][0])).grid(row=0, column=3, padx=5, pady=5,
                                                                            sticky="ne")

                x_coor = 105
                y_coor = 130
                index = 0
                frames = [self.frame1, self.frame2, self.frame3, self.frame4]

                for act in current_grp:
                    title = act[1]

                    d = act[2]
                    yr = datetime.datetime.strptime(d, "%x").year
                    d = d.split("/")
                    d[2] = str(yr)
                    t = act[3].split(":")

                    due_dt = datetime.datetime(month=int(d[0]), day=int(d[1]), year=int(d[2]),
                                               hour=int(t[0]), minute=int(t[1]), second=int(t[2]))
                    format_dt = due_dt.strftime("%c")

                    dt_now = datetime.datetime.now()

                    due_in_days = (due_dt - dt_now).days

                    due_color = self.color(due_in_days)
                    due_text = f"Due in {due_in_days} day/s"

                    if x_coor > 300:
                        x_coor = 105
                        y_coor += 130

                    self.__my_canvas.create_window(x_coor, y_coor, window=frames[index])
                    frames[index].configure(bg=due_color)

                    Label(frames[index], text=title, bg=due_color, width=17, height=4,
                          font=('Montserrat SemiBold', 8)).grid(row=0, column=0, columnspan=2)
                    Label(frames[index], text=due_text, bg=due_color).grid(row=1, column=0, columnspan=2, sticky="sw")
                    Label(frames[index], text=format_dt, bg=due_color).grid(row=2, column=0, columnspan=2, sticky="sw")

                    index += 1
                    x_coor += 190

    def create(self):
        def add():
            Title = title.get()
            Date = due_date.get_date()
            Time = f"{hour.get()}:{mint.get()}:{sec.get()}"
            self.__last_ID += 1

            data = (self.__last_ID, Title, Date, Time)

            self.__database.execute(f'INSERT INTO {self.table} (ID, Title, DueDate, DueTime) VALUES(?, ?, ?, ?)', data)
            self.__database.commit()
            creator_frame.destroy()
            self.__btn_state += 1
            self.display(create=True)

        def cancel():
            creator_frame.destroy()
            self.__btn_state += 1

        if not self.disable():
            creator_frame = Frame(self)
            self.__my_canvas.create_window(200, 200, window=creator_frame)

            Button(creator_frame, text="Add", bg="green", fg=self.fgc, width=7, command=add).grid(row=6, column=0,
                                                                                                  columnspan=2, pady=10,
                                                                                                  sticky="nse")
            Button(creator_frame, text="Cancel", bg="red", fg=self.fgc, width=7, command=cancel).grid(row=6, column=4,
                                                                                                      columnspan=2,
                                                                                                      pady=10,
                                                                                                      sticky="nsw")

            Label(creator_frame, text="Title").grid(row=0, column=0, sticky="sw", padx=10, pady=5)
            title = Entry(creator_frame, width=50)
            title.grid(row=1, column=0, columnspan=6, padx=10)

            Label(creator_frame, text="Date").grid(row=2, column=0, sticky="sw", padx=10, pady=5)
            due_date = Calendar(creator_frame, width=50)
            due_date.grid(row=3, column=0, columnspan=6, padx=10, sticky="nsew")

            Label(creator_frame, text="Time").grid(row=4, column=0, sticky="sw", padx=10, pady=5)
            Label(creator_frame, text="Hour").grid(row=5, column=0, sticky="nse")
            Label(creator_frame, text="Min").grid(row=5, column=2, sticky="nse")
            Label(creator_frame, text="Sec").grid(row=5, column=4, sticky="nse")
            hour = Spinbox(creator_frame, from_=0, to=23, wrap=True, width=5, state="readonly", justify=CENTER)
            mint = Spinbox(creator_frame, from_=0, to=59, wrap=True, width=5, state="readonly", justify=CENTER)
            sec = Spinbox(creator_frame, from_=0, to=59, wrap=True, width=5, state="readonly", justify=CENTER)

            hour.grid(row=5, column=1, sticky="nsw")
            mint.grid(row=5, column=3, sticky="nsw")
            sec.grid(row=5, column=5, sticky="nsw")

            self.__btn_state += 1

    def remove(self, id_, done=False):
        def confirm():
            self.__database.execute(f'delete from {self.table} where id=?', id_)
            self.__database.commit()
            notif_frame.destroy()
            if done:
                showinfo(message=self.__messages[randint(0, 4)])
            self.__btn_state += 1
            self.display()

        def cancel():
            notif_frame.destroy()
            self.__btn_state += 1

        if not self.disable():
            text = "Are you sure you want to delete this?"
            if done:
                text = "Mark as done"

            notif_frame = Frame(self)
            notif_frame.configure(bg="#CECECE")
            self.__my_canvas.create_window(200, 200, window=notif_frame)

            Label(notif_frame, text=text, bg="#CECECE", width=30).grid(row=0, column=0, columnspan=2, sticky="nsew",
                                                                       padx=10, pady=10)
            Button(notif_frame, text="Confirm", bg="green", fg=self.fgc, width=7, command=confirm).grid(row=1, column=1,
                                                                                                        pady=10)
            Button(notif_frame, text="Cancel", bg="red", fg=self.fgc, width=7, command=cancel).grid(row=1, column=0,
                                                                                                    pady=10)

            self.__btn_state += 1

    def state(self):
        if self.__current_i == self.__n_pages - 1:
            self.__next.config(state=DISABLED)
            self.__prev.config(state=NORMAL)

        if self.__current_i == 0:
            self.__prev.config(state=DISABLED)

    def next(self):
        if not self.disable():
            self.__prev.config(state=NORMAL)
            self.__current_i += 1
            self.display()

    def prev(self):
        if not self.disable():
            self.__next.config(state=NORMAL)
            self.__current_i -= 1
            self.display()

    def color(self, day):
        if day <= 0:
            color = "#FAA0A0"
        elif day <= 2:
            color = "#ffc095"
        elif day <= 4:
            color = "#FDFD96"
        else:
            color = "#93E9BE"
        return color

    def disable(self):
        if self.__btn_state % 2 != 0:
            return True

        else:
            return False


"--------------------------------------------------------------------"

Window().mainloop()
