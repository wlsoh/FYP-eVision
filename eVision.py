# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Main GUI Integration
# Date Created: 05/05/2022
from tkinter import *
from PIL import Image, ImageTk
from ctypes import windll
import pymysql

# Prevent blur due to screen scale setting
windll.shcore.SetProcessDpiAwareness(1) 

#==============================================================================================#
#                                   Functions & Classes                                        #
#==============================================================================================#

# Dynamically resize login left image
def resize_image(event):
    new_width = event.width
    new_height = event.height
    image = copy_img.resize((new_width, new_height), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    label.config(image = photo)
    label.image = photo #avoid garbage collection
    
# Dynamically resize login right
class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)

# Place window in center
# def center_window(z):
#     # Make the frame opened at center
#     global screen_width, screen_height, x, y
#     screen_width = z.winfo_screenwidth()
#     screen_height = z.winfo_screenheight()
#     x = (screen_width/2)-(window_width/2)
#     y = (screen_height/2)-(window_height/2)
#     z.geometry(f'{window_width}x{window_height}+{int(x)}+{int(y)}')

#==============================================================================================#
#                                           Login                                              #
#==============================================================================================#

## Login Page Interface (Root)
root = Tk()
cscreen_height = root.winfo_screenheight()
cscreen_width = root.winfo_screenwidth()
ratio = float(cscreen_width/1920)
root.title('e-Vision Login')
root.iconbitmap('asset/logo.ico')
root.state('zoomed')
root.minsize(int(cscreen_width*0.8333), int(cscreen_height*0.8333))
# Configure row column attribute
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_rowconfigure(2, weight=0)
root.grid_rowconfigure(3, weight=0)
root.grid_rowconfigure(4, weight=0)
root.grid_rowconfigure(5, weight=0)
root.grid_rowconfigure(6, weight=0)
root.grid_rowconfigure(7, weight=0)
root.grid_rowconfigure(8, weight=0)
root.grid_rowconfigure(9, weight=1)
# Setup frames
login_banner = Frame(root, width=int(cscreen_width/2), height=int(cscreen_height))
login_banner.grid(row=0, column=0, rowspan=10, sticky="nsew")
login_component = Frame(root, width=int(cscreen_width/2), height=int(cscreen_height), bg="#EDF1F7")
login_component.grid(row=0, column=1, rowspan=10, sticky="nsew")
# Left banner image
img = Image.open('asset/login_left.png')
img = img.resize((int(cscreen_width/2), int(cscreen_height)), Image.ANTIALIAS)
copy_img = img.copy()
banner_img = ImageTk.PhotoImage(img)
label = Label(login_banner, image=banner_img)
label.config(highlightthickness=0, borderwidth=0)
label.bind('<Configure>', resize_image)
label.pack(fill=BOTH,expand=YES)
# Right login components
canva = ResizingCanvas(login_component, width=int(cscreen_width/2), height=int(cscreen_height), bg="#EDF1F7", highlightthickness=0)
canva.pack(fill=BOTH, expand=YES)
login_title = Label(root, text="Login to Account", font=("Lato bold", int(34*ratio)), bg="#EDF1F7")
login_title.grid(row=1, column=1, sticky="w", padx=int(100*ratio))
login_desc = Label(root, text="Enter your login data created in below section", font=("Lato", int(12*ratio)), bg="#EDF1F7")
login_desc.grid(row=2, column=1, sticky="w", padx=int(100*ratio))
lbl_email = Label(root, text="Email", font=("Lato bold", int(15*ratio)), bg="#EDF1F7")
lbl_email.grid(row=3, column=1, sticky="w", padx=int(100*ratio), pady=(int(65*ratio),int(5*ratio)))
txt_email = Entry(root, bd=17, relief=FLAT, font=("Lato", int(14*ratio)))
txt_email.grid(row=4, column=1, sticky="nsew", padx=int(100*ratio))
lbl_pass = Label(root, text="Password", font=("Lato bold", int(15*ratio)), bg="#EDF1F7")
lbl_pass.grid(row=5, column=1, sticky="w", padx=int(100*ratio), pady=(int(50*ratio),int(5*ratio)))
txt_pass = Entry(root, bd=17, relief=FLAT, font=("Lato", int(14*ratio)), show="*")
txt_pass.grid(row=6, column=1, sticky="nsew", padx=int(100*ratio))
btn_login = Button(root, text="Login Account", font=("Lato bold", int(16*ratio)), height=2, fg="white", bg="#1267AC", relief=RAISED, activebackground="#0E4470", activeforeground="white")
btn_login.grid(row=7, column=1, sticky="nsew", padx=int(100*ratio), pady=(int(70*ratio),int(40*ratio)))
lbl_reg = Label(root, text="Don't have account? Please contact company's Admin", font=("Lato", int(12*ratio)), bg="#EDF1F7")
lbl_reg.grid(row=8, column=1, sticky="w", padx=int(100*ratio))









root.mainloop()