# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Main GUI Integration
# Date Created: 05/05/2022
import os
import io
import re
from cv2 import exp
import pymysql
import pandas as pd
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
from ctypes import windll
from pymysql.constants import CLIENT
from datetime import datetime
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from Google import Create_Service


#==============================================================================================#
#                                 Connection & Initial Setup                                   #
#==============================================================================================#
# Prevent blur due to screen scale setting
windll.shcore.SetProcessDpiAwareness(1) 
# Regex for validation
pare = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")
emailregex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
phoneregex = "^(\+?6?01)[02-46-9]-*[0-9]{7}$|^(\+?6?01)[1]-*[0-9]{8}$"

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
#                                         Classes                                              #
#==============================================================================================#
# Login session class
class Usersession:
    def __init__(self, uid, ufname, ulname, upass, uadd, ucity, ustate, upost, uemail, uphone, urole, uavatar, ullogin, uflogin):
        self.user_id = uid
        self.user_firstname = ufname
        self.user_lastname = ulname
        self.user_password = upass
        self.user_addressline = uadd
        self.user_city = ucity
        self.user_state = ustate
        self.user_postcode = upost
        self.user_email = uemail
        self.user_phone = uphone
        self.user_role = urole
        self.user_avatar = uavatar
        self.user_lastlogin = ullogin
        self.user_firstlogin = uflogin
        
    # First time change password function
    def firstchange(self, newf, conf):
        new = newf.get()
        con = conf.get()
        
        # If both fields empty
        if len(new) == 0 & len(con) == 0:
            messagebox.showerror("Change Password Failed", "The fields were empty! Please fill in the valid new password and confirm password values!")
            newf.focus()
        # If new pass field empty
        elif len(new) == 0:
            messagebox.showerror("Change Password Failed", "The new password fields were empty! Please fill in the valid new password values!")
            newf.focus()
        # If confirm pass field empty
        elif len(con) == 0:
            messagebox.showerror("Change Password Failed", "The confirm password fields were empty! Please fill in the valid confirm password values!")
            conf.focus()
        # If new pass and confirm pass not same
        elif (new != con):
            messagebox.showerror("Change Password Failed", "The values for new password field and confirm password field are not identical!")
            newf.delete(0, END)
            conf.delete(0, END)
            newf.focus()
        # If new password not exceed range
        elif (len(new) > 127):
            messagebox.showerror("Change Password Failed", "The values for new password exceed acceptable length range!")
            newf.delete(0, END)
            conf.delete(0, END)
            newf.focus()
        # If new password same with current password
        elif (new == self.user_password):
            messagebox.showerror("Change Password Failed", "The new password should not be same with existing password!")
            newf.delete(0, END)
            conf.delete(0, END)
            newf.focus()
        # If new password not satisfied the requirement
        elif (re.fullmatch(pare, new)==None):
            messagebox.showerror("Change Password Failed", "The values for new password must be at least 8 characters with minimum one special character, one number and both uppercase & lowercase letter!")
            newf.delete(0, END)
            conf.delete(0, END)
            newf.focus()
        else:  
            cid = self.user_id
            sql = '''UPDATE User SET user_password = (%s), user_firstLogin = 0 WHERE user_id = (%s)'''
            cursor.execute(sql, (new, cid))
            cursor.connection.commit()
            if cursor.rowcount > 0:
                # Update the current user data
                sql = '''SELECT * FROM User WHERE user_id = (%s)'''
                cursor.execute(sql, (cid))
                result_details = cursor.fetchone()
                self.user_id = result_details[0]
                self.user_firstname = result_details[1]
                self.user_lastname = result_details[2]
                self.user_password = result_details[3]
                self.user_addressline = result_details[4]
                self.user_city = result_details[5]
                self.user_state = result_details[6]
                self.user_postcode = result_details[7]
                self.user_email = result_details[8]
                self.user_phone = result_details[9]
                self.user_role = result_details[10]
                self.user_firstlogin = result_details[12]
                messagebox.showinfo("Change Password Successful", "Your temporary password had been replaced with the new password!")
                mainWindow.attributes('-disabled', 0)
                wel.destroy() # Close the interface
                mainWindow.focus_force()
            # If error
            else:
                messagebox.showerror("Change Passord Failed", "An error had occured in database server! Please contact developer for help!")
                logout()
                
    # Upload avatar function
    def upload_avatar(self, loc):
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
                deletefile(self.user_avatar)
                sql = '''UPDATE User SET user_avatar = (%s) WHERE user_id = (%s)''' # Update user avatar
                cursor.execute(sql, (temp_id, self.user_id))
                cursor.connection.commit()
                if cursor.rowcount > 0:
                    self.user_avatar = temp_id
                    getimg(self.user_avatar) # Download the new avatar to temp
                    avatar_path = 'temp/' + self.user_avatar + '.png' # Display new avatar
                    img_avatar = Image.open(avatar_path)
                    img_avatar = img_avatar.resize((round(200*ratio),round(200*ratio)), Image.ANTIALIAS)
                    img_avatar = ImageTk.PhotoImage(img_avatar)
                    loc.configure(image=img_avatar)
                    loc.image = img_avatar
                    profileWindow.attributes('-disabled', 0)
                    loading_splash.destroy()
                    messagebox.showinfo("Avatar Upload Successful", "Your new avatar image had been successfully replaced!")
                else:
                    profileWindow.attributes('-disabled', 0)
                    loading_splash.destroy()
                    messagebox.showerror("Avatar Upload Failed", "An error had occured in database server! Please contact developer for help!")
                
    # Update password function
    def updatepass(self, oldf, newf, conf):
        confirmbox = messagebox.askquestion('Password Change Confirmation', 'Are you sure to change your password?', icon='warning')
        if confirmbox == 'yes':
            old = oldf.get()
            new = newf.get()
            con = conf.get()
            
            # If both fields empty
            if len(new) == 0 & len(con) == 0 & len(old) == 0:
                messagebox.showerror("Change Password Failed", "The fields were empty! Please fill in the valid new password and confirm password values!")
                newf.focus()
            # If new pass field empty
            elif len(new) == 0:
                messagebox.showerror("Change Password Failed", "The new password fields were empty! Please fill in the valid new password values!")
                newf.focus()
            # If confirm pass field empty
            elif len(con) == 0:
                messagebox.showerror("Change Password Failed", "The confirm password fields were empty! Please fill in the valid confirm password values!")
                conf.focus()
            # If new pass and confirm pass not same
            elif (new != con):
                messagebox.showerror("Change Password Failed", "The values for new password field and confirm password field are not identical!")
                newf.delete(0, END)
                conf.delete(0, END)
                newf.focus()
            # If new password not exceed range
            elif (len(new) > 127):
                messagebox.showerror("Change Password Failed", "The values for new password exceed acceptable length range (127)!")
                oldf.delete(0, END)
                newf.delete(0, END)
                conf.delete(0, END)
                oldf.focus()
            # If new password not satisfied the requirement
            elif (re.fullmatch(pare, new)==None):
                messagebox.showerror("Change Password Failed", "The values for new password must be at least 8 characters with minimum one special character, one number and both uppercase & lowercase letter!")
                oldf.delete(0, END)
                newf.delete(0, END)
                conf.delete(0, END)
                oldf.focus()
            # If old password incorrect
            elif (old != self.user_password):
                messagebox.showerror("Change Password Failed", "Incorrect current password!")
                oldf.delete(0, END)
                newf.delete(0, END)
                conf.delete(0, END)
                oldf.focus()
            # If new password same with current password
            elif (new == self.user_password):
                messagebox.showerror("Change Password Failed", "The new password should not be same with existing password!")
                oldf.delete(0, END)
                newf.delete(0, END)
                conf.delete(0, END)
                oldf.focus()
            else:
                cid = self.user_id
                sql = '''UPDATE User SET user_password = (%s) WHERE user_id = (%s)'''
                cursor.execute(sql, (new, cid))
                cursor.connection.commit()
                if cursor.rowcount > 0:
                    # Update the current user data
                    sql = '''SELECT * FROM User WHERE user_id = (%s)'''
                    cursor.execute(sql, (cid))
                    result_details = cursor.fetchone()
                    self.user_id = result_details[0]
                    self.user_firstname = result_details[1]
                    self.user_lastname = result_details[2]
                    self.user_password = result_details[3]
                    self.user_addressline = result_details[4]
                    self.user_city = result_details[5]
                    self.user_state = result_details[6]
                    self.user_postcode = result_details[7]
                    self.user_email = result_details[8]
                    self.user_phone = result_details[9]
                    self.user_role = result_details[10]
                    self.user_firstlogin = result_details[12]
                    messagebox.showinfo("Change Password Successful", "Your had successfully updated your password!")
                    profileWindow.attributes('-disabled', 0)
                    updpassWindow.destroy() # Close the interface
                    profileWindow.focus_force()
                # If error
                else:
                    messagebox.showerror("Change Passord Failed", "An error had occured in database server! Please contact developer for help!")
                    oldf.delete(0, END)
                    newf.delete(0, END)
                    conf.delete(0, END)
                    newf.focus()
                    
    # Update profile details function
    def updateprofile(self, uf, ul, ad, ci, st, po, em, ph):
        confirmbox = messagebox.askquestion('Profile Update Confirmation', 'Are you sure to update your personal details with current information?', icon='warning')
        if confirmbox == 'yes':
            if not (len(po.get()) == 5):
                messagebox.showerror("Update Profile Failed", "The postcode should have five digits!")
                po.focus()
            else:
                loading(updprofileWindow)
                updprofileWindow.update()
                global email_exist
                email_exist = False
                # Check for email redundancy
                if em.get() != self.user_email:
                    sql = '''SELECT user_email FROM User'''
                    cursor.execute(sql)
                    result = [result[0] for result in cursor.fetchall()]
                    for i in range(len(result)):
                        if result[i] == em.get():
                            loading_splash.destroy()
                            messagebox.showerror("Update Profile Failed", "The new inserted email had been registered previously!")
                            email_exist = True
                            updprofileWindow.attributes('-disabled', 0)
                            updprofileWindow.focus_force()
                            em.focus()
                            break
                # Update profile if exist was false
                if(email_exist == False):
                    input_addline = ad.get()
                    if "," in input_addline[-1]:
                        input_addline = input_addline.rstrip(",")
                    sql = '''UPDATE User SET user_firstname = (%s), user_lastname = (%s), user_addressline = (%s), user_city = (%s), user_state = (%s), user_postcode = (%s), user_email = (%s), user_phone = (%s) WHERE user_id = (%s)''' # Update user info
                    cursor.execute(sql, (uf.get(), ul.get(), input_addline, ci.get(), st.get(), po.get(), em.get(), ph.get(), self.user_id))
                    cursor.connection.commit()
                    if cursor.rowcount > 0:
                    # Update the current user data
                        sql = '''SELECT * FROM User WHERE user_id = (%s)'''
                        cursor.execute(sql, (self.user_id))
                        result_details = cursor.fetchone()
                        self.user_firstname = result_details[1]
                        self.user_lastname = result_details[2]
                        self.user_addressline = result_details[4]
                        self.user_city = result_details[5]
                        self.user_state = result_details[6]
                        self.user_postcode = result_details[7]
                        self.user_email = result_details[8]
                        self.user_phone = result_details[9]
                        loading_splash.destroy()
                        messagebox.showinfo("Personal Info Update Successful", "Your new personal details had been updated!")
                        profileWindow.attributes('-disabled', 0)
                        updprofileWindow.destroy() # Close the interface
                        profileWindow.focus_force()
                        # Update content display
                        canvas.itemconfig(name_label, text="{}".format(self.user_firstname+" "+self.user_lastname))
                        add_con.configure(state=NORMAL)
                        add_con.delete(1.0, END)
                        add_con.insert(END, "{}, {} {}, {}.".format(self.user_addressline, self.user_postcode, self.user_city, self.user_state))
                        add_con.configure(state=DISABLED)
                        email_con.configure(state=NORMAL)
                        email_con.delete(1.0, END)
                        email_con.insert(END, "{}".format(self.user_email))
                        email_con.configure(state=DISABLED)
                        phone_con.configure(state=NORMAL)
                        phone_con.delete(1.0, END)
                        phone_con.insert(END, "{}".format(self.user_phone))
                        phone_con.configure(state=DISABLED)
                        profileWindow.update()
                    # If error
                    else:
                        loading_splash.destroy()
                        messagebox.showerror("Personal Info Update Failed", "An error had occured in database server! Please contact developer for help!")
                        profileWindow.attributes('-disabled', 0)
                        updprofileWindow.destroy() # Close the interface
                        profileWindow.focus_force()  

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

# Tooltip class
class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


#==============================================================================================#
#                                         Functions                                            #
#==============================================================================================#
# Loading screen function
def loading(win):
    global loading_splash, frame_loading
    
    win.attributes('-disabled', 1)
    loading_splash = Toplevel(root)
    loading_splash.grab_set()
    loading_splash.overrideredirect(True)
    height = round(150*ratio)
    width = round(400*ratio)
    x = (cscreen_width/2)-(width/2)
    y = (cscreen_height/2)-(height/2)
    loading_splash.geometry(f'{width}x{height}+{round(x)}+{round(y)}')
    frame_loading = Frame(loading_splash, width=width, height=height, bg="#242426")
    frame_loading.pack()
    Label(frame_loading, text="Loading...", font=("Bahnschrift", round(15*ratio)), bg="#242426", fg='#FFBD09').place(x=round(152*ratio), y=round(35*ratio))
    Label(frame_loading, text="Please wait...", font=("Bahnschrift", round(15*ratio)), bg="#242426", fg='#FFBD09').place(x=round(135*ratio), y=round(70*ratio))

# Dynamically resize login left image
def resize_image(event):
    new_width = event.width
    new_height = event.height
    image = copy_img.resize((new_width, new_height), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    label.config(image = photo)
    label.image = photo #avoid garbage collection

# Hide/Show password function
def showpass():
    if(var1.get() == 1):
        txt_pass.configure(show="")
    else:
        txt_pass.configure(show="*")

# Login function
def login(eloc, ploc):
    uname = eloc.get()
    pas = ploc.get()
    global usession
    
    # If both fields empty
    if len(uname) == 0 & len(pas) == 0:
        messagebox.showerror("Login Failed", "The fields were empty! Please fill in the valid email and password before login again!")
        eloc.focus()
    # If email field empty
    elif len(uname) == 0:
        messagebox.showerror("Login Failed", "The email field was empty! Please fill in the valid email and login again!")
        eloc.focus()
    # If password field empty
    elif len(pas) == 0:
        messagebox.showerror("Login Failed", "The password field was empty! Please fill in the valid password and login again!")
        ploc.focus()
    # If password minimum length not satisfied
    elif len(pas) < 8:
        messagebox.showerror("Login Failed", "The password should not less than 8 characters! Please fill in the valid password and login again!")
        ploc.delete(0, END)
        ploc.focus()
    else:  
        sql = '''SELECT * FROM User WHERE user_email = (%s) AND user_password = (%s)'''
        row_result = cursor.execute(sql, (uname, pas))
        if row_result > 0:
            loading(root)
            root.update()
            result_detail = cursor.fetchone()
            usession = Usersession(
                result_detail[0], 
                result_detail[1], 
                result_detail[2], 
                result_detail[3], 
                result_detail[4], 
                result_detail[5], 
                result_detail[6], 
                result_detail[7], 
                result_detail[8], 
                result_detail[9], 
                result_detail[10], 
                result_detail[11], 
                result_detail[12], 
                result_detail[13]
            )
            now = datetime.now() # Get current date time
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            sql = '''UPDATE User SET user_lastlogin_datetime = (%s) WHERE user_id = (%s)''' # Update last login
            cursor.execute(sql, (dt_string, usession.user_id))
            cursor.connection.commit()
            usession.user_lastlogin = dt_string
            # Get avatar
            getimg(usession.user_avatar)
            root.attributes('-disabled', 0)
            loading_splash.destroy()
            eloc.delete(0, END)
            ploc.delete(0, END)
            eloc.focus()
            messagebox.showinfo("Login Successful", "Hi {0}, welcome back to e-Vision!".format(usession.user_firstname))
            mainPage() # Invoke the main page
            root.withdraw() # Withdraw the login page
        # If no such user found
        else:
            messagebox.showerror("Login Failed", "Invalid email/password! Please try to login again with valid email and password created!")
            eloc.delete(0, END)
            ploc.delete(0, END)
            eloc.focus()
 
# Logout function
def logout():
    confirmbox = messagebox.askquestion('e-Vision Logout', 'Are you sure to logout the system?', icon='warning')
    if confirmbox == 'yes':
        global usession
        del usession # Delete user session
        # Clear all files in temp folder
        dir = './temp'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        mainWindow.destroy() # Destroy current winfow
        root.deiconify() # Show login page again
        root.state('zoomed') 

# Do nothing function
def disable_event():
   pass

# Back to main button function
def backmainbtn(comploc, curwin, bgcol):
    icon_back = Image.open('asset/back.png')
    icon_back = icon_back.resize((round(65*ratio),round(65*ratio)), Image.ANTIALIAS)
    icon_back = ImageTk.PhotoImage(icon_back)
    btn_back = Button(comploc, command=lambda:backmain(curwin), image=icon_back, height=round(65*ratio), width=round(65*ratio), bg=bgcol, relief=FLAT, bd=0, highlightthickness=0, activebackground=bgcol)
    btn_back.image = icon_back
    btn_back.pack()

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

# Show message on tooltip function
def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

# Close update profile page function
def closeupdprofile():
    updprofileWindow.destroy()
    profileWindow.attributes('-disabled', 0)
    profileWindow.focus_force()

# Close change password page function
def closechgpass():
    updpassWindow.destroy()
    profileWindow.attributes('-disabled', 0)
    profileWindow.focus_force()

# Limit first name entry box length function
def fnamevalidation(u_input):
    if len(u_input) > 30: 
        btn_upd.config(state='disabled')  
        fname_label_error.configure(text="Exceed 30 Characters Length Limit!")
        fname_label_error.grid(row=3, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 
    elif len(u_input) > 0 and len(u_input) <= 30:
        fname_label_error.grid_remove()
        if not phone_label_error.grid_info() and not email_label_error.grid_info() and not lname_label_error.grid_info() and not add_label_error.grid_info() and not city_label_error.grid_info(): 
            btn_upd.config(state='normal')  
        return True 
    elif (len(u_input)==0):
        btn_upd.config(state='disabled')  
        fname_label_error.configure(text="Invalid Empty Field!")
        fname_label_error.grid(row=3, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 

# Limit last name entry box length function
def lnamevalidation(u_input):
    if len(u_input) > 30: 
        btn_upd.config(state='disabled')  
        lname_label_error.configure(text="Exceed 30 Characters Length Limit!")
        lname_label_error.grid(row=5, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 
    elif len(u_input) > 0 and len(u_input) <= 30:
        lname_label_error.grid_remove()
        if not phone_label_error.grid_info() and not email_label_error.grid_info() and not fname_label_error.grid_info() and not add_label_error.grid_info() and not city_label_error.grid_info(): 
            btn_upd.config(state='normal')  
        return True 
    elif (len(u_input)==0):
        btn_upd.config(state='disabled')  
        lname_label_error.configure(text="Invalid Empty Field!")
        lname_label_error.grid(row=5, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 

# Limit address line entry box length function
def addvalidation(u_input):
    if len(u_input) > 255: 
        btn_upd.config(state='disabled')  
        add_label_error.configure(text="Exceed 255 Characters Length Limit!")
        add_label_error.grid(row=7, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 
    elif len(u_input) > 0 and len(u_input) <= 255:
        add_label_error.grid_remove()
        if not phone_label_error.grid_info() and not email_label_error.grid_info() and not fname_label_error.grid_info() and not lname_label_error.grid_info() and not city_label_error.grid_info(): 
            btn_upd.config(state='normal')  
        return True 
    elif (len(u_input)==0):
        btn_upd.config(state='disabled')  
        add_label_error.configure(text="Invalid Empty Field!")
        add_label_error.grid(row=7, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 

# Limit address line entry box length function
def cityvalidation1(u_input):
    if len(u_input) > 30: 
        btn_upd.config(state='disabled')  
        city_label_error.configure(text="Exceed 30 Characters Length Limit!")
        city_label_error.grid(row=9, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 
    elif len(u_input) > 0 and len(u_input) <= 30:
        city_label_error.grid_remove()
        if not phone_label_error.grid_info() and not email_label_error.grid_info() and not fname_label_error.grid_info() and not add_label_error.grid_info() and not lname_label_error.grid_info(): 
            btn_upd.config(state='normal')  
        return True 
    elif (len(u_input)==0):
        btn_upd.config(state='disabled')  
        city_label_error.configure(text="Invalid Empty Field!")
        city_label_error.grid(row=9, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 
def cityvalidation2(*args):
    value = city_val.get()
    
    whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    if not (value.isalpha() & value.isspace()):
        corrected = ''.join(filter(whitelist.__contains__, value))
        if len(corrected) > 30: 
            corrected = corrected[:30]
        city_val.set(corrected)

# Limit postal code entry box length and numeric only function    
def postvalidation1(input):
    if input.isdigit():
        return True
    else:
        return False
def postvalidation2(*args):
    value = post_val.get()
    if len(value) > 5: 
        post_val.set(value[:5])

# Validate email entry box function
def validate_email(u_input):
    if(re.search(emailregex, u_input) and u_input.isalpha):
        email_label_error.grid_remove()
        if not phone_label_error.grid_info(): 
            btn_upd.config(state='normal')  
        return True  
    elif (len(u_input)==0):
        btn_upd.config(state='disabled')  
        email_label_error.configure(text="Invalid Empty Field!")
        email_label_error.grid(row=13, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True    
    else:
        btn_upd.config(state='disabled')  
        email_label_error.configure(text="Improper Email Format!")
        email_label_error.grid(row=13, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True

# Validate phone entry box function
def validate_phone(u_input):
    if(re.search(phoneregex, u_input) and u_input.isalpha):
        phone_label_error.grid_remove()
        if not email_label_error.grid_info():
            btn_upd.config(state='normal')  
        return True        
    elif (len(u_input)==0):
        btn_upd.config(state='disabled')  
        phone_label_error.configure(text="Invalid Empty Field!")
        phone_label_error.grid(row=15, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True    
    else:
        btn_upd.config(state='disabled') 
        phone_label_error.configure(text="Improper Phone Number Format!") 
        phone_label_error.grid(row=15, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True

# Change password validation function
def validate_pass1(*args):
    if oldpass_val.get() and newpass_val.get and conpass_val.get():
        one_empty.configure(fg="green")
    else:
        one_empty.configure(fg="red")
        
    if(len(newpass_val.get()) >= 8):
        two_length.configure(fg="green")
    else:
        two_length.configure(fg="red")
        
    if(re.search('[a-z]+', newpass_val.get())):
        three_lower.configure(fg="green")
    else:
        three_lower.configure(fg="red")
        
    if(re.search('[A-Z]+', newpass_val.get())):
        four_upper.configure(fg="green")
    else:
        four_upper.configure(fg="red")
        
    if(re.search('\d', newpass_val.get())):
        five_digit.configure(fg="green")
    else:
        five_digit.configure(fg="red")
        
    if(re.search('[@$!%*?&]', newpass_val.get())):
        six_specialchar.configure(fg="green")
    else:
        six_specialchar.configure(fg="red")
        
    if((newpass_val.get() == conpass_val.get()) and newpass_val.get() and conpass_val.get()):
        seven_con.configure(fg="green")
    else:
        seven_con.configure(fg="red")
        
    if ((one_empty["foreground"] == 'green') and (two_length["foreground"] == 'green') and (three_lower["foreground"] == 'green') and (four_upper["foreground"] == 'green') and 
        (six_specialchar["foreground"] == 'green') and (seven_con["foreground"] == 'green')):
        btn_passupd.config(state='normal')
    else:
        btn_passupd.config(state='disabled')
def validate_pass2(*args):
    if fnewpass_val.get and fconpass_val.get():
        fone_empty.configure(fg="green")
    else:
        fone_empty.configure(fg="red")
        
    if(len(fnewpass_val.get()) >= 8):
        ftwo_length.configure(fg="green")
    else:
        ftwo_length.configure(fg="red")
        
    if(re.search('[a-z]+', fnewpass_val.get())):
        fthree_lower.configure(fg="green")
    else:
        fthree_lower.configure(fg="red")
        
    if(re.search('[A-Z]+', fnewpass_val.get())):
        ffour_upper.configure(fg="green")
    else:
        ffour_upper.configure(fg="red")
        
    if(re.search('\d', fnewpass_val.get())):
        ffive_digit.configure(fg="green")
    else:
        ffive_digit.configure(fg="red")
        
    if(re.search('[@$!%*?&]', fnewpass_val.get())):
        fsix_specialchar.configure(fg="green")
    else:
        fsix_specialchar.configure(fg="red")
        
    if((fnewpass_val.get() == fconpass_val.get()) and fnewpass_val.get() and fconpass_val.get()):
        fseven_con.configure(fg="green")
    else:
        fseven_con.configure(fg="red")
        
    if ((fone_empty["foreground"] == 'green') and (ftwo_length["foreground"] == 'green') and (fthree_lower["foreground"] == 'green') and (ffour_upper["foreground"] == 'green') and 
        (fsix_specialchar["foreground"] == 'green') and (fseven_con["foreground"] == 'green')):
        fbtn_save.config(state='normal')
    else:
        fbtn_save.config(state='disabled')

    
#==============================================================================================#
#                                     Login Page (root)                                        #
#==============================================================================================#
## Login Page Interface (Root)
root = Tk()

# Configure window attribute
cscreen_height = root.winfo_screenheight()
cscreen_width = root.winfo_screenwidth()
ratio = float('%.3f' % (cscreen_height/1080))
root.title('e-Vision Login')
root.iconbitmap('asset/logo.ico')
root.state('zoomed')
root.minsize(round(cscreen_width*0.8333), round(cscreen_height*0.8333))
root.call('tk', 'scaling', 1.34)

# Configure row column attribute
root.grid_columnconfigure(0, weight=round(1*ratio))
root.grid_columnconfigure(1, weight=round(1*ratio))
root.grid_rowconfigure(0, weight=round(1*ratio))
root.grid_rowconfigure(9, weight=round(1*ratio))

# Setup frames
login_banner = Frame(root, width=round(cscreen_width/2), height=round(cscreen_height))
login_banner.grid(row=0, column=0, rowspan=10, sticky="nsew")
login_component = Frame(root, width=round(cscreen_width/2), height=round(cscreen_height), bg="#EDF1F7")
login_component.grid(row=0, column=1, rowspan=10, sticky="nsew")

# Left banner image
img = Image.open('asset/login_left.png')
img = img.resize((round(cscreen_width/2), round(cscreen_height)), Image.ANTIALIAS)
copy_img = img.copy()
banner_img = ImageTk.PhotoImage(img)
label = Label(login_banner, image=banner_img)
label.config(highlightthickness=0, borderwidth=0)
label.bind('<Configure>', resize_image)
label.pack(fill=BOTH,expand=YES)
# Right login components
canva = ResizingCanvas(login_component, width=round(cscreen_width/2), height=round(cscreen_height), bg="#EDF1F7", highlightthickness=0)
canva.pack(fill=BOTH, expand=YES)
login_title = Label(root, text="Login to Account", font=("Lato bold", round(34*ratio)), bg="#EDF1F7")
login_title.grid(row=1, column=1, sticky="w", padx=round(100*ratio))
login_desc = Label(root, text="Enter your login data created in below section", font=("Lato", round(12*ratio)), bg="#EDF1F7")
login_desc.grid(row=2, column=1, sticky="w", padx=round(100*ratio))
lbl_email = Label(root, text="Email", font=("Lato bold", round(15*ratio)), bg="#EDF1F7")
lbl_email.grid(row=3, column=1, sticky="w", padx=round(100*ratio), pady=(round(65*ratio),round(5*ratio)))
txt_email = Entry(root, bd=round(17*ratio), relief=FLAT, font=("Lato", round(14*ratio)))
txt_email.grid(row=4, column=1, sticky="nsew", padx=round(100*ratio))
lbl_pass = Label(root, text="Password", font=("Lato bold", round(15*ratio)), bg="#EDF1F7")
lbl_pass.grid(row=5, column=1, sticky="w", padx=round(100*ratio), pady=(round(50*ratio),round(5*ratio)))
txt_pass = Entry(root, bd=round(17*ratio), relief=FLAT, font=("Lato", round(14*ratio)), show="*")
txt_pass.grid(row=6, column=1, sticky="nsew", padx=round(100*ratio))
var1 = IntVar()
showpas = Checkbutton(root, text='Show Password',variable=var1, onvalue=1, offvalue=0, font=("Lato", round(11*ratio)), command=lambda:showpass(), bg="#EDF1F7")
showpas.grid(row=7, column=1, sticky="nw", padx=round(100*ratio), pady=round(10*ratio))
btn_login = Button(root, text="Login Account", command=lambda:login(txt_email, txt_pass), font=("Lato bold", round(16*ratio)), height=2, fg="white", bg="#1267AC", relief=RAISED, activebackground="#0E4470", activeforeground="white")
btn_login.grid(row=7, column=1, sticky="sew", padx=round(100*ratio), pady=(round(70*ratio),round(40*ratio)))
lbl_reg = Label(root, text="Don't have account? Please contact company's Admin", font=("Lato", round(12*ratio)), bg="#EDF1F7")
lbl_reg.grid(row=8, column=1, sticky="w", padx=round(100*ratio))

#==============================================================================================#
#                                         Main Page                                            #
#==============================================================================================#
## Main Page Interface
def mainPage():
    global mainWindow
    
    # Configure window attribute
    mainWindow = Toplevel(root)
    mainWindow.title('e-Vision')
    mainWindow.iconbitmap('asset/logo.ico')
    mainWindow.state('zoomed')
    mainWindow.minsize(round(cscreen_width*0.9), round(cscreen_height*0.9))
    
    # Configure row column attribute
    mainWindow.grid_columnconfigure(0, weight=round(2*ratio))
    mainWindow.grid_columnconfigure(1, weight=round(1*ratio))
    mainWindow.grid_columnconfigure(2, weight=round(2*ratio))
    mainWindow.grid_rowconfigure(2, weight=round(4*ratio))
    
    # Setup frames
    left_frame = Frame(mainWindow, width=round(cscreen_width*0.78), height=round(cscreen_height), bg="#EDF1F7")
    left_frame.grid(row=0, column=0, rowspan=9, columnspan=3, sticky="nsew")
    right_frame = Frame(mainWindow, width=round(cscreen_width*0.22), height=round(cscreen_height), bg="#1D253D")
    right_frame.grid(row=0, column=3, rowspan=9, columnspan=2, sticky="nsew")
    
    # Left components
    video_player = Frame(mainWindow, bg="white", highlightbackground="black", highlightthickness=1)
    video_player.grid(row=0, column=0, rowspan=8, columnspan=3, sticky="nsew", padx=round(25*ratio), pady=(round(30*ratio), round(15*ratio)))
    if(usession.user_role == 1):
        btn_frame1 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame1.grid(row=8, column=0, sticky="nsew")
        btn_mnguser = Button(btn_frame1, command=lambda:usermanagementPage(), text="Manage User", font=("Lato bold", round(12*ratio)), height=1, width=round(25*ratio), fg="white", bg="#364052", relief=RAISED, activebackground="#1D232D", activeforeground="white")
        btn_mnguser.pack(pady=(round(10*ratio), round(30*ratio)))
        btn_frame2 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame2.grid(row=8, column=1, sticky="nsew")
        btn_mngcamera = Button(btn_frame2, text="Manage Camera", font=("Lato bold", round(12*ratio)), height=1, width=round(25*ratio), fg="white", bg="#364052", relief=RAISED, activebackground="#1D232D", activeforeground="white")
        btn_mngcamera.pack(pady=(round(10*ratio), round(30*ratio)))
        btn_frame3 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame3.grid(row=8, column=2, sticky="nsew")
        btn_asscamera = Button(btn_frame3, text="Assign Camera", font=("Lato bold", round(12*ratio)), height=1, width=round(25*ratio), fg="white", bg="#364052", relief=RAISED, activebackground="#1D232D", activeforeground="white")
        btn_asscamera.pack(pady=(round(10*ratio), round(30*ratio)))
    else:
        btn_frame1 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame1.grid(row=8, column=0, sticky="nsew", pady=(round(10*ratio), round(50*ratio)))
        btn_frame2 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame2.grid(row=8, column=1, sticky="nsew")
        btn_frame3 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame3.grid(row=8, column=2, sticky="nsew")
    # Right components
    img = Image.open('asset/logo.png')
    img = img.resize((round((img.size[0]/1.35)*ratio), round((img.size[0]/1.35)*ratio)))
    img = ImageTk.PhotoImage(img)
    img_label = Label(mainWindow, image=img, bg="#1D253D")
    img_label.image = img
    img_label.grid(column=3, row=0, columnspan=2, sticky="nsew", pady=(round(30*ratio), round(5*ratio)))
    btn_frame4 = Frame(mainWindow, bg="#1D253D")
    btn_frame4.grid(row=1, column=3, sticky="nsew", padx=(round(30*ratio), round(5*ratio)), pady=round(10*ratio))
    btn_profile = Button(btn_frame4, text="Profile", command=lambda:profilePage(), font=("Lato bold", round(13*ratio)), fg="white", bg="#5869F0", relief=FLAT, activebackground="#414EBB", activeforeground="white")
    btn_profile.pack(fill='x')
    btn_frame5 = Frame(mainWindow, bg="#1D253D")
    btn_frame5.grid(row=1, column=4, sticky="nsew", padx=(round(5*ratio), round(30*ratio)), pady=round(10*ratio))
    btn_logout = Button(btn_frame5, text="Logout", command=lambda:logout(), font=("Lato bold", round(13*ratio)), height=1, width=round(15*ratio), fg="white", bg="#FF0000", relief=FLAT, activebackground="#B50505", activeforeground="white")
    btn_logout.pack(fill='x')
    notebookstyle = ttk.Style()
    notebookstyle.theme_use('default')
    notebookstyle.configure('TNotebook', background="#1D253D", borderwidth=round(1*ratio), relief=FLAT)
    notebookstyle.configure('TNotebook.Tab', font=("Lato bold", round(11*ratio)), background="#34415B", borderwidth=round(1*ratio), relief=FLAT, foreground="white", padding=(round(30*ratio),round(5*ratio),round(30*ratio),round(5*ratio)))
    notebookstyle.map("TNotebook.Tab", background=[("selected", "#8D9EC1")])
    notebookstyle.layout("Tab",
    [('Notebook.tab', {'sticky': 'nswe', 'children':
        [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
            [('Notebook.label', {'side': 'top', 'sticky': ''})],
        })],
    })]
    )
    acci_tab = ttk.Notebook(mainWindow)
    acci_tab.grid(row=2, column=3, columnspan=2, sticky="nsew", padx=round(30*ratio))
    new_accif = Frame(acci_tab, bg="#34415B")
    history_accif = Frame(acci_tab, bg="#34415B")
    new_accif.pack(fill="both", expand=1)
    history_accif.pack(fill="both", expand=1)
    acci_tab.add(new_accif, text="New Detected")
    acci_tab.add(history_accif, text="Accident History")
    btn_frame6 = Frame(mainWindow, bg="#1D253D")
    btn_frame6.grid(row=3, column=3, columnspan=2, sticky="nsew", padx=round(30*ratio), pady=round(10*ratio))
    btn_refresh = Button(btn_frame6, text="Refresh Accident List", font=("Lato bold", round(13*ratio)), height=1, width=round(32*ratio), fg="white", bg="#5869F0", relief=FLAT, activebackground="#414EBB", activeforeground="white")
    btn_refresh.pack(fill='x')
    btn_frame7 = Frame(mainWindow, bg="#1D253D")
    btn_frame7.grid(row=4, column=3, sticky="nsew", padx=(round(30*ratio), round(5*ratio)), pady=(0, round(5*ratio)))
    btn_init = Button(btn_frame7, text="Initiate", font=("Lato bold", round(13*ratio)), height=1, width=round(15*ratio), fg="white", bg="#5869F0", relief=FLAT, activebackground="#414EBB", activeforeground="white")
    btn_init.pack(fill='x')
    btn_frame8 = Frame(mainWindow, bg="#1D253D")
    btn_frame8.grid(row=4, column=4, sticky="nsew", padx=(round(5*ratio), round(30*ratio)), pady=(0, round(5*ratio)))
    btn_stop = Button(btn_frame8, text="Stop", font=("Lato bold", round(13*ratio)), height=1, width=round(15*ratio), fg="white", bg="#5869F0", relief=FLAT, activebackground="#414EBB", activeforeground="white")
    btn_stop.pack(fill='x')
    camera_list = Label(mainWindow, text="Camera List: ", font=("Lato", round(13*ratio)), bg="#1D253D", fg="white")
    camera_list.grid(row=5, column=3, columnspan=2, sticky="w", padx=round(30*ratio), pady=(round(5*ratio),0))
    camera_id = Label(mainWindow, text="Camera ID: ", font=("Lato", round(13*ratio)), bg="#1D253D", fg="white")
    camera_id.grid(row=6, column=3, columnspan=2, sticky="w", padx=round(30*ratio))
    camera_loc = Label(mainWindow, text="Location: ", font=("Lato", round(13*ratio)), bg="#1D253D", fg="white")
    camera_loc.grid(row=7, column=3, columnspan=2, sticky="w", padx=round(30*ratio), pady=(0,round(5*ratio)))
    btn_frame9 = Frame(mainWindow, bg="#1D253D")
    btn_frame9.grid(row=8, column=3, sticky="nsew", padx=(round(30*ratio), round(5*ratio)), pady=(round(5*ratio), 0))
    icon_prev = Image.open('asset/previous_icon.png')
    icon_prev = icon_prev.resize((round(30*ratio),round(30*ratio)), Image.ANTIALIAS)
    icon_prev = ImageTk.PhotoImage(icon_prev)
    btn_prev = Button(btn_frame9, image=icon_prev, height=round(30*ratio), width=round(150*ratio), bg="#5869F0", relief=FLAT, activebackground="#414EBB")
    btn_prev.image = icon_prev
    btn_prev.pack(fill='x')
    btn_frame10 = Frame(mainWindow, bg="#1D253D")
    btn_frame10.grid(row=8, column=4, sticky="nsew", padx=(round(5*ratio), round(30*ratio)), pady=(round(5*ratio), 0))
    icon_next = Image.open('asset/next_icon.png')
    icon_next = icon_next.resize((round(30*ratio),round(30*ratio)), Image.ANTIALIAS)
    icon_next = ImageTk.PhotoImage(icon_next)
    btn_next = Button(btn_frame10, image=icon_next, height=round(30*ratio), width=round(150*ratio), bg="#5869F0", relief=FLAT, activebackground="#414EBB")
    btn_next.image = icon_next
    btn_next.pack(fill='x')
    mainWindow.protocol("WM_DELETE_WINDOW", logout) # If click on close button of window
    # Check for first time login
    if(usession.user_firstlogin == 1):
        mainWindow.attributes('-disabled', 1)
        global wel, fnewpass_val, fconpass_val, fone_empty, ftwo_length, fthree_lower,ffour_upper, ffive_digit, fsix_specialchar, fseven_con, fbtn_save
        wel = Toplevel(mainWindow)
        wel.grab_set()
        wel.overrideredirect(True)
        height = round(554*ratio)
        width = round(520*ratio)
        x = (cscreen_width/2)-(width/2)
        y = (cscreen_height/2)-(height/2)
        wel.geometry(f'{width}x{height}+{round(x)}+{round(y)}')
        # Configure row column attribute
        wel.grid_columnconfigure(0, weight=1)
        wel.grid_columnconfigure(1, weight=1)
        fr = Frame(wel, highlightbackground="black", highlightthickness=1, bg="white")
        fr.grid(row=0, column=0, rowspan=13, columnspan=2, sticky="nsew")
        wel_lbl = Label(wel, text="Welcome!", font=("Lato bold", round(18*ratio)), bg="white")
        wel_lbl.grid(row=0, column=0, padx=round(40*ratio), pady=(round(25*ratio), round(10*ratio)), sticky="nsw")
        f1 = Frame(wel, bg="white")
        f1.grid(row=1, column=0, columnspan=2, padx=round(40*ratio), sticky="nsew")
        desc_lbl = Text(f1, font=("Lato", round(12*ratio)), bg="white", wrap=WORD, highlightthickness=0, height=round(4*ratio), relief=FLAT)
        desc_lbl.pack()
        desc_lbl.insert(INSERT, "To make your account secure, please create a new password to replace the temporary password given initially before continue.")
        desc_lbl.configure(state="disabled")
        new_lbl = Label(wel, text="New Password", font=("Lato bold", round(13*ratio)), bg="white")
        new_lbl.grid(row=2, column=0, padx=(round(40*ratio) ,0), pady=(0, round(10*ratio)), sticky="nsw")
        connew_lbl = Label(wel, text="Confirm New Password", font=("Lato bold", round(13*ratio)), bg="white")
        connew_lbl.grid(row=3, column=0, padx=(round(40*ratio), 0), pady=(round(10*ratio),0), sticky="nsw")
        fnewpass_val = StringVar()
        fnewpass_val.trace("w", validate_pass2)
        txt_newpas = Entry(wel, font=("Lato", round(12*ratio)), relief=FLAT, highlightthickness=2, show="*", textvariable=fnewpass_val)
        txt_newpas.grid(row=2, column=1, sticky="nsw", padx=(round(10*ratio), round(25*ratio)), pady=(0, round(10*ratio)))
        fconpass_val = StringVar()
        fconpass_val.trace("w", validate_pass2)
        txt_cpas = Entry(wel, font=("Lato", round(12*ratio)), relief=FLAT, highlightthickness=2, show="*", textvariable=fconpass_val)
        txt_cpas.grid(row=3, column=1, sticky="nsw", padx=(round(10*ratio), round(25*ratio)), pady=(round(10*ratio),0))
        # Password validation display
        passpolicy_label = Label(wel, text="Password Policy Requirements (Red Indicated NOT Fulfiled):", font=("Lato", round(10*ratio)), bg="white", fg="black")
        passpolicy_label.grid(row=4, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0), pady=(round(30*ratio), 0))
        fone_empty = Label(wel, text="Password can't be empty!", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
        fone_empty.grid(row=5, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
        ftwo_length = Label(wel, text="Password must have a minimum of 8 characters in length!", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
        ftwo_length.grid(row=6, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
        fthree_lower = Label(wel, text="Password must have at least one lowercase English letter! (e.g. a-z)", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
        fthree_lower.grid(row=7, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
        ffour_upper = Label(wel, text="Password must have at least one uppercase English letter! (e.g. A-Z)", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
        ffour_upper.grid(row=8, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
        ffive_digit = Label(wel, text="Password must have at least one digit! (e.g. 0-9)", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
        ffive_digit.grid(row=9, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
        fsix_specialchar = Label(wel, text="Password must have at least one accepted special character! (e.g. @$!%*?&)", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
        fsix_specialchar.grid(row=10, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
        fseven_con = Label(wel, text="Confirm new password does not match new password", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
        fseven_con.grid(row=11, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
        fbtn_save = Button(wel, command=lambda:usession.firstchange(txt_newpas, txt_cpas), text="Save", font=("Lato bold", round(15*ratio)), height=1, fg="white", bg="#1F5192", relief=RAISED, activebackground="#173B6A", activeforeground="white")
        fbtn_save.grid(row=12, column=0, columnspan=2, sticky="nsew", padx=round(40*ratio),  pady=round(30*ratio))
        fbtn_save.config(state='disabled')  
    
#==============================================================================================#
#                                         Profile Page                                         #
#==============================================================================================#
## Profile Page Interface
def profilePage(): 
    global profileWindow, name_label, add_con, email_con, phone_con, canvas
    
    # Configure  window attribute
    mainWindow.withdraw()
    profileWindow = Toplevel(mainWindow)
    profileWindow.title('e-Vision My Profile')
    profileWindow.iconbitmap('asset/logo.ico')
    height = round(700*ratio)
    width = round(1150*ratio)
    x = (cscreen_width/2)-(width/2)
    y = (cscreen_height/2)-(height/2)
    profileWindow.geometry(f'{width}x{height}+{round(x)}+{round(y)}')
    profileWindow.resizable(False, False)
    profileWindow.protocol("WM_DELETE_WINDOW", disable_event)
    
    # Configure row column attribute
    profileWindow.grid_columnconfigure(1, weight=round(1*ratio))
    profileWindow.grid_columnconfigure(2, weight=round(1*ratio))

    profileWindow.grid_rowconfigure(6, weight=round(1*ratio))
    profileWindow.grid_rowconfigure(7, weight=round(3*ratio))
    
    # Setup frames
    left_frame = Frame(profileWindow, width=round(cscreen_width*0.17), bg="#1b1b23", relief=RAISED)
    left_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")
    right_frame = Frame(profileWindow, width=round(cscreen_width*0.43), bg="#2b2f3b")
    right_frame.grid(row=0, column=1, rowspan=8, columnspan=2, sticky="nsew")
    
    # Left components
    btn_frame1 = Frame(profileWindow, bg="#1b1b23")
    btn_frame1.grid(row=0, column=0, sticky="nsw", padx=round(10*ratio), pady=(round(10*ratio),0))
    backmainbtn(btn_frame1, profileWindow, "#1b1b23")
    avatar_path = 'temp/' + usession.user_avatar + '.png'
    img_avatar = Image.open(avatar_path)
    img_avatar = img_avatar.resize((round(180*ratio),round(180*ratio)), Image.ANTIALIAS)
    img_avatar = ImageTk.PhotoImage(img_avatar)
    imgava_label = Label(profileWindow, image=img_avatar, bg="#1b1b23")
    imgava_label.image = img_avatar
    imgava_label.grid(column=0, row=1, rowspan=2, sticky="nsew")
    page_title = Label(profileWindow, text="Personal Info", font=("Lato bold", round(18*ratio)), bg="#1b1b23", fg="white")
    page_title.grid(row=3, column=0, sticky="nsew", pady=round(10*ratio))
    btn_frame2 = Frame(profileWindow, bg="#1b1b23")
    btn_frame2.grid(row=4, column=0, sticky="nsew")
    btn_upload = Button(btn_frame2, command=lambda:usession.upload_avatar(imgava_label), text="Upload New Avatar", font=("Lato bold", round(12*ratio)), height=1, width=round(20*ratio), fg="white", bg="#1F5192", relief=FLAT, activebackground="#173B6A", activeforeground="white")
    btn_upload.pack()
    CreateToolTip(btn_upload, text = 'Best fit image ratio is 50 50\n'
                 'Accept both PNG and JPG format\n'
                 'Max size limit is 20MB')
    # Right components
    canvas = Canvas(right_frame, width=round(825*ratio), height=round(260*ratio), bd=0, highlightthickness=0)
    canvas.pack(side=TOP)
    banner_img = Image.open('asset/profile_banner.jpg')
    banner_img = banner_img.resize((round(825*ratio),round(260*ratio)), Image.ANTIALIAS)
    banner_img = ImageTk.PhotoImage(banner_img)
    profileWindow.banner_img = banner_img
    banner_back = canvas.create_image(0,0, image=banner_img, anchor=NW)
    sys_label = canvas.create_text(round(800*ratio), round(20*ratio),text="e-Vision", font=("Lato bold", round(14*ratio)), fill="black", anchor=NE)
    name_label = canvas.create_text(round(65*ratio), round(215*ratio), text="{}".format(usession.user_firstname+" "+usession.user_lastname), font=("Lato bold", round(32*ratio)), fill="white", anchor=SW)
    if (usession.user_role == 1):
        txt = 'Admin'
    else:
        txt = 'Monitoring Employee'
    role_label = canvas.create_text(round(65*ratio), round(240*ratio), text="{}".format(txt), font=("Lato", round(15*ratio)), fill="white", anchor=SW)
    uid_label = Label(profileWindow, text="User ID", font=("Lato bold", round(16*ratio)), bg="#2b2f3b", fg="white")
    uid_label.grid(row=3, column=1, sticky="sw", padx=(round(60*ratio), 0), pady=(round(40*ratio), 0))
    f0 = Frame(profileWindow, bg="#2b2f3b")
    f0.grid(row=4, column=1, padx=(round(60*ratio), 0), sticky="nw")
    uid_con = Text(f0, font=("Lato", round(14*ratio)), bg="#2b2f3b", fg="white", wrap=WORD, highlightthickness=0, height=round(2*ratio), width=round(25*ratio), relief=FLAT)
    uid_con.pack()
    uid_con.insert(INSERT, "{}".format(usession.user_id))
    uid_con.configure(state="disabled")
    add_label = Label(profileWindow, text="Address", font=("Lato bold", round(16*ratio)), bg="#2b2f3b", fg="white")
    add_label.grid(row=5, column=1, sticky="sw", padx=(round(60*ratio), 0), pady=(round(30*ratio),0))
    f1 = Frame(profileWindow, bg="#2b2f3b")
    f1.grid(row=6, column=1, padx=(round(60*ratio), 0), sticky="nw")
    add_con = Text(f1, font=("Lato", round(14*ratio)), bg="#2b2f3b", fg="white", wrap=WORD, highlightthickness=0, height=round(5*ratio), width=round(30*ratio), relief=FLAT)
    add_con.pack()
    add_con.insert(INSERT, "{}, {} {}, {}.".format(usession.user_addressline, usession.user_postcode, usession.user_city, usession.user_state))
    add_con.configure(state="disabled")
    email_label = Label(profileWindow, text="Email", font=("Lato bold", round(16*ratio)), bg="#2b2f3b", fg="white")
    email_label.grid(row=3, column=2, sticky="sw", padx=(round(15*ratio), round(35*ratio)), pady=(round(40*ratio), 0))
    f2 = Frame(profileWindow, bg="#2b2f3b")
    f2.grid(row=4, column=2, padx=(round(15*ratio), round(25*ratio)), sticky="nw")
    email_con = Text(f2, font=("Lato", round(14*ratio)), bg="#2b2f3b", fg="white", wrap=WORD, highlightthickness=0, height=round(1*ratio), width=round(35*ratio), relief=FLAT)
    email_con.pack()
    email_con.insert(INSERT, "{}".format(usession.user_email))
    email_con.configure(state="disabled")
    phone_label = Label(profileWindow, text="Phone Number", font=("Lato bold", round(16*ratio)), bg="#2b2f3b", fg="white")
    phone_label.grid(row=5, column=2, sticky="sw", padx=(round(15*ratio), round(35*ratio)), pady=(round(30*ratio),0))
    f3 = Frame(profileWindow, bg="#2b2f3b")
    f3.grid(row=6, column=2, padx=(round(15*ratio), round(25*ratio)), sticky="nw")
    phone_con = Text(f3, font=("Lato", round(14*ratio)), bg="#2b2f3b", fg="white", wrap=WORD, highlightthickness=0, height=round(2*ratio), width=round(25*ratio), relief=FLAT)
    phone_con.pack()
    phone_con.insert(INSERT, "{}".format(usession.user_phone))
    phone_con.configure(state="disabled")
    btn_frame3 = Frame(profileWindow, bg="#2b2f3b")
    btn_frame3.grid(row=7, column=1, sticky="nse", padx=round(30*ratio), pady=round(10*ratio))
    btn_edit = Button(btn_frame3, command=lambda:updateprofilePage(), text="Edit Profile", font=("Lato bold", round(12*ratio)), height=1, width=round(20*ratio), fg="white", bg="#1F5192", relief=FLAT, activebackground="#173B6A", activeforeground="white")
    btn_edit.pack()
    btn_frame4 = Frame(profileWindow, bg="#2b2f3b")
    btn_frame4.grid(row=7, column=2, sticky="nsw", padx=round(30*ratio), pady=round(10*ratio))
    btn_chgpas = Button(btn_frame4, command=lambda:updatepassPage(), text="Change Password", font=("Lato bold", round(12*ratio)), height=1, width=round(20*ratio), fg="black", bg="white", relief=FLAT, activebackground="#DCDCDC", activeforeground="black")
    btn_chgpas.pack()
    
#==============================================================================================#
#                                     Update Profile Page                                      #
#==============================================================================================#
## Update Profile Page Interface
def updateprofilePage():
    global updprofileWindow, ufname_val, ulname_val, add_val, city_val, post_val, state_val, email_label_error, email_val, phone_label_error, phone_val, btn_upd, fname_label_error, lname_label_error, add_label_error, city_label_error
    
    # Configure window attribute
    profileWindow.attributes('-disabled', 1)
    updprofileWindow = Toplevel(profileWindow)
    updprofileWindow.grab_set()
    updprofileWindow.overrideredirect(True)
    height = round(800*ratio)
    width = round(500*ratio)
    x = (cscreen_width/2)-(width/2)
    y = (cscreen_height/2)-(height/2)
    updprofileWindow.geometry(f'{width}x{height}+{round(x)}+{round(y)}')
    
    # Configure row column attribute
    updprofileWindow.grid_columnconfigure(0, weight=round(1*ratio))
    updprofileWindow.grid_columnconfigure(1, weight=round(1*ratio))
    updprofileWindow.grid_rowconfigure(17, weight=round(1*ratio))
    
    # Background frame
    f0 = Frame(updprofileWindow, bg="white")
    f0.grid(row=0, column=0, rowspan=18, columnspan=2, sticky="nsew")
    # Header title
    proupdtile = Image.open('asset/update_profile.png')
    proupdtile = proupdtile.resize((round(250*ratio),round(90*ratio)))
    proupdtile = ImageTk.PhotoImage(proupdtile)
    proupdtile_label = Label(updprofileWindow, image=proupdtile, bg="white")
    proupdtile_label.image = proupdtile
    proupdtile_label.grid(column=0, row=0, columnspan=2, sticky="nsew", pady=(round(30*ratio), round(20*ratio)))
    # Contents
    uid_label = Label(updprofileWindow, text="User ID", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    uid_label.grid(row=1, column=0, columnspan=2, sticky="sw", padx=round(60*ratio))
    f0 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f0.grid(row=2, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    uid_text = Entry(f0, bd=round(3*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio))
    uid_text.pack(fill=BOTH, expand=True)
    uid_text.insert(INSERT, "{}".format(usession.user_id))
    uid_text.configure(state="disabled")
    ufname_label = Label(updprofileWindow, text="First Name", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    ufname_label.grid(row=3, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    fname_label_error = Label(updprofileWindow, text="Invalid Empty Field!", font=("Lato bold", round(9*ratio)), bg="white", fg="red")
    f1 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f1.grid(row=4, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    ufname_val = StringVar()
    my_valid3 = updprofileWindow.register(fnamevalidation)
    ufname_text = Entry(f1, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=ufname_val)
    ufname_text.pack(fill=BOTH, expand=True)
    ufname_text.insert(INSERT, "{}".format(usession.user_firstname))
    ufname_text.config(validate="key", validatecommand=(my_valid3, '%P'))
    CreateToolTip(ufname_text, text = 'Max length should only be 30 characters')
    ulname_label = Label(updprofileWindow, text="Last Name", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    ulname_label.grid(row=5, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    lname_label_error = Label(updprofileWindow, text="Invalid Empty Field!", font=("Lato bold", round(9*ratio)), bg="white", fg="red")
    f2 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f2.grid(row=6, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    ulname_val = StringVar()
    my_valid4 = updprofileWindow.register(lnamevalidation)
    ulname_text = Entry(f2, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=ulname_val)
    ulname_text.pack(fill=BOTH, expand=True)
    ulname_text.insert(INSERT, "{}".format(usession.user_lastname))
    ulname_text.config(validate="key", validatecommand=(my_valid4, '%P'))
    CreateToolTip(ulname_text, text = 'Max length should only be 30 characters')
    add_label = Label(updprofileWindow, text="Address Line", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    add_label.grid(row=7, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    add_label_error = Label(updprofileWindow, text="Invalid Empty Field!", font=("Lato bold", round(9*ratio)), bg="white", fg="red")
    f3 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f3.grid(row=8, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    add_val = StringVar()
    my_valid5 = updprofileWindow.register(addvalidation)
    add_text = Entry(f3, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=add_val)
    add_text.pack(fill=BOTH, expand=True)
    add_text.insert(INSERT, "{}".format(usession.user_addressline))
    add_text.config(validate="key", validatecommand=(my_valid5, '%P'))
    CreateToolTip(add_text, text = 'Max length should only be 255 characters')
    city_label = Label(updprofileWindow, text="City", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    city_label.grid(row=9, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    city_label_error = Label(updprofileWindow, text="Invalid Empty Field!", font=("Lato bold", round(9*ratio)), bg="white", fg="red")
    f4 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f4.grid(row=10, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    city_val = StringVar()
    city_val.trace('w', cityvalidation2)
    city_text = Entry(f4, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=city_val)
    city_text.pack(fill=BOTH, expand=True)
    city_text.insert(INSERT, "{}".format(usession.user_city))
    myvalid6 = updprofileWindow.register(cityvalidation1)
    city_text.config(validate="key", validatecommand=(myvalid6, '%P'))
    CreateToolTip(city_text, text = 'Max length should only be 30 characters')
    post_label = Label(updprofileWindow, text="Postal Code", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    post_label.grid(row=11, column=0, sticky="sw", padx=(round(60*ratio), 0), pady=(round(10*ratio), 0))
    f4a = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f4a.grid(row=12, column=0, padx=(round(60*ratio), round(10*ratio)), sticky="nw")
    post_val = StringVar()
    post_val.trace("w", postvalidation2)
    post_text = Entry(f4a, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), textvariable=post_val)
    post_text.pack(fill=BOTH, expand=True)
    post_text.insert(INSERT, "{}".format(usession.user_postcode))
    reg = updprofileWindow.register(postvalidation1)
    post_text.config(validate="key", validatecommand=(reg, '%P'))
    CreateToolTip(post_text, text = 'Max length should only be 5 numeric')
    state_label = Label(updprofileWindow, text="State", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    state_label.grid(row=11, column=1, sticky="sw", padx=(round(15*ratio), round(60*ratio)), pady=(round(10*ratio), 0))
    f5 = Frame(updprofileWindow, relief=SUNKEN)
    f5.grid(row=12, column=1, padx=(round(10*ratio), round(60*ratio)), sticky="ne")
    state_val = StringVar()
    state_text = ttk.Combobox(f5, font=("Lato", round(14*ratio)), textvariable=state_val, state='readonly', background="white")
    state_text['values'] = ('Johor', 
                          'Kedah',
                          'Kelantan',
                          'Malacca',
                          'Negeri Sembilan',
                          'Pahang',
                          'Penang',
                          'Perak',
                          'Perlis',
                          'Sabah',
                          'Sarawak',
                          'Selangor',
                          'Terengganu',
                          'Kuala Lumpur',
                          'Labuan',
                          'Putrajaya')
    state_text.pack(fill=BOTH, expand=True)
    state_text.current(0)
    ustate = usession.user_state
    if ustate == 'Johor':
        state_text.current(0)
    elif ustate == 'Kedah':
        state_text.current(1)
    elif ustate == 'Kelantan':
        state_text.current(2)
    elif ustate == 'Malacca':
        state_text.current(3)
    elif ustate == 'Negeri Sembilan':
        state_text.current(4)
    elif ustate == 'Pahang':
        state_text.current(5)
    elif ustate == 'Penang':
        state_text.current(6)
    elif ustate == 'Perak':
        state_text.current(7)
    elif ustate == 'Perlis':
        state_text.current(8)
    elif ustate == 'Sabah':
        state_text.current(9)
    elif ustate == 'Sarawak':
        state_text.current(10)
    elif ustate == 'Selangor':
        state_text.current(11)
    elif ustate == 'Terengganu':
        state_text.current(12)
    elif ustate == 'Kuala Lumpur':
        state_text.current(13)
    elif ustate == 'Labuan':
        state_text.current(14)
    else:
        state_text.current(15)
    email_label = Label(updprofileWindow, text="Email", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    email_label.grid(row=13, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    email_label_error = Label(updprofileWindow, text="Improper Email Format!", font=("Lato bold", round(9*ratio)), bg="white", fg="red")
    f6 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f6.grid(row=14, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    email_val = StringVar()
    my_valid = updprofileWindow.register(validate_email)
    email_text = Entry(f6, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=email_val)
    email_text.pack(fill=BOTH, expand=True)
    email_text.insert(INSERT, "{}".format(usession.user_email))
    email_text.config(validate="key", validatecommand=(my_valid, '%P'))
    CreateToolTip(email_text, text = 'e.g. dummy@xyz.com')
    phone_label = Label(updprofileWindow, text="Phone Number", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    phone_label.grid(row=15, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    phone_label_error = Label(updprofileWindow, text="Improper Phone Number Format!", font=("Lato bold", round(9*ratio)), bg="white", fg="red")
    f7 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f7.grid(row=16, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    phone_val = StringVar()
    phone_valid = updprofileWindow.register(validate_phone)
    phone_text = Entry(f7, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=phone_val)
    phone_text.pack(fill=BOTH, expand=True)
    phone_text.insert(INSERT, "{}".format(usession.user_phone))
    phone_text.config(validate="key", validatecommand=(phone_valid, '%P'))
    CreateToolTip(phone_text, text = 'e.g. 012-3456789')
    f8 = Frame(updprofileWindow ,bg="white")
    f8.grid(row=17, column=0, sticky="nse", padx=(0,round(20*ratio)), pady=round(15*ratio))
    btn_upd = Button(f8, text="Update", command=lambda:usession.updateprofile(ufname_text, ulname_text, add_text, city_text, state_text, post_text, email_text, phone_text), font=("Lato bold", round(12*ratio)), height=1, width=round(13*ratio), fg="white", bg="#1F5192", relief=RAISED, activebackground="#173B6A", activeforeground="white")
    btn_upd.pack()
    f9 = Frame(updprofileWindow, bg="white")
    f9.grid(row=17, column=1, sticky="nsw", padx=(round(50*ratio),0), pady=round(15*ratio))
    btn_close = Button(f9, text="Close", command=lambda:closeupdprofile(), font=("Lato bold", round(12*ratio)), height=1, width=round(13*ratio), fg="black", bg="white", relief=RAISED, activebackground="#DCDCDC", activeforeground="black")
    btn_close.pack()
    
#==============================================================================================#
#                                     Update Profile Page                                      #
#==============================================================================================#
## Update Password Page Interface
def updatepassPage():
    global updpassWindow, oldpass_val, newpass_val, conpass_val, one_empty, two_length, three_lower, four_upper, five_digit, six_specialchar, seven_con, btn_passupd
    
    # Configure window attribute
    profileWindow.attributes('-disabled', 1)
    updpassWindow = Toplevel(profileWindow)
    updpassWindow.grab_set()
    updpassWindow.overrideredirect(True)
    height = round(630*ratio)
    width = round(520*ratio)
    x = (cscreen_width/2)-(width/2)
    y = (cscreen_height/2)-(height/2)
    updpassWindow.geometry(f'{width}x{height}+{round(x)}+{round(y)}')
    
    # Configure row column attribute
    updpassWindow.grid_columnconfigure(0, weight=round(1*ratio))
    updpassWindow.grid_columnconfigure(1, weight=round(1*ratio))
    updpassWindow.grid_rowconfigure(12, weight=round(1*ratio))
    
    # Background frame
    f0 = Frame(updpassWindow, bg="white")
    f0.grid(row=0, column=0, rowspan=13, columnspan=2, sticky="nsew")
    # Header title
    passupdtile = Image.open('asset/change_password.png')
    passupdtile = passupdtile.resize((round(290*ratio),round(90*ratio)), Image.ANTIALIAS)
    passupdtile = ImageTk.PhotoImage(passupdtile)
    passupdtile_label = Label(updpassWindow, image=passupdtile, bg="white")
    passupdtile_label.image = passupdtile
    passupdtile_label.grid(column=0, row=0, columnspan=2, sticky="nsew", pady=(round(40*ratio),round(30*ratio))) 
    # Contents
    f1a = Frame(updpassWindow, bg="white")
    f1a.grid(row=1, column=0, sticky="nsw", padx=(round(40*ratio), 0))
    oldpass_label = Label(f1a, text="Old Password", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    oldpass_label.pack()
    f1 = Frame(updpassWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f1.grid(row=1, column=1, sticky="nse", padx=(0, round(40*ratio)))
    oldpass_val = StringVar()
    oldpass_val.trace("w", validate_pass1)
    oldpass_text = Entry(f1, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(20*ratio), show="*", textvariable=oldpass_val)
    oldpass_text.pack()
    f2a = Frame(updpassWindow, bg="white")
    f2a.grid(row=2, column=0, sticky="nsw", padx=(round(40*ratio), 0), pady=round(20*ratio))
    newpass_label = Label(f2a, text="New Password", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    newpass_label.pack()
    f2 = Frame(updpassWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f2.grid(row=2, column=1, sticky="nse", pady=round(20*ratio), padx=(0, round(40*ratio)))
    newpass_val = StringVar()
    newpass_val.trace("w", validate_pass1)
    newpass_text = Entry(f2, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(20*ratio), show="*", textvariable=newpass_val)
    newpass_text.pack()
    f3a = Frame(updpassWindow, bg="white")
    f3a.grid(row=3, column=0, sticky="nsw", padx=(round(40*ratio), 0))
    connewpass_label = Label(f3a, text="Confirm New Password", font=("Lato bold", round(13*ratio)), bg="white", fg="black")
    connewpass_label.pack()
    f3 = Frame(updpassWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f3.grid(row=3, column=1, sticky="nse", padx=(0, round(40*ratio)))
    conpass_val = StringVar()
    conpass_val.trace("w", validate_pass1)
    connewpass_text = Entry(f3, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(20*ratio), show="*", textvariable=conpass_val)
    connewpass_text.pack()
    passpolicy_label = Label(updpassWindow, text="Password Policy Requirements (Red Indicated NOT Fulfiled):", font=("Lato", round(10*ratio)), bg="white", fg="black")
    passpolicy_label.grid(row=4, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0), pady=(round(30*ratio), 0))
    one_empty = Label(updpassWindow, text="Password can't be empty!", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
    one_empty.grid(row=5, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    two_length = Label(updpassWindow, text="Password must have a minimum of 8 characters in length!", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
    two_length.grid(row=6, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    three_lower = Label(updpassWindow, text="Password must have at least one lowercase English letter! (e.g. a-z)", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
    three_lower.grid(row=7, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    four_upper = Label(updpassWindow, text="Password must have at least one uppercase English letter! (e.g. A-Z)", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
    four_upper.grid(row=8, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    five_digit = Label(updpassWindow, text="Password must have at least one digit! (e.g. 0-9)", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
    five_digit.grid(row=9, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    six_specialchar = Label(updpassWindow, text="Password must have at least one accepted special character! (e.g. @$!%*?&)", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
    six_specialchar.grid(row=10, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio)))
    seven_con = Label(updpassWindow, text="Confirm new password does not match new password", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
    seven_con.grid(row=11, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    f4 = Frame(updpassWindow ,bg="white")
    f4.grid(row=12, column=0, sticky="nse", pady=round(30*ratio), padx=(0, round(30*ratio)))
    btn_passupd = Button(f4, text="Update", command=lambda:usession.updatepass(oldpass_text, newpass_text, connewpass_text), font=("Lato bold", round(12*ratio)), height=1, width=round(13*ratio), fg="white", bg="#1F5192", relief=RAISED, activebackground="#173B6A", activeforeground="white")
    btn_passupd.pack()
    btn_passupd.config(state='disabled')
    f5 = Frame(updpassWindow, bg="white")
    f5.grid(row=12, column=1, sticky="nsw", pady=round(30*ratio), padx=(round(45*ratio), 0))
    btn_passclose = Button(f5, text="Close", command=lambda:closechgpass(), font=("Lato bold", round(12*ratio)), height=1, width=round(13*ratio), fg="black", bg="white", relief=RAISED, activebackground="#DCDCDC", activeforeground="black")
    btn_passclose.pack()

#==============================================================================================#
#                                   Admin - Manage User Page                                   #
#==============================================================================================#
## Admin - Manage User Page Interface
def usermanagementPage():
    # Configure  window attribute
    mainWindow.withdraw()
    usermanageWindow = Toplevel(mainWindow)
    usermanageWindow.title('e-Vision User Management')
    usermanageWindow.iconbitmap('asset/logo.ico')
    height = round(960*ratio)
    width = round(1600*ratio)
    x = (cscreen_width/2)-(width/2)
    y = ((cscreen_height/2)-(height/2))-round(25*ratio)
    usermanageWindow.geometry(f'{width}x{height}+{round(x)}+{round(y)}')
    usermanageWindow.resizable(False, False)
    usermanageWindow.protocol("WM_DELETE_WINDOW", disable_event)
    
    # Configure row column attribute
    usermanageWindow.grid_columnconfigure(2, weight=round(1*ratio))
    usermanageWindow.grid_columnconfigure(3, weight=round(2*ratio))
    usermanageWindow.grid_columnconfigure(4, weight=round(2*ratio))
    usermanageWindow.grid_rowconfigure(23, weight=round(1*ratio))
    
    # Setup frames
    left_frame = Frame(usermanageWindow, width=round(cscreen_width*0.28), bg="#EDF1F7")
    left_frame.grid(row=0, column=0, rowspan=24, columnspan=3, sticky="nsew")
    right_frame = Frame(usermanageWindow, width=round(cscreen_width*0.58), bg="#21BDBF")
    right_frame.grid(row=0, column=3, rowspan=24, columnspan=2, sticky="nsew")
    dummy_frame = Frame(usermanageWindow, width=round(cscreen_width*0.094), bg="#EDF1F7")
    dummy_frame.grid(row=0, column=1, rowspan=24, sticky="nsew")
    
    # Left components
    btn_frame1 = Canvas(usermanageWindow, bg="#EDF1F7")
    btn_frame1.grid(row=0, column=0, sticky="nsw", padx=round(10*ratio), pady=round(10*ratio))
    backmainbtn(btn_frame1, usermanageWindow, "#EDF1F7")
    # Header title
    usrmngtile = Image.open('asset/user_management.png')
    usrmngtile = usrmngtile.resize((round(295*ratio),round(110*ratio)))
    usrmngtile = ImageTk.PhotoImage(usrmngtile)
    usrmngtile_label = Label(usermanageWindow, image=usrmngtile, bg="#EDF1F7")
    usrmngtile_label.image = usrmngtile
    usrmngtile_label.grid(column=1, row=0, columnspan=2, sticky="nsw", pady=(round(30*ratio), round(5*ratio)), padx=(round(20*ratio), 0))
    # User detail fields
    uid_label = Label(usermanageWindow, text="User ID", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    uid_label.grid(row=2, column=0, columnspan=3, sticky="sw", padx=round(60*ratio))
    f0 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f0.grid(row=3, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    uid_text = Entry(f0, bd=round(3*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio))
    uid_text.pack(fill=BOTH, expand=True)
    uid_text.configure(state="disabled")
    CreateToolTip(uid_text, text = 'Add New User: Leave this field blank as system will auto generate the user ID\n'
                  'Update User Info: Select the user to be updated in the list, user ID field will be automatically filled')
    ufname_label = Label(usermanageWindow, text="First Name", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    ufname_label.grid(row=4, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    f1 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f1.grid(row=5, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    ufname_val = StringVar()
    # ufname_val.trace('w', fnamevalidation)
    ufname_text = Entry(f1, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=ufname_val)
    ufname_text.pack(fill=BOTH, expand=True)
    CreateToolTip(ufname_text, text = 'Max length should only be 30 characters')
    ulname_label = Label(usermanageWindow, text="Last Name", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    ulname_label.grid(row=6, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    f2 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f2.grid(row=7, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    ulname_val = StringVar()
    # ulname_val.trace('w', lnamevalidation)
    ulname_text = Entry(f2, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=ulname_val)
    ulname_text.pack(fill=BOTH, expand=True)
    CreateToolTip(ulname_text, text = 'Max length should only be 30 characters')
    pas_label = Label(usermanageWindow, text="Password", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    pas_label.grid(row=8, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    fpas = Frame(usermanageWindow, bg="#EDF1F7")
    fpas.grid(row=9, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    resetpas_btn = Button(fpas, text="Reset Password", font=("Lato bold", round(13*ratio)), width=round(20*ratio))
    resetpas_btn.pack(side=LEFT)
    # pas_val = StringVar()
    # # pas_val.trace('w', addvalidation)
    # pas_text = Entry(fpas, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=pas_val)
    # pas_text.pack(fill=BOTH, expand=True)
    # CreateToolTip(pas_text, text = 'Password Policy Requirement:\n'
    #               '\t1. Minimum 8 characters in length\n'
    #               '\t2. At least one lowercase English letter (a-z)\n'
    #               '\t3. At least one uppercase English letter (A-Z)\n'
    #               '\t4. At least one digit (0-9)\n'
    #               '\t5. At least one accepted special character (@$!%*?&')
    add_label = Label(usermanageWindow, text="Address Line", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    add_label.grid(row=10, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    f3 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f3.grid(row=11, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    add_val = StringVar()
    # add_val.trace('w', addvalidation)
    add_text = Entry(f3, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=add_val)
    add_text.pack(fill=BOTH, expand=True)
    CreateToolTip(add_text, text = 'Max length should only be 255 characters')
    city_label = Label(usermanageWindow, text="City", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    city_label.grid(row=12, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    f4 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f4.grid(row=13, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    city_val = StringVar()
    # city_val.trace('w', cityvalidation)
    city_text = Entry(f4, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=city_val)
    city_text.pack(fill=BOTH, expand=True)
    CreateToolTip(city_text, text = 'Max length should only be 30 characters')
    post_label = Label(usermanageWindow, text="Postal Code", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    post_label.grid(row=14, column=0, columnspan=2, sticky="sw", padx=(round(60*ratio), 0), pady=(round(10*ratio), 0))
    f4a = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f4a.grid(row=15, column=0, columnspan=2, padx=(round(60*ratio), round(10*ratio)), sticky="nw")
    post_val = StringVar()
    # post_val.trace("w", postvalidation2)
    post_text = Entry(f4a, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), textvariable=post_val)
    post_text.pack(fill=BOTH, expand=True)
    # reg = updprofileWindow.register(postvalidation1)
    # post_text.config(validate="key", validatecommand=(reg, '%P'))
    CreateToolTip(post_text, text = 'Max length should only be 5 numeric')
    state_label = Label(usermanageWindow, text="State", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    state_label.grid(row=14, column=2, sticky="sw", padx=(round(15*ratio), round(60*ratio)), pady=(round(10*ratio), 0))
    f5 = Frame(usermanageWindow, relief=SUNKEN)
    f5.grid(row=15, column=2, padx=(round(10*ratio), round(60*ratio)), sticky="ne")
    state_val = StringVar()
    state_text = ttk.Combobox(f5, font=("Lato", round(14*ratio)), textvariable=state_val, state='readonly', background="white")
    state_text['values'] = ('Johor', 
                          'Kedah',
                          'Kelantan',
                          'Malacca',
                          'Negeri Sembilan',
                          'Pahang',
                          'Penang',
                          'Perak',
                          'Perlis',
                          'Sabah',
                          'Sarawak',
                          'Selangor',
                          'Terengganu',
                          'Kuala Lumpur',
                          'Labuan',
                          'Putrajaya')
    state_text.pack(fill=BOTH, expand=True)
    state_text.current(0)
    email_label = Label(usermanageWindow, text="Email", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    email_label.grid(row=16, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    um_email_label_error = Label(usermanageWindow, text="Improper Email Format!", font=("Lato bold", round(9*ratio)), bg="#EDF1F7", fg="red")
    f6 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f6.grid(row=17, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    email_val = StringVar()
    # my_valid = usermanageWindow.register(validate_email)
    email_text = Entry(f6, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=email_val)
    email_text.pack(fill=BOTH, expand=True)
    # email_text.config(validate="key", validatecommand=(my_valid, '%P'))
    CreateToolTip(email_text, text = 'e.g. dummy@xyz.com')
    phone_label = Label(usermanageWindow, text="Phone Number", font=("Lato bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    phone_label.grid(row=18, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    um_phone_label_error = Label(usermanageWindow, text="Improper Phone Number Format!", font=("Lato bold", round(9*ratio)), bg="white", fg="red")
    f7 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f7.grid(row=19, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    phone_val = StringVar()
    # phone_valid = usermanageWindow.register(validate_phone)
    phone_text = Entry(f7, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=phone_val)
    phone_text.pack(fill=BOTH, expand=True)
    # phone_text.config(validate="key", validatecommand=(phone_valid, '%P'))
    CreateToolTip(phone_text, text = 'e.g. 012-3456789')
    f8 = Frame(usermanageWindow, bg="#EDF1F7")
    f8.grid(row=20, column=0, columnspan=3, sticky="nsew", padx=round(60*ratio), pady=(round(20*ratio), round(5*ratio)))
    add_userbtn = Button(f8, text="Add New User", font=("Lato bold", round(13*ratio)), width=round(43*ratio), bg="#15D500", fg="white", relief=FLAT, activebackground="#10A500", activeforeground="white")
    add_userbtn.pack()
    f9 = Frame(usermanageWindow, bg="#EDF1F7")
    f9.grid(row=21, column=0, columnspan=3, sticky="nsew", padx=round(60*ratio), pady= round(5*ratio))
    upd_userbtn = Button(f9, text="Update User Info", font=("Lato bold", round(13*ratio)), width=round(43*ratio), bg="#1F5192", fg="white", relief=FLAT, activebackground="#112F57", activeforeground="white")
    upd_userbtn.pack()
    f10 = Frame(usermanageWindow, bg="#EDF1F7")
    f10.grid(row=22, column=0, columnspan=3, sticky="nsew", padx=round(60*ratio), pady=round(5*ratio))
    add_userbtn = Button(f10, text="Delete User", font=("Lato bold", round(13*ratio)), width=round(43*ratio), bg="#E30000", fg="white", relief=FLAT, activebackground="#9E0101", activeforeground="white")
    add_userbtn.pack()
    
    # Right components
    sys_label = Label(usermanageWindow, text="e-Vision", font=("Lato bold", round(14*ratio)), bg="#21BDBF", fg="white")
    sys_label.grid(row=0, column=4, sticky="ne", padx=round(30*ratio), pady=round(15*ratio))
    # Treeview components
    column_headerlist = ['User ID', 'First Name', 'Last Name', 'Address Line', 'City', 'Postcode', 'State', 'Email Address', 'Phone Number']
    

root.mainloop()