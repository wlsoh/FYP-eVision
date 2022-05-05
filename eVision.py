# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Main GUI Integration
# Date Created: 05/05/2022
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
from ctypes import windll
import pymysql
import pymysql
from pymysql.constants import CLIENT
import re
from datetime import datetime
import os
import io
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from Google import Create_Service
import pandas as pd

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
# Connection with Google Cloud using Auth2.0
CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
folder_id = '18aJTxbazV-zxcygJQ4E9qIu1f1bwAAWH'
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
            loading(root)
            root.update()
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
                'user_avatar': result_detail[11],
                'user_lastlogin': result_detail[12],
                'user_firstlogin': result_detail[13]
            }
            now = datetime.now() # Get current date time
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            sql = '''UPDATE User SET user_lastlogin_datetime = (%s) WHERE user_id = (%s)''' # Update last login
            cursor.execute(sql, (dt_string, currentuser["user_id"]))
            cursor.connection.commit()
            currentuser["user_lastlogin"] = dt_string
            # Get avatar
            getimg(currentuser["user_avatar"])
            root.attributes('-disabled', 0)
            loading_splash.destroy()
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
        currentuser.clear() # Set user session to empty
        # Clear all files in temp folder
        dir = './temp'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        mainWindow.destroy() # Destroy current winfow
        root.deiconify() # Show login page again
        root.state('zoomed')
        
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

# Back to main function
def backmain(cur):
    cur.withdraw()
    mainWindow.deiconify()
    mainWindow.state('zoomed')

# Download image from cloud storage function
def getimg(fileid):
    # Download the uploaded file
    file_ids = [fileid]
    file_names = [fileid + '.png']

    for file_id, file_name in zip(file_ids, file_names):
        request = service.files().get_media(fileId=file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fd=fh, request=request)
        done = False
        
        while not done:
            status, done = downloader.next_chunk()
            print('Download progress {0}'.format(status.progress()*100))
            
        fh.seek(0)
        with open(os.path.join('./temp', file_name), 'wb') as f:
            f.write(fh.read())
            f.close()
            
# Download video from cloud storage function
def getvideo(fileid):
    # Download the uploaded file
    file_ids = [fileid]
    file_names = [fileid + '.mp4']

    for file_id, file_name in zip(file_ids, file_names):
        request = service.files().get_media(fileId=file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fd=fh, request=request)
        done = False
        
        while not done:
            status, done = downloader.next_chunk()
            print('Download progress {0}'.format(status.progress()*100))
            
        fh.seek(0)
        with open(os.path.join('./temp', file_name), 'wb') as f:
            f.write(fh.read())
            f.close()         

# Upload image to cloud storage function
def uploadimg(filepath):
    # Upload a file to folder
    file_names = [filepath]
    mime_types = ['image/jpg ']

    for file_name, mime_type in zip(file_names, mime_types):
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        media = MediaFileUpload(file_name, mimetype=mime_type)
        
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

# Delete existing file
def deletefile(fileid):
    file_id = fileid
    if(file_id != "1cqBLIEBhkWQ1qmRSi1UehZ7pYKeGQm8e"):
        service.files().delete(fileId=file_id).execute()

# Get the latest file ID
def getfilelist():
    # Get list of file
    query = f"parents = '{folder_id}'"
    response = service.files().list(q=query).execute()
    files = response.get('files')
    nextPageToken = response.get('nextPageToken')

    while nextPageToken:
        response = service.files().list(q=query, pageToken=nextPageToken).execute()
        files.extend(response.get('files'))
        nextPageToken = response.get('nextPageToken')
        
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.min_rows', 500)
    pd.set_option('display.max_colwidth', 150)
    pd.set_option('display.width', 200)
    pd.set_option('expand_frame_repr', True)
    df = pd.DataFrame(files)
    # print(df)
    # print(df.iloc[0,1])
    return df.iloc[0,1]

# Loading screen function
def loading(win):
    global loading_splash, frame_loading
    
    win.attributes('-disabled', 1)
    loading_splash = Toplevel(root)
    loading_splash.grab_set()
    loading_splash.overrideredirect(True)
    height = int(150*ratio)
    width = int(400*ratio)
    x = (cscreen_width/2)-(width/2)
    y = (cscreen_height/2)-(height/2)
    loading_splash.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
    frame_loading = Frame(loading_splash, width=width, height=height, bg="#242426")
    frame_loading.pack()
    Label(frame_loading, text="Loading...", font="Bahnschrift 15", bg="#242426", fg='#FFBD09').place(x=int(152*ratio), y=int(35*ratio))
    Label(frame_loading, text="Please wait...", font="Bahnschrift 15", bg="#242426", fg='#FFBD09').place(x=int(135*ratio), y=int(70*ratio))

# Upload avatar function
def upload_avatar():
    file = askopenfile(parent=profileWindow, mode='rb', title='Choose a image file', filetypes=[("PNG", "*.png"),("JPG", "*.jpg")])
    if not file:
        pass
    else:
        size = os.path.getsize(file.name)
        # Limit file size as 20mb max
        if size > 20971520:
            messagebox.showerror("Avatar Upload Failed", "The avatar image should not be exceeding 20MB!")
        else:
            loading(profileWindow)
            profileWindow.update()
            uploadimg(file.name)
            temp_id = getfilelist()
            deletefile(currentuser["user_avatar"])
            sql = '''UPDATE User SET user_avatar = (%s) WHERE user_id = (%s)''' # Update user avatar
            cursor.execute(sql, (temp_id, currentuser["user_id"]))
            cursor.connection.commit()
            currentuser["user_avatar"] = temp_id
            getimg(currentuser["user_avatar"]) # Download the new avatar to temp
            avatar_path = 'temp/' + currentuser["user_avatar"] + '.png' # Display new avatar
            img_avatar = Image.open(avatar_path)
            img_avatar = img_avatar.resize((int(200*ratio),int(200*ratio)), Image.ANTIALIAS)
            img_avatar = ImageTk.PhotoImage(img_avatar)
            imgava_label.configure(image=img_avatar)
            imgava_label.image = img_avatar
            profileWindow.attributes('-disabled', 0)
            loading_splash.destroy()
            messagebox.showinfo("Avatar Upload Successful", "Your new avatar image had been successfully replaced!")
        
        
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
        desc_lbl = Text(f1, font=("Lato", int(12*ratio)), bg="white", wrap=WORD, highlightthickness=0, height=int(5*ratio), relief=FLAT)
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
    profileWindow.grid_columnconfigure(0, weight=0)
    profileWindow.grid_columnconfigure(1, weight=1)
    profileWindow.grid_columnconfigure(2, weight=1)
    profileWindow.grid_rowconfigure(0, weight=0)
    profileWindow.grid_rowconfigure(1, weight=0)
    profileWindow.grid_rowconfigure(2, weight=1)
    profileWindow.grid_rowconfigure(3, weight=0)
    profileWindow.grid_rowconfigure(4, weight=0)
    profileWindow.grid_rowconfigure(5, weight=0)
    profileWindow.grid_rowconfigure(6, weight=1)
    profileWindow.grid_rowconfigure(7, weight=3)
    # Setup frames
    left_frame = Frame(profileWindow, width=int(cscreen_width*0.17), height=int(cscreen_height), bg="#222222")
    left_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")
    right_frame = Frame(profileWindow, width=int(cscreen_width*0.43), height=int(cscreen_height), bg="#EDF1F7")
    right_frame.grid(row=0, column=1, rowspan=8, columnspan=2, sticky="nsew")
    # Left components
    btn_frame1 = Frame(profileWindow, bg="#222222")
    btn_frame1.grid(row=0, column=0, sticky="nsw", padx=int(10*ratio), pady=int(10*ratio))
    icon_back = Image.open('asset/back.png')
    icon_back = icon_back.resize((int(65*ratio),int(65*ratio)), Image.ANTIALIAS)
    icon_back = ImageTk.PhotoImage(icon_back)
    btn_back = Button(btn_frame1, command=lambda:backmain(profileWindow), image=icon_back, height=int(65*ratio), width=int(65*ratio), bg="#222222", relief=FLAT, bd=0, highlightthickness=0, activebackground="#222222")
    btn_back.image = icon_back
    btn_back.pack()
    avatar_path = 'temp/' + currentuser["user_avatar"] + '.png'
    img_avatar = Image.open(avatar_path)
    img_avatar = img_avatar.resize((int(200*ratio),int(200*ratio)), Image.ANTIALIAS)
    img_avatar = ImageTk.PhotoImage(img_avatar)
    global imgava_label
    imgava_label = Label(profileWindow, image=img_avatar, bg="#222222")
    imgava_label.image = img_avatar
    imgava_label.grid(column=0, row=1, rowspan=2, sticky="nsew")
    page_title = Label(profileWindow, text="Personal Info", font=("Lato bold", int(18*ratio)), bg="#222222", fg="white")
    page_title.grid(row=3, column=0, sticky="nsew", pady=int(10*ratio))
    btn_frame2 = Frame(profileWindow, bg="#222222")
    btn_frame2.grid(row=4, column=0, sticky="nsew")
    btn_upload = Button(btn_frame2, command=lambda:upload_avatar(), text="Upload New Avatar", font=("Lato bold", int(12*ratio)), height=1, width=int(18*ratio), fg="white", bg="#1F5192", relief=FLAT, activebackground="#173B6A", activeforeground="white")
    btn_upload.pack()
    # Right components
    sys_label = Label(profileWindow, text="e-Vision", font=("Lato bold", int(14*ratio)), bg="#EDF1F7", fg="black")
    sys_label.grid(row=0, column=2, sticky="ne", padx=int(30*ratio), pady=int(15*ratio))
    name_label = Label(profileWindow, text="{}".format(currentuser["user_firstname"]+" "+currentuser["user_lastname"]), font=("Lato bold", int(32*ratio)), bg="#EDF1F7", fg="#05009B")
    name_label.grid(row=1, column=1, sticky="sw", padx=(int(35*ratio), 0), pady=(int(30*ratio), 0))
    if currentuser["user_role"]==1:
        txt = 'Admin'
    else:
        txt = 'Monitoring Employee'
    role_label = Label(profileWindow, text="{}".format(txt), font=("Lato", int(15*ratio)), bg="#EDF1F7", fg="black")
    role_label.grid(row=2, column=1, sticky="nw", padx=(int(35*ratio), 0))
    uid_label = Label(profileWindow, text="User ID", font=("Lato bold", int(16*ratio)), bg="#EDF1F7", fg="black")
    uid_label.grid(row=3, column=1, sticky="sw", padx=(int(35*ratio), 0))
    uid_con = Label(profileWindow, text="{}".format(currentuser["user_id"]), font=("Lato", int(14*ratio)), bg="#EDF1F7", fg="black")
    uid_con.grid(row=4, column=1, sticky="nw", padx=(int(35*ratio), 0))
    add_label = Label(profileWindow, text="Address", font=("Lato bold", int(16*ratio)), bg="#EDF1F7", fg="black")
    add_label.grid(row=5, column=1, sticky="sw", padx=(int(35*ratio), 0), pady=(int(40*ratio),0))
    f1 = Frame(profileWindow, bg="#EDF1F7")
    f1.grid(row=6, column=1, padx=(int(35*ratio), 0), sticky="nsw")
    add_con = Text(f1, font=("Lato", int(14*ratio)), bg="#EDF1F7", fg="black", wrap=WORD, highlightthickness=0, height=int(5*ratio), width=int(25*ratio), relief=FLAT)
    add_con.pack()
    add_con.insert(INSERT, "{}, {} {}, {}.".format(currentuser["user_addressline"], currentuser["user_postcode"], currentuser["user_city"], currentuser["user_state"]))
    add_con.configure(state="disabled")
    email_label = Label(profileWindow, text="Email", font=("Lato bold", int(16*ratio)), bg="#EDF1F7", fg="black")
    email_label.grid(row=3, column=2, sticky="sw", padx=(0, int(35*ratio)))
    email_con = Label(profileWindow, text="{}".format(currentuser["user_email"]), font=("Lato", int(14*ratio)), bg="#EDF1F7", fg="black")
    email_con.grid(row=4, column=2, sticky="nw", padx=(0, int(35*ratio)))
    phone_label = Label(profileWindow, text="Phone Number", font=("Lato bold", int(16*ratio)), bg="#EDF1F7", fg="black")
    phone_label.grid(row=5, column=2, sticky="sw", padx=(0, int(35*ratio)), pady=(int(40*ratio),0))
    phone_con = Label(profileWindow, text="{}".format(currentuser["user_phone"]), font=("Lato", int(14*ratio)), bg="#EDF1F7", fg="black")
    phone_con.grid(row=6, column=2, sticky="nw", padx=(0, int(35*ratio)))
    btn_frame3 = Frame(profileWindow, bg="#EDF1F7")
    btn_frame3.grid(row=7, column=1, sticky="nse", padx=int(80*ratio))
    btn_edit = Button(btn_frame3, text="Edit Profile", font=("Lato bold", int(12*ratio)), height=1, width=int(20*ratio), fg="white", bg="#1F5192", relief=RAISED, activebackground="#173B6A", activeforeground="white")
    btn_edit.pack()
    btn_frame4 = Frame(profileWindow, bg="#EDF1F7")
    btn_frame4.grid(row=7, column=2, sticky="nsw")
    btn_chgpas = Button(btn_frame4, text="Change Password", font=("Lato bold", int(12*ratio)), height=1, width=int(20*ratio), fg="black", bg="white", relief=RAISED, activebackground="#DCDCDC", activeforeground="black")
    btn_chgpas.pack()

root.mainloop()