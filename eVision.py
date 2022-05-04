# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Main GUI Integration
# Date Created: 05/05/2022
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from ctypes import windll
import pymysql
import pymysql
from pymysql.constants import CLIENT
import re
from datetime import datetime

# Prevent blur due to screen scale setting
windll.shcore.SetProcessDpiAwareness(1) 
# Regex for password validation
pare = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")
# Create database connection to AWS RDS
db = pymysql.connect(
    host='mydatabase.cdkg8rguncrh.ap-southeast-1.rds.amazonaws.com',
    user='admin',
    password='%Abc040231',
    database='eVision',
    client_flag=CLIENT.MULTI_STATEMENTS
)
cursor = db.cursor()
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

# Login function
def login():
    uname = txt_email.get()
    pas = txt_pass.get()
    global currentuser
    
    # If both fields empty
    if len(uname) == 0 & len(pas) == 0:
        messagebox.showerror("Login Failed", "The fields were empty! Please fill in the valid email and password before login again!")
        txt_email.focus()
    # If email field empty
    elif len(uname) == 0:
        messagebox.showerror("Login Failed", "The email field was empty! Please fill in the valid email and login again!")
        txt_email.focus()
    # If password field empty
    elif len(pas) == 0:
        messagebox.showerror("Login Failed", "The password field was empty! Please fill in the valid password and login again!")
        txt_pass.focus()
    # If password minimum length not satisfied
    elif len(pas) < 8:
        messagebox.showerror("Login Failed", "The password should not less than 8 characters! Please fill in the valid password and login again!")
        txt_pass.delete(0, END)
        txt_pass.focus()
    else:  
        sql = '''SELECT * FROM User WHERE user_email = (%s) AND user_password = (%s)'''
        row_result = cursor.execute(sql, (uname, pas))
        if row_result > 0:
            result_detail = cursor.fetchone()
            currentuser = {
                'user_id': result_detail[0],
                'user_firstname': result_detail[1],
                'user_lastname': result_detail[2],
                'user_password': result_detail[3],
                'user_addressline': result_detail[4],
                'user_city': result_detail[5],
                'user_state': result_detail[6],
                'user_postcode': result_detail[7],
                'user_email': result_detail[8],
                'user_phone': result_detail[9],
                'user_role': result_detail[10],
                'user_lastlogin': result_detail[11],
                'user_firstlogin': result_detail[12]
            }
            now = datetime.now() # Get current date time
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            sql = '''UPDATE User SET user_lastlogin_datetime = (%s) WHERE user_id = (%s)''' # Update last login
            cursor.execute(sql, (dt_string, currentuser["user_id"]))
            cursor.connection.commit()
            currentuser["user_lastlogin"] = dt_string
            txt_email.delete(0, END)
            txt_pass.delete(0, END)
            txt_email.focus()
            messagebox.showinfo("Login Successful", "Hi {0}, welcome back to e-Vision!".format(currentuser["user_firstname"]))
            mainPage() # Invoke the main page
            root.withdraw() # Withdraw the login page
        # If no such user found
        else:
            messagebox.showerror("Login Failed", "Invalid email/password! Please try to login again with valid email and password created!")
            txt_email.delete(0, END)
            txt_pass.delete(0, END)
            txt_email.focus()
            
# Logout function
def logout():
    confirmbox = messagebox.askquestion('e-Vision Logout', 'Are you sure to logout the system?', icon='warning')
    if confirmbox == 'yes':
        currentuser = {} # Set user session to empty
        mainWindow.destroy() # Destroy current winfow
        root.deiconify() # Show login page again
        
# First time change password function
def firstchange():
    new = txt_newpas.get()
    con = txt_cpas.get()
    
    # If both fields empty
    if len(new) == 0 & len(con) == 0:
        messagebox.showerror("Change Password Failed", "The fields were empty! Please fill in the valid new password and confirm password values!")
        txt_newpas.focus()
    # If new pass field empty
    elif len(new) == 0:
        messagebox.showerror("Change Password Failed", "The new password fields were empty! Please fill in the valid new password values!")
        txt_newpas.focus()
    # If confirm pass field empty
    elif len(con) == 0:
        messagebox.showerror("Change Password Failed", "The confirm password fields were empty! Please fill in the valid confirm password values!")
        txt_cpas.focus()
    # If new pass and confirm pass not same
    elif (new != con):
        messagebox.showerror("Change Password Failed", "The values for new password field and confirm password field are not identical!")
        txt_newpas.delete(0, END)
        txt_cpas.delete(0, END)
        txt_newpas.focus()
    # If new password not satisfied the requirement
    elif (re.fullmatch(pare, new)==None):
        messagebox.showerror("Change Password Failed", "The values for new password must be at least 8 characters with minimum one special character and on uppercase letter!")
        txt_newpas.delete(0, END)
        txt_cpas.delete(0, END)
        txt_newpas.focus()
    else:  
        cid = currentuser["user_id"]
        sql = '''UPDATE User SET user_password = (%s), user_firstLogin = 0 WHERE user_id = (%s)'''
        cursor.execute(sql, (new, cid))
        cursor.connection.commit()
        if cursor.rowcount > 0:
            # Update the current user data
            sql = '''SELECT * FROM User WHERE user_id = (%s)'''
            cursor.execute(sql, (cid))
            result_details = cursor.fetchone()
            currentuser["user_id"] = result_details[0]
            currentuser["user_firstname"] = result_details[1]
            currentuser["user_lastname"] = result_details[2]
            currentuser["user_password"] = result_details[3]
            currentuser["user_addressline"] = result_details[4]
            currentuser["user_city"] = result_details[5]
            currentuser["user_state"] = result_details[6]
            currentuser["user_postcode"] = result_details[7]
            currentuser["user_email"] = result_details[8]
            currentuser["user_phone"] = result_details[9]
            currentuser["user_role"] = result_details[10]
            currentuser["user_firstlogin"] = result_details[12]
            messagebox.showinfo("Change Password Successful", "Your temporary password had been replaced with the new password!")
            mainWindow.attributes('-disabled', 0)
            wel.destroy() # Close the interface
        # If error
        else:
            messagebox.showerror("Change Passord Failed", "Error occured in server! Please check with devloper in order to use the system!")
            logout()  

# Do nothing function
def disable_event():
   pass
        
#==============================================================================================#
#                                        Login Page                                            #
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
btn_login = Button(root, text="Login Account", command=lambda:login(), font=("Lato bold", int(16*ratio)), height=2, fg="white", bg="#1267AC", relief=RAISED, activebackground="#0E4470", activeforeground="white")
btn_login.grid(row=7, column=1, sticky="nsew", padx=int(100*ratio), pady=(int(70*ratio),int(40*ratio)))
lbl_reg = Label(root, text="Don't have account? Please contact company's Admin", font=("Lato", int(12*ratio)), bg="#EDF1F7")
lbl_reg.grid(row=8, column=1, sticky="w", padx=int(100*ratio))


#==============================================================================================#
#                                         Main Page                                            #
#==============================================================================================#

## Main Page Interface
def mainPage():
    global mainWindow
    mainWindow = Toplevel(root)
    mainWindow.title('e-Vision')
    mainWindow.iconbitmap('asset/logo.ico')
    mainWindow.state('zoomed')
    mainWindow.minsize(int(cscreen_width*0.9), int(cscreen_height*0.9))
    # Configure row column attribute
    mainWindow.grid_columnconfigure(0, weight=2)
    mainWindow.grid_columnconfigure(1, weight=1)
    mainWindow.grid_columnconfigure(2, weight=2)
    mainWindow.grid_columnconfigure(3, weight=0)
    mainWindow.grid_columnconfigure(4, weight=0)
    mainWindow.grid_rowconfigure(0, weight=0)
    mainWindow.grid_rowconfigure(1, weight=0)
    mainWindow.grid_rowconfigure(2, weight=4)
    mainWindow.grid_rowconfigure(3, weight=0)
    mainWindow.grid_rowconfigure(4, weight=0)
    mainWindow.grid_rowconfigure(5, weight=0)
    mainWindow.grid_rowconfigure(6, weight=0)
    mainWindow.grid_rowconfigure(7, weight=0)
    mainWindow.grid_rowconfigure(8, weight=0)
    # Setup frames
    left_frame = Frame(mainWindow, width=int(cscreen_width*0.78), height=int(cscreen_height), bg="#EDF1F7")
    left_frame.grid(row=0, column=0, rowspan=9, columnspan=3, sticky="nsew")
    right_frame = Frame(mainWindow, width=int(cscreen_width*0.22), height=int(cscreen_height), bg="#1D253D")
    right_frame.grid(row=0, column=3, rowspan=9, columnspan=2, sticky="nsew")
    # Left components
    video_player = Frame(mainWindow, bg="white", highlightbackground="black", highlightthickness=1)
    video_player.grid(row=0, column=0, rowspan=8, columnspan=3, sticky="nsew", padx=int(25*ratio), pady=(int(30*ratio), int(15*ratio)))
    if(currentuser["user_role"] == 1):
        btn_frame1 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame1.grid(row=8, column=0, sticky="nsew")
        btn_mnguser = Button(btn_frame1, text="Manage User", font=("Lato bold", int(12*ratio)), height=1, width=int(25*ratio), fg="white", bg="#364052", relief=RAISED, activebackground="#1D232D", activeforeground="white")
        btn_mnguser.pack(pady=(int(10*ratio), int(30*ratio)))
        btn_frame2 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame2.grid(row=8, column=1, sticky="nsew")
        btn_mngcamera = Button(btn_frame2, text="Manage Camera", font=("Lato bold", int(12*ratio)), height=1, width=int(25*ratio), fg="white", bg="#364052", relief=RAISED, activebackground="#1D232D", activeforeground="white")
        btn_mngcamera.pack(pady=(int(10*ratio), int(30*ratio)))
        btn_frame3 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame3.grid(row=8, column=2, sticky="nsew")
        btn_asscamera = Button(btn_frame3, text="Assign Camera", font=("Lato bold", int(12*ratio)), height=1, width=int(25*ratio), fg="white", bg="#364052", relief=RAISED, activebackground="#1D232D", activeforeground="white")
        btn_asscamera.pack(pady=(int(10*ratio), int(30*ratio)))
    else:
        btn_frame1 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame1.grid(row=8, column=0, sticky="nsew", pady=(int(10*ratio), int(50*ratio)))
        btn_frame2 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame2.grid(row=8, column=1, sticky="nsew")
        btn_frame3 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame3.grid(row=8, column=2, sticky="nsew")
    # Right components
    img = Image.open('asset/logo.png')
    img = img.resize((int(img.size[0]/1.35), int(img.size[0]/1.35)))
    img = ImageTk.PhotoImage(img)
    img_label = Label(mainWindow, image=img, bg="#1D253D")
    img_label.image = img
    img_label.grid(column=3, row=0, columnspan=2, sticky="nsew", pady=(int(30*ratio), int(5*ratio)))
    btn_frame4 = Frame(mainWindow, bg="#1D253D")
    btn_frame4.grid(row=1, column=3, sticky="nse", padx=int(5*ratio))
    btn_profile = Button(btn_frame4, text="Profile", command=lambda:profilePage(), font=("Lato bold", int(13*ratio)), height=1, width=int(15*ratio), fg="white", bg="#5869F0", relief=FLAT, activebackground="#414EBB", activeforeground="white")
    btn_profile.pack(pady=int(10*ratio))
    btn_frame5 = Frame(mainWindow, bg="#1D253D")
    btn_frame5.grid(row=1, column=4, sticky="nsw", padx=int(5*ratio))
    btn_logout = Button(btn_frame5, text="Logout", command=lambda:logout(), font=("Lato bold", int(13*ratio)), height=1, width=int(15*ratio), fg="white", bg="#FF0000", relief=FLAT, activebackground="#B50505", activeforeground="white")
    btn_logout.pack(pady=int(10*ratio))
    notebookstyle = ttk.Style()
    notebookstyle.theme_use('default')
    notebookstyle.configure('TNotebook', background="#1D253D", borderwidth=1, relief=FLAT)
    notebookstyle.configure('TNotebook.Tab', font=("Lato bold", int(11*ratio)), background="#34415B", borderwidth=1, relief=FLAT, foreground="white", width=int(20*ratio), padding=(int(32*ratio),int(5*ratio),int(-30*ratio),int(5*ratio)))
    notebookstyle.map("TNotebook.Tab", background=[("selected", "#8D9EC1")])
    notebookstyle.layout("Tab",
    [('Notebook.tab', {'sticky': 'nswe', 'children':
        [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
            [('Notebook.label', {'side': 'top', 'sticky': ''})],
        })],
    })]
    )
    acci_tab = ttk.Notebook(mainWindow)
    acci_tab.grid(row=2, column=3, columnspan=2, sticky="nsew", padx=int(30*ratio))
    new_accif = Frame(acci_tab, bg="#34415B")
    history_accif = Frame(acci_tab, bg="#34415B")
    new_accif.pack(fill="both", expand=1)
    history_accif.pack(fill="both", expand=1)
    acci_tab.add(new_accif, text="Unreviewed List")
    acci_tab.add(history_accif, text="Accidents History")
    # to be continued...
    btn_frame6 = Frame(mainWindow, bg="#1D253D")
    btn_frame6.grid(row=3, column=3, columnspan=2, sticky="nsew", padx=5)
    btn_refresh = Button(btn_frame6, text="Refresh Accident List", font=("Lato bold", int(13*ratio)), height=1, width=int(32*ratio), fg="white", bg="#5869F0", relief=FLAT, activebackground="#414EBB", activeforeground="white")
    btn_refresh.pack(pady=int(10*ratio))
    btn_frame7 = Frame(mainWindow, bg="#1D253D")
    btn_frame7.grid(row=4, column=3, sticky="nse", padx=int(5*ratio))
    btn_init = Button(btn_frame7, text="Initiate", font=("Lato bold", int(13*ratio)), height=1, width=int(15*ratio), fg="white", bg="#5869F0", relief=FLAT, activebackground="#414EBB", activeforeground="white")
    btn_init.pack()
    btn_frame8 = Frame(mainWindow, bg="#1D253D")
    btn_frame8.grid(row=4, column=4, sticky="nsw", padx=int(5*ratio))
    btn_stop = Button(btn_frame8, text="Stop", font=("Lato bold", int(13*ratio)), height=1, width=int(15*ratio), fg="white", bg="#5869F0", relief=FLAT, activebackground="#414EBB", activeforeground="white")
    btn_stop.pack()
    camera_list = Label(mainWindow, text="Camera List: ", font=("Lato", int(13*ratio)), bg="#1D253D", fg="white")
    camera_list.grid(row=5, column=3, columnspan=2, sticky="w", padx=int(45*ratio), pady=(int(5*ratio),0))
    camera_id = Label(mainWindow, text="Camera ID: ", font=("Lato", int(13*ratio)), bg="#1D253D", fg="white")
    camera_id.grid(row=6, column=3, columnspan=2, sticky="w", padx=int(45*ratio))
    camera_loc = Label(mainWindow, text="Location: ", font=("Lato", int(13*ratio)), bg="#1D253D", fg="white")
    camera_loc.grid(row=7, column=3, columnspan=2, sticky="w", padx=int(45*ratio), pady=(0,int(5*ratio)))
    btn_frame9 = Frame(mainWindow, bg="#1D253D")
    btn_frame9.grid(row=8, column=3, sticky="nse", padx=int(5*ratio))
    icon_prev = Image.open('asset/previous_icon.png')
    icon_prev = icon_prev.resize((int(30*ratio),int(30*ratio)), Image.ANTIALIAS)
    icon_prev = ImageTk.PhotoImage(icon_prev)
    btn_prev = Button(btn_frame9, image=icon_prev, height=int(30*ratio), width=int(150*ratio), bg="#5869F0", relief=FLAT, activebackground="#414EBB")
    btn_prev.image = icon_prev
    btn_prev.pack()
    btn_frame10 = Frame(mainWindow, bg="#1D253D")
    btn_frame10.grid(row=8, column=4, sticky="nsw", padx=int(5*ratio))
    icon_next = Image.open('asset/next_icon.png')
    icon_next = icon_next.resize((int(30*ratio),int(30*ratio)), Image.ANTIALIAS)
    icon_next = ImageTk.PhotoImage(icon_next)
    btn_next = Button(btn_frame10, image=icon_next, height=int(30*ratio), width=int(150*ratio), bg="#5869F0", relief=FLAT, activebackground="#414EBB")
    btn_next.image = icon_next
    btn_next.pack()
    mainWindow.protocol("WM_DELETE_WINDOW", logout) # If click on close button of window
    # Check for first time login
    if(currentuser["user_firstlogin"]==1):
        mainWindow.attributes('-disabled', 1)
        global txt_cpas, txt_newpas, wel
        wel = Toplevel(mainWindow)
        wel.grab_set()
        wel.overrideredirect(True)
        height = int(400*ratio)
        width = int(380*ratio)
        x = (cscreen_width/2)-(width/2)
        y = (cscreen_height/2)-(height/2)
        wel.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
        # Configure row column attribute
        wel.grid_columnconfigure(0, weight=1)
        wel.grid_columnconfigure(1, weight=1)
        wel.grid_rowconfigure(0, weight=0)
        wel.grid_rowconfigure(1, weight=0)
        wel.grid_rowconfigure(2, weight=0)
        wel.grid_rowconfigure(3, weight=0)
        wel.grid_rowconfigure(4, weight=0)
        fr = Frame(wel, highlightbackground="black", highlightthickness=1, bg="white")
        fr.grid(row=0, column=0, rowspan=5, columnspan=2, sticky="nsew")
        wel_lbl = Label(wel, text="Welcome!", font=("Lato bold", int(18*ratio)), bg="white")
        wel_lbl.grid(row=0, column=0, padx=int(25*ratio), pady=(int(25*ratio), int(10*ratio)), sticky="nsw")
        f1 = Frame(wel, bg="white")
        f1.grid(row=1, column=0, columnspan=2, padx=int(25*ratio), sticky="nsew")
        desc_lbl = Text(f1, font=("Lato", int(12*ratio)), bg="white", wrap=WORD, highlightthickness=0, height=5, relief=FLAT)
        desc_lbl.pack()
        desc_lbl.insert(INSERT, "To make your account secure, please create a new password to replace the temporary password given initially. (At least 8 characters with minimum one special character and one uppercase letter)")
        desc_lbl.configure(state="disabled")
        wel_lbl = Label(wel, text="New Password", font=("Lato bold", int(13*ratio)), bg="white")
        wel_lbl.grid(row=2, column=0, padx=(int(25*ratio) ,0), pady=(int(30*ratio), int(10*ratio)), sticky="nsw")
        wel_lbl = Label(wel, text="Confirm Password", font=("Lato bold", int(13*ratio)), bg="white")
        wel_lbl.grid(row=3, column=0, padx=(int(25*ratio), 0), pady=(int(10*ratio), int(30*ratio)), sticky="nsw")
        txt_newpas = Entry(wel, font=("Lato", int(12*ratio)), relief=FLAT, highlightthickness=2, show="*")
        txt_newpas.grid(row=2, column=1, sticky="nsw", padx=(int(10*ratio), int(25*ratio)), pady=(int(30*ratio), int(10*ratio)))
        txt_cpas = Entry(wel, font=("Lato", int(12*ratio)), relief=FLAT, highlightthickness=2, show="*")
        txt_cpas.grid(row=3, column=1, sticky="nsw", padx=(int(10*ratio), int(25*ratio)), pady=(int(10*ratio), int(30*ratio)))
        btn_save = Button(wel, command=lambda:firstchange(), text="Save", font=("Lato bold", int(15*ratio)), height=1, fg="white", bg="#1F5192", relief=RAISED, activebackground="#173B6A", activeforeground="white")
        btn_save.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=int(25*ratio),  pady=(int(5*ratio), int(40*ratio)))
    
    
#==============================================================================================#
#                                         Profile Page                                         #
#==============================================================================================#

## Profile Page Interface
def profilePage():
    global profileWindow
    mainWindow.withdraw()
    profileWindow = Toplevel(mainWindow)
    profileWindow.title('e-Vision My Profile')
    profileWindow.iconbitmap('asset/logo.ico')
    height = int(700*ratio)
    width = int(1150*ratio)
    x = (cscreen_width/2)-(width/2)
    y = (cscreen_height/2)-(height/2)
    profileWindow.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
    profileWindow.resizable(False, False)
    profileWindow.protocol("WM_DELETE_WINDOW", disable_event)
    # Configure row column attribute
    profileWindow.grid_columnconfigure(0, weight=1)
    profileWindow.grid_columnconfigure(1, weight=2)
    profileWindow.grid_columnconfigure(2, weight=2)
    profileWindow.grid_rowconfigure(0, weight=1)
    profileWindow.grid_rowconfigure(1, weight=1)
    profileWindow.grid_rowconfigure(2, weight=1)
    profileWindow.grid_rowconfigure(3, weight=0)
    profileWindow.grid_rowconfigure(4, weight=1)
    profileWindow.grid_rowconfigure(5, weight=0)
    profileWindow.grid_rowconfigure(6, weight=2)
    profileWindow.grid_rowconfigure(7, weight=3)
    # Setup frames
    left_frame = Frame(profileWindow, width=int(cscreen_width*0.18), height=int(cscreen_height), bg="#222222")
    left_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")
    right_frame = Frame(profileWindow, width=int(cscreen_width*0.4), height=int(cscreen_height), bg="#EDF1F7")
    right_frame.grid(row=0, column=1, rowspan=8, columnspan=2, sticky="nsew")
    # Left components
    btn_frame1 = Frame(profileWindow, bg="#222222")
    btn_frame1.grid(row=0, column=0, sticky="nsw", padx=int(10*ratio), pady=int(10*ratio))
    icon_back = Image.open('asset/back.png')
    icon_back = icon_back.resize((int(65*ratio),int(65*ratio)), Image.ANTIALIAS)
    icon_back = ImageTk.PhotoImage(icon_back)
    btn_next = Button(btn_frame1, image=icon_back, height=int(65*ratio), width=int(65*ratio), bg="#222222", relief=FLAT, bd=0, highlightthickness=0, activebackground="#222222")
    btn_next.image = icon_back
    btn_next.pack()

root.mainloop()