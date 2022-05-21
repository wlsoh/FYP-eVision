# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Main GUI Integration
# Date Created: 05/05/2022
import os
import io
import re
import secrets
import string
import pymysql
import pandas as pd
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
from ctypes import windll
from datetime import datetime
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from Google import Create_Service
from mysql_db.db_connect import MySqlConnector
from email_sender import *


#==============================================================================================#
#                                 Connection & Initial Setup                                   #
#==============================================================================================#
# Prevent blur due to screen scale setting
windll.shcore.SetProcessDpiAwareness(1) 
# Regex for validation
pare = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")
emailregex = '^[a-zA-Z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
phoneregex = "^(\+?6?01)[02-46-9]-*[0-9]{7}$|^(\+?6?01)[1]-*[0-9]{8}$"

# Create database connection to AWS RDS
sql_config = 'online'

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
    def __init__(self, uid, ufname, ulname, uadd, ucity, ustate, upost, uemail, uphone, urole, uavatar, ullogin, uflogin):
        self.user_id = uid
        self.user_firstname = ufname
        self.user_lastname = ulname
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
        # If new password not satisfied the requirement
        elif (re.fullmatch(pare, new)==None):
            messagebox.showerror("Change Password Failed", "The values for new password must be at least 8 characters with minimum one special character, one number and both uppercase & lowercase letter!")
            newf.delete(0, END)
            conf.delete(0, END)
            newf.focus()
        else:  
            cid = self.user_id
            try:
                mysql_con = MySqlConnector(sql_config) # Initial connection
                sql = '''SELECT * FROM User WHERE user_id = (%s) AND BINARY user_password = SHA2(%s, 256)'''
                result_details = mysql_con.queryall(sql, (cid, new))
            except pymysql.Error as e:
                messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                print("Error %d: %s" % (e.args[0], e.args[1]))
                return False
            finally:
                # Close the connection
                mysql_con.close()
                
            if not result_details:
                try:
                    mysql_con = MySqlConnector(sql_config) # Initial connection
                    sql = '''UPDATE User SET user_password = SHA2(%s, 256), user_firstLogin = 0 WHERE user_id = (%s)'''
                    update = mysql_con.update(sql, (new, cid))
                    if update > 0:
                        # Update the current user data
                        sql = '''SELECT * FROM User WHERE user_id = (%s)'''
                        result_details = mysql_con.queryall(sql, (cid))
                        self.user_id = result_details[0][0]
                        self.user_firstname = result_details[0][1]
                        self.user_lastname = result_details[0][2]
                        self.user_addressline = result_details[0][4]
                        self.user_city = result_details[0][5]
                        self.user_state = result_details[0][6]
                        self.user_postcode = result_details[0][7]
                        self.user_email = result_details[0][8]
                        self.user_phone = result_details[0][9]
                        self.user_role = result_details[0][10]
                        self.user_firstlogin = result_details[0][12]
                        messagebox.showinfo("Change Password Successful", "Your temporary password had been replaced with the new password!")
                        mainWindow.attributes('-disabled', 0)
                        wel.destroy() # Close the interface
                        mainWindow.focus_force()
                    # If error
                    else:
                        messagebox.showerror("Change Passord Failed", "Failed to update your temporary password! Please contact developer for help!")
                        logout()
                except pymysql.Error as e:
                    messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                    print("Error %d: %s" % (e.args[0], e.args[1]))
                    return False
                finally:
                    # Close the connection
                    mysql_con.close()
            else:
                messagebox.showerror("Change Password Failed", "The new password should not be same with existing password!")
                newf.delete(0, END)
                conf.delete(0, END)
                newf.focus()
            
                
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
                try:
                    mysql_con = MySqlConnector(sql_config) # Initial connection
                    sql = sql = '''UPDATE User SET user_avatar = (%s) WHERE user_id = (%s)''' # Update user avatar
                    update = mysql_con.update(sql, (temp_id, self.user_id))
                    if update > 0:
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
                    # If error
                    else:
                        profileWindow.attributes('-disabled', 0)
                        loading_splash.destroy()
                        messagebox.showerror("Change Avatar Failed", "Failed to update your avatar! Please contact developer for help!")
                except pymysql.Error as e:
                    messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                    print("Error %d: %s" % (e.args[0], e.args[1]))
                    return False
                finally:
                    # Close the connection
                    mysql_con.close()
                
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
            else:
                cid = self.user_id
                
                try:
                    mysql_con = MySqlConnector(sql_config) # Initial connection
                    sql = '''SELECT * FROM User WHERE user_id = (%s) AND BINARY user_password = SHA2(%s, 256)'''
                    result_details = mysql_con.queryall(sql, (cid, old))
                except pymysql.Error as e:
                    messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                    print("Error %d: %s" % (e.args[0], e.args[1]))
                    return False
                finally:
                    # Close the connection
                    mysql_con.close()
                
                if result_details:
                    try:
                        mysql_con = MySqlConnector(sql_config) # Initial connection
                        sql = '''SELECT * FROM User WHERE user_id = (%s) AND BINARY user_password = SHA2(%s, 256)'''
                        result_details1 = mysql_con.queryall(sql, (cid, new))
                    except pymysql.Error as e:
                        messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                        print("Error %d: %s" % (e.args[0], e.args[1]))
                        return False
                    finally:
                        # Close the connection
                        mysql_con.close()
                    
                    if not  result_details1:
                        loading(updpassWindow)
                        try:
                            mysql_con = MySqlConnector(sql_config) # Initial connection
                            sql = '''UPDATE User SET user_password = SHA2(%s, 256) WHERE user_id = (%s)'''
                            update = mysql_con.update(sql, (new, cid))
                            if update > 0:
                                # Update the current user data
                                sql = '''SELECT * FROM User WHERE user_id = (%s)'''
                                result_details = mysql_con.queryall(sql, (cid))
                                self.user_id = result_details[0][0]
                                self.user_firstname = result_details[0][1]
                                self.user_lastname = result_details[0][2]
                                self.user_addressline = result_details[0][4]
                                self.user_city = result_details[0][5]
                                self.user_state = result_details[0][6]
                                self.user_postcode = result_details[0][7]
                                self.user_email = result_details[0][8]
                                self.user_phone = result_details[0][9]
                                self.user_role = result_details[0][10]
                                self.user_firstlogin = result_details[0][12]
                                loading_splash.destroy()
                                messagebox.showinfo("Change Password Successful", "Your had successfully updated your password!")
                                profileWindow.attributes('-disabled', 0)
                                updpassWindow.destroy() # Close the interface
                                profileWindow.focus_force()
                            # If error
                            else:
                                loading_splash.destroy()
                                messagebox.showerror("Change Passord Failed", "Failed to update your temporary password! Please contact developer for help!")
                                profileWindow.attributes('-disabled', 0)
                                updpassWindow.destroy() # Close the interface
                                profileWindow.focus_force() 
                        except pymysql.Error as e:
                            messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                            print("Error %d: %s" % (e.args[0], e.args[1]))
                            return False
                        finally:
                            # Close the connection
                            mysql_con.close()
                    else:
                        messagebox.showerror("Change Password Failed", "The new password should not be same with existing password!")
                        oldf.delete(0, END)
                        newf.delete(0, END)
                        conf.delete(0, END)
                        oldf.focus()
                else:
                    messagebox.showerror("Change Password Failed", "Incorrect current password!")
                    oldf.delete(0, END)
                    newf.delete(0, END)
                    conf.delete(0, END)
                    oldf.focus()
                    
                        
                    
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
                if em.get().lower() != self.user_email:
                    try:
                        mysql_con = MySqlConnector(sql_config) # Initial connection
                        sql = '''SELECT user_email FROM User'''
                        result_details = mysql_con.queryall(sql)
                        result = [result[0] for result in result_details]
                        for i in range(len(result)):
                            if result[i] == em.get().lower():
                                loading_splash.destroy()
                                messagebox.showerror("Update Profile Failed", "The new inserted email had been registered previously!")
                                email_exist = True
                                updprofileWindow.attributes('-disabled', 0)
                                updprofileWindow.focus_force()
                                em.focus()
                                break
                    except pymysql.Error as e:
                        messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                        print("Error %d: %s" % (e.args[0], e.args[1]))
                        return False
                    finally:
                        # Close the connection
                        mysql_con.close()
                        
                # Update profile if exist was false
                if(email_exist == False):
                    input_addline = ad.get()
                    if "," in input_addline[-1]:
                        input_addline = input_addline.rstrip(",")
                    try:
                        mysql_con = MySqlConnector(sql_config) # Initial connection
                        sql = '''UPDATE User SET user_firstname = (%s), user_lastname = (%s), user_addressline = (%s), user_city = (%s), user_state = (%s), user_postcode = (%s), user_email = (%s), user_phone = (%s) WHERE user_id = (%s)''' # Update user info
                        update = mysql_con.update(sql, (uf.get(), ul.get(), input_addline, ci.get(), st.get(), po.get(), em.get().lower(), ph.get(), self.user_id))
                        if update > 0:
                            # Update the current user data
                            sql = '''SELECT * FROM User WHERE user_id = (%s)'''
                            result_details1 = mysql_con.queryall(sql, (self.user_id))
                            self.user_firstname = result_details1[0][1]
                            self.user_lastname = result_details1[0][2]
                            self.user_addressline = result_details1[0][4]
                            self.user_city = result_details1[0][5]
                            self.user_state = result_details1[0][6]
                            self.user_postcode = result_details1[0][7]
                            self.user_email = result_details1[0][8]
                            self.user_phone = result_details1[0][9]
                            loading_splash.destroy()
                            messagebox.showinfo("Personal Info Update Successful", "Your new personal details had been updated!")
                            profileWindow.attributes('-disabled', 0)
                            updprofileWindow.destroy() # Close the interface
                            profileWindow.focus_force()
                            # Update content display
                            canvas.itemconfig(name_label, text="{}".format(self.user_firstname+" "+self.user_lastname))
                            addline_con.configure(text=self.user_addressline)
                            city_con.configure(text=self.user_city)
                            zipcode_con.configure(text=self.user_postcode)
                            state_con.configure(text=self.user_state)
                            email_con.configure(text=self.user_email)
                            phone_con.configure(text=self.user_phone)
                            profileWindow.update()
                        # If error
                        else:
                            loading_splash.destroy()
                            messagebox.showerror("Personal Info Update Failed", "Failed to update your personal details! Please contact developer for help!")
                            profileWindow.attributes('-disabled', 0)
                            updprofileWindow.destroy() # Close the interface
                            profileWindow.focus_force() 
                    except pymysql.Error as e:
                        messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                        print("Error %d: %s" % (e.args[0], e.args[1]))
                        return False
                    finally:
                        # Close the connection
                        mysql_con.close()

# User class
class User:
    def __init__(self, ufname, ulname, uadd, ucity, ustate, upost, uemail, uphone):
        self.user_firstname = ufname
        self.user_lastname = ulname
        self.user_addressline = uadd
        self.user_city = ucity
        self.user_state = ustate
        self.user_postcode = upost
        self.user_email = uemail
        self.user_phone = uphone

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
                      background="white", relief=SOLID, borderwidth=1,
                      font=("Lato", "8", "normal"))
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
    width = round(450*ratio)
    x = (cscreen_width/2)-(width/2)
    y = (cscreen_height/2)-(height/2)
    loading_splash.geometry(f'{width}x{height}+{round(x)}+{round(y)}')
    # Left banner
    frame_img = Frame(loading_splash, bg="#242426", width=round(150*ratio), height=round(150*ratio))
    frame_img.grid(row=0, column=0, rowspan=2)
    left_banner = Image.open('asset/loading_banner.jpg')
    left_banner = left_banner.resize((round(150*ratio),round(150*ratio)), Image.ANTIALIAS)
    left_banner = ImageTk.PhotoImage(left_banner)
    leftb_lbl = Label(frame_img, image=left_banner, bg="#242426", relief=FLAT, bd=0)
    leftb_lbl.image = left_banner
    leftb_lbl.pack(expand=TRUE, fill=BOTH)
    # Right content
    frame_loading = Frame(loading_splash, bg="#242426", width=round(300*ratio), height=round(150*ratio))
    frame_loading.grid(row=0, column=1, rowspan=2, columnspan=2)
    txt1 = Label(loading_splash, text="Loading...", font=("Arial Rounded MT Bold", round(15*ratio)), bg="#242426", fg='#FFBD09')
    txt1.grid(row=0, column=1, columnspan=2, sticky="sew")
    txt2 = Label(loading_splash, text="Let's wait & chill", font=("Arial Rounded MT Bold", round(15*ratio)), bg="#242426", fg='#FFBD09')
    txt2.grid(row=1, column=1, columnspan=2, sticky="new")

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
    global passwordShown
    
    if passwordShown:
        passwordShown = False
        txt_pass.configure(show="*")
        show_pass.pack_forget()
        hide_pass.pack(side=RIGHT, padx=round(10*ratio), fill=BOTH)
        
    else:
        passwordShown = True
        txt_pass.configure(show="")
        hide_pass.pack_forget()
        show_pass.pack(side=RIGHT, padx=round(10*ratio), fill=BOTH)

# Login function
def login(eloc, ploc, eml_error, pas_error):
    uname = eloc.get()
    pas = ploc.get()
    global usession
    
    # If both fields empty
    if not uname and not pas:
        eml_error.config(text="Invalid empty field!")
        pas_error.config(text="Invalid empty field!")
        eloc.focus()
    # If email field empty
    elif not uname and pas:
        eml_error.config(text="Invalid empty field!")
        pas_error.config(text="")
        eloc.focus()
    # If password field empty
    elif not pas and uname:
        eml_error.config(text="")
        pas_error.config(text="Invalid empty field!")
        ploc.focus()
    # If password minimum length not satisfied
    elif len(pas) < 8:
        eml_error.config(text="")
        pas_error.config(text="Password length should not less than 8 characters!")
        ploc.focus()
    else:
        eml_error.config(text="")
        pas_error.config(text="")
        try:
            mysql_con = MySqlConnector(sql_config) # Initial connection
            sql = '''SELECT * FROM User WHERE user_email = (%s) AND BINARY user_password = SHA2(%s, 256)'''
            result_details = mysql_con.queryall(sql, (uname.lower(), pas))
            if result_details:
                loading(root)
                root.update()
                usession = Usersession(
                    result_details[0][0], 
                    result_details[0][1], 
                    result_details[0][2],  
                    result_details[0][4], 
                    result_details[0][5], 
                    result_details[0][6], 
                    result_details[0][7], 
                    result_details[0][8], 
                    result_details[0][9], 
                    result_details[0][10], 
                    result_details[0][11], 
                    result_details[0][12], 
                    result_details[0][13]
                )
                now = datetime.now() # Get current date time
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                sql = '''UPDATE User SET user_lastlogin_datetime = (%s) WHERE user_id = (%s)''' # Update last login
                mysql_con.update(sql, (dt_string, usession.user_id))
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
        except pymysql.Error as e:
            messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            # Close the connection
            mysql_con.close()
 
# Logout function
def logout():
    confirmbox = messagebox.askquestion('e-Vision Logout', 'Are you sure to logout the system?', icon='warning')
    if confirmbox == 'yes':
        global usession, passwordShown
        del usession # Delete user session
        # Clear all files in temp folder
        dir = './temp'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        mainWindow.destroy() # Destroy current winfow
        root.deiconify() # Show login page again
        root.geometry(f'{width1}x{height1}+{round(x1)}+{round(y1)}')
        if passwordShown:
            passwordShown = False
            txt_pass.configure(show="*")
            show_pass.pack_forget()
            hide_pass.pack(side=RIGHT, padx=round(10*ratio), fill=BOTH)

# Do nothing function
def disable_event():
   pass

# Back to main button function
def backmainbtn(comploc, curwin, bgcol):
    icon_back = Image.open('asset/back.png')
    icon_back = icon_back.resize((round(65*ratio),round(65*ratio)), Image.ANTIALIAS)
    icon_back = ImageTk.PhotoImage(icon_back)
    btn_back = Button(comploc, cursor="hand2", command=lambda:backmain(curwin), image=icon_back, height=round(65*ratio), width=round(65*ratio), bg=bgcol, relief=FLAT, bd=0, highlightthickness=0, activebackground=bgcol)
    btn_back.image = icon_back
    btn_back.pack()
    CreateToolTip(btn_back, text = 'Back to Main Page')

# Back to main function
def backmain(cur):
    cur.withdraw()
    style.theme_use("default")
    mainWindow.deiconify()
    mainWindow.state('zoomed')
    
# Back to Login function
def backlogin(cur):
    cur.destroy()
    style.theme_use("default")
    root.attributes('-disabled', 0)
    root.focus_force()

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
        btn_upd.config(state='disabled', cursor="")  
        fname_label_error.configure(text="Exceed 30 Characters Length Limit!")
        fname_label_error.grid(row=3, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 
    elif len(u_input) > 0 and len(u_input) <= 30:
        fname_label_error.grid_remove()
        if not phone_label_error.grid_info() and not email_label_error.grid_info() and not lname_label_error.grid_info() and not add_label_error.grid_info() and not city_label_error.grid_info(): 
            btn_upd.config(state='normal', cursor="hand2")  
        return True 
    elif (len(u_input)==0):
        btn_upd.config(state='disabled', cursor="")  
        fname_label_error.configure(text="Invalid Empty Field!")
        fname_label_error.grid(row=3, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 

# Limit last name entry box length function
def lnamevalidation(u_input):
    if len(u_input) > 30: 
        btn_upd.config(state='disabled', cursor="")  
        lname_label_error.configure(text="Exceed 30 Characters Length Limit!")
        lname_label_error.grid(row=5, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 
    elif len(u_input) > 0 and len(u_input) <= 30:
        lname_label_error.grid_remove()
        if not phone_label_error.grid_info() and not email_label_error.grid_info() and not fname_label_error.grid_info() and not add_label_error.grid_info() and not city_label_error.grid_info(): 
            btn_upd.config(state='normal', cursor="hand2")  
        return True 
    elif (len(u_input)==0):
        btn_upd.config(state='disabled', cursor="")  
        lname_label_error.configure(text="Invalid Empty Field!")
        lname_label_error.grid(row=5, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 

# Limit address line entry box length function
def addvalidation(u_input):
    if len(u_input) > 255: 
        btn_upd.config(state='disabled', cursor="")  
        add_label_error.configure(text="Exceed 255 Characters Length Limit!")
        add_label_error.grid(row=7, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 
    elif len(u_input) > 0 and len(u_input) <= 255:
        add_label_error.grid_remove()
        if not phone_label_error.grid_info() and not email_label_error.grid_info() and not fname_label_error.grid_info() and not lname_label_error.grid_info() and not city_label_error.grid_info(): 
            btn_upd.config(state='normal', cursor="hand2")  
        return True 
    elif (len(u_input)==0):
        btn_upd.config(state='disabled', cursor="")  
        add_label_error.configure(text="Invalid Empty Field!")
        add_label_error.grid(row=7, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 

# Limit address line entry box length function
def cityvalidation1(u_input):
    if len(u_input) > 30: 
        btn_upd.config(state='disabled', cursor="")  
        city_label_error.configure(text="Exceed 30 Characters Length Limit!")
        city_label_error.grid(row=9, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True 
    elif len(u_input) > 0 and len(u_input) <= 30:
        city_label_error.grid_remove()
        if not phone_label_error.grid_info() and not email_label_error.grid_info() and not fname_label_error.grid_info() and not add_label_error.grid_info() and not lname_label_error.grid_info(): 
            btn_upd.config(state='normal', cursor="hand2")  
        return True 
    elif (len(u_input)==0):
        btn_upd.config(state='disabled', cursor="")  
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
            btn_upd.config(state='normal', cursor="hand2")  
        return True  
    elif (len(u_input)==0):
        btn_upd.config(state='disabled', cursor="")  
        email_label_error.configure(text="Invalid Empty Field!")
        email_label_error.grid(row=13, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True    
    else:
        btn_upd.config(state='disabled', cursor="")  
        email_label_error.configure(text="Improper Email Format!")
        email_label_error.grid(row=13, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True

# Validate phone entry box function
def validate_phone(u_input):
    if(re.search(phoneregex, u_input) and u_input.isalpha):
        phone_label_error.grid_remove()
        if not email_label_error.grid_info():
            btn_upd.config(state='normal', cursor="hand2")  
        return True        
    elif (len(u_input)==0):
        btn_upd.config(state='disabled', cursor="")  
        phone_label_error.configure(text="Invalid Empty Field!")
        phone_label_error.grid(row=15, column=0, columnspan=2, sticky="se", padx=round(60*ratio), pady=(round(10*ratio), 0))
        return True    
    else:
        btn_upd.config(state='disabled', cursor="") 
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
        btn_passupd.config(state='normal', cursor="hand2")
    else:
        btn_passupd.config(state='disabled', cursor="")
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
        fbtn_save.config(state='normal', cursor="hand2")
    else:
        fbtn_save.config(state='disabled', cursor="")

# Search all user function
def serachAllUser():
    loading(usermanageWindow)
    try:
        mysql_con = MySqlConnector(sql_config) # Initial connection
        sql = '''SELECT * FROM User WHERE user_role = 2'''
        result_details = mysql_con.queryall(sql)
        if result_details:
            usermanageWindow.attributes('-disabled', 0)
            loading_splash.destroy()
            return result_details
        # If no existing data found
        else:
            result = None
            usermanageWindow.attributes('-disabled', 0)
            loading_splash.destroy()
            messagebox.showinfo("No User Data Found", "There was no existing monitoring employee found in the system!")
            return result_details
    except pymysql.Error as e:
        messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
        print("Error %d: %s" % (e.args[0], e.args[1]))
        return False
    finally:
        # Close the connection
        mysql_con.close()

# Search user based on filter function
def searchUserByFilter(value, opt):
    if opt == 'All':
        try:
            mysql_con = MySqlConnector(sql_config) # Initial connection
            loading(usermanageWindow)
            sql = '''SELECT * FROM User WHERE user_role = 2'''
            result_details = mysql_con.queryall(sql)
            if result_details:
                usrmng_tree.delete(*usrmng_tree.get_children())
                usrmng_count = 0
                for dt in result_details:
                    if usrmng_count % 2 == 0:
                        usrmng_tree.insert("", 'end', values=(dt[0], dt[1], dt[2], dt[4], dt[5], dt[7], dt[6], dt[8], dt[9], dt[12]), tags=('evenrow',))
                    else:
                        usrmng_tree.insert("", 'end', values=(dt[0], dt[1], dt[2], dt[4], dt[5], dt[7], dt[6], dt[8], dt[9], dt[12]), tags=('oddrow',))
                    usrmng_count +=1
                usermanageWindow.attributes('-disabled', 0)
                loading_splash.destroy()
            # If no existing data found
            else:
                result_details = None
                usrmng_tree.delete(*usrmng_tree.get_children())
                usrmng_count = 0
                usermanageWindow.attributes('-disabled', 0)
                loading_splash.destroy()
                messagebox.showinfo("No User Data Found", "There was no existing monitoring employee found in the system!")
        except pymysql.Error as e:
            messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            # Close the connection
            mysql_con.close()
    else:
        if not value:
            message = "The value field should not be empty for " + opt + " fitlration option!"
            messagebox.showerror("Invalid Empty Field", message)
            filterfield_text.focus()
        else:
            try:
                mysql_con = MySqlConnector(sql_config) # Initial connection
                loading(usermanageWindow)
                if opt == 'User ID':
                    sql = '''SELECT * FROM User WHERE user_role = 2 AND user_id LIKE CONCAT('%%', %s, '%%')'''
                elif opt == 'First Name':
                    sql = '''SELECT * FROM User WHERE user_role = 2 AND user_firstname LIKE CONCAT('%%', %s, '%%')'''
                elif opt == 'Last Name':
                    sql = '''SELECT * FROM User WHERE user_role = 2 AND user_lastname LIKE CONCAT('%%', %s, '%%')'''
                elif opt == 'Email':
                    sql = '''SELECT * FROM User WHERE user_role = 2 AND user_email LIKE CONCAT('%%', %s, '%%')'''
                else:
                    sql = '''SELECT * FROM User WHERE user_role = 2 AND user_phone LIKE CONCAT('%%', %s, '%%')'''
                result_details1 = mysql_con.queryall(sql, (value))
                if result_details1:
                    usrmng_tree.delete(*usrmng_tree.get_children())
                    usrmng_count = 0
                    for dt in result_details1:
                        if usrmng_count % 2 == 0:
                            usrmng_tree.insert("", 'end', values=(dt[0], dt[1], dt[2], dt[4], dt[5], dt[7], dt[6], dt[8], dt[9], dt[12]), tags=('evenrow',))
                        else:
                            usrmng_tree.insert("", 'end', values=(dt[0], dt[1], dt[2], dt[4], dt[5], dt[7], dt[6], dt[8], dt[9], dt[12]), tags=('oddrow',))
                        usrmng_count +=1
                    usermanageWindow.attributes('-disabled', 0)
                    loading_splash.destroy()
                # If no existing data found
                else:
                    result_details1 = None
                    usrmng_tree.delete(*usrmng_tree.get_children())
                    usrmng_count = 0
                    usermanageWindow.attributes('-disabled', 0)
                    loading_splash.destroy()
                    messagebox.showinfo("No User Data Found", "There was no such monitoring employee found based on the filtration value!")
            except pymysql.Error as e:
                messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                print("Error %d: %s" % (e.args[0], e.args[1]))
                return False
            finally:
                # Close the connection
                mysql_con.close()
       
# Filter user callback fucntion
def usrmngcallback(eventObject):
    if filter_opt.get() == 'All':
        filterfield_text.delete(0, 'end')
        filterfield_text.config(state='disabled')
    else:
        filterfield_text.config(state='normal')
        filterfield_text.focus()
    
# Generate random password function
def generate_temppassword():
    temp_pass = ''.join((secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(8)))
    return temp_pass

# Reset password for user
def reset_password(email, err_lbl):
    email_con = email.get()
    
    if not email_con:
        err_lbl.config(text="The email field should not be empty!")
        email.focus()
    elif not (re.search(emailregex, email_con) and email_con.isalpha):
        err_lbl.config(text="Invalid email format!")
        email.focus() 
    else:
        try:
            mysql_con = MySqlConnector(sql_config) # Initial connection
            sql = '''SELECT * FROM User WHERE user_email = (%s)'''
            result_details = mysql_con.queryall(sql, (email_con))
            if result_details:
                global existed
                existed = True
                err_lbl.config(text="")
            # If no existing data found
            else:
                existed = False
                err_lbl.config(text="We cannot find your email!")
        except pymysql.Error as e:
            messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
            print("Error %d: %s" % (e.args[0], e.args[1]))
            return False
        finally:
            # Close the connection
            mysql_con.close()
            
        if existed:
            loading(forgetpassWindow)
            forgetpassWindow.update()
            # Generate random pass
            temp = generate_temppassword()
            # Update the password
            try:
                mysql_con = MySqlConnector(sql_config) # Initial connection
                sql = '''UPDATE User SET user_password = SHA2(%s, 256), user_firstLogin = 1 WHERE user_email = (%s)'''
                update = mysql_con.update(sql, (temp, email_con))
                if update > 0:
                    # Send email to the user
                    emailtxt = [email_con]
                    send = mail_resetpass(emailtxt, temp)
                    if send:
                        messagebox.showinfo("Password Reset Successful", "Your password had been reset. Please check your email in order to login.")
                        forgetpassWindow.attributes('-disabled', 0)
                        loading_splash.destroy()    
                        forgetpassWindow.destroy() # Close the interface
                        root.attributes('-disabled', 0)
                        root.focus_force()
                    else:
                        messagebox.showinfo("Password Reset Process Not Complete", "Your password had been reset but email was not generated due to server error! Please contact developer for help!")
                        forgetpassWindow.attributes('-disabled', 0)
                        loading_splash.destroy() 
                        forgetpassWindow.destroy() # Close the interface
                        root.attributes('-disabled', 0)
                        root.focus_force()
                # If error
                else:
                    messagebox.showerror("Passord Reset Failed", "Failed to reset your password! Please contact developer for help!")
                    forgetpassWindow.attributes('-disabled', 0)
                    loading_splash.destroy() 
                    forgetpassWindow.destroy() # Close the interface
                    root.attributes('-disabled', 0)
                    root.focus_force()
            except pymysql.Error as e:
                messagebox.showerror("Database Connection Error", "Error occured in database server! Please contact developer for help!")
                print("Error %d: %s" % (e.args[0], e.args[1]))
                return False
            finally:
                # Close the connection
                mysql_con.close()


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
width1 = round(cscreen_width*0.8333)
height1 = round(cscreen_height*0.8333)
root.minsize(width1, height1)
x1 = (cscreen_width/2)-(width1/2)
y1 = (cscreen_height/2)-(height1/2)-round(40)
root.geometry(f'{width1}x{height1}+{round(x1)}+{round(y1)}')
root.call('tk', 'scaling', 1.34)

# Configure row column attribute
root.grid_columnconfigure(0, weight=round(1*ratio))
root.grid_columnconfigure(1, weight=round(1*ratio))
root.grid_rowconfigure(9, weight=round(1*ratio))

# Setup frames
login_banner = Frame(root, width=round(cscreen_width/2), height=round(cscreen_height))
login_banner.grid(row=0, column=0, rowspan=10, sticky="nsew")
login_component = Frame(root, width=round(cscreen_width/2), height=round(cscreen_height))
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
canva = ResizingCanvas(login_component, width=round(cscreen_width/2), height=round(cscreen_height), bg="#2b2f3b", highlightthickness=0)
canva.pack(fill=BOTH, expand=YES)
img = Image.open('asset/logo_round.png')
img = img.resize((round((img.size[0]/2.5)*ratio), round((img.size[0]/2.5)*ratio)))
img = ImageTk.PhotoImage(img)
frame = Frame(root, bg="#2b2f3b")
frame.grid(row=0, column=1, padx=round(100*ratio), pady=(round(120*ratio),0), sticky="nsw")
img_label = Label(frame, image=img, bg="#2b2f3b")
img_label.image = img
img_label.pack()
login_title = Label(root, text="Login to Account", font=("Arial Rounded MT Bold", round(34*ratio)), bg="#2b2f3b", fg="white")
login_title.grid(row=1, column=1, sticky="w", padx=round(100*ratio))
login_desc = Label(root, text="Enter your login data created in below section", font=("Lato", round(12*ratio)), bg="#2b2f3b", fg="white")
login_desc.grid(row=2, column=1, sticky="w", padx=round(100*ratio))
lbl_email = Label(root, text="Email", font=("Arial Rounded MT Bold", round(14*ratio)), bg="#2b2f3b", fg="white")
lbl_email.grid(row=3, column=1, sticky="w", padx=round(100*ratio), pady=(round(65*ratio),round(5*ratio)))
emlerror_lbl = Label(root, text="", font=("Lato bold", round(10*ratio)), bg="#2b2f3b", fg="red")
emlerror_lbl.grid(row=3, column=1, sticky="e", padx=round(100*ratio), pady=(round(65*ratio),round(5*ratio)))
frame1 = Frame(root, highlightbackground="#d1d1d1", highlightthickness=1)
frame1.grid(row=4, column=1, sticky="nsew", padx=round(100*ratio))
txt_email = Entry(frame1, bd=round(17*ratio), relief=FLAT, font=("Lato", round(14*ratio)))
txt_email.pack(expand=True, fill=BOTH)
lbl_pass = Label(root, text="Password", font=("Arial Rounded MT Bold", round(14*ratio)), bg="#2b2f3b", fg="white")
lbl_pass.grid(row=5, column=1, sticky="w", padx=round(100*ratio), pady=round(5*ratio))
pserror_lbl = Label(root, text="", font=("Lato bold", round(10*ratio)), bg="#2b2f3b", fg="red")
pserror_lbl.grid(row=5, column=1, sticky="e", padx=round(100*ratio), pady=round(5*ratio))
frame2 = Frame(root, highlightbackground="#d1d1d1", highlightthickness=1, bg="white")
frame2.grid(row=6, column=1, sticky="nsew", padx=round(100*ratio))
txt_pass = Entry(frame2, bd=round(17*ratio), relief=FLAT, font=("Lato", round(14*ratio)), show="*", bg="white")
txt_pass.pack(expand=True, fill=BOTH, side=LEFT)
passwordShown  = False
hide_icon = Image.open('asset/hide_pass.png')
hide_icon = hide_icon.resize((round(35*ratio),round(35*ratio)), Image.ANTIALIAS)
hide_icon = ImageTk.PhotoImage(hide_icon)
hide_pass = Button(frame2, image=hide_icon, bg="white", relief=FLAT, bd=0, activebackground="white", command=lambda:showpass(), cursor="hand2")
hide_pass.image = hide_icon
show_icon = Image.open('asset/show_pass.png')
show_icon = show_icon.resize((round(35*ratio),round(35*ratio)), Image.ANTIALIAS)
show_icon = ImageTk.PhotoImage(show_icon)
show_pass = Button(frame2, image=show_icon, bg="white", relief=FLAT, bd=0, activebackground="white", command=lambda:showpass())
show_pass.image = show_icon
hide_pass.pack(side=RIGHT, padx=round(10*ratio), fill=BOTH)
CreateToolTip(hide_pass, text = 'Show Password')
CreateToolTip(show_pass, text = 'Hide Password')
frame3 = Frame(root, bg="#2b2f3b")
frame3.grid(row=7, column=1, sticky="ne", padx=round(100*ratio), pady=round(10*ratio))
forget_pass = Button(frame3, command=lambda:forgetpassPage(), text="Forget password?", font=("Arial Rounded MT Bold", round(11*ratio)), bg="#2b2f3b", activebackground="#2b2f3b", relief=FLAT, bd=0, fg="white", activeforeground="white", cursor="hand2")
forget_pass.pack(side=RIGHT)
btn_login = Button(root, text="Login Account", command=lambda:login(txt_email, txt_pass, emlerror_lbl, pserror_lbl), font=("Arial Rounded MT Bold", round(16*ratio)), height=2, fg="white", bg="#0170e3", relief=RIDGE, bd=1, activebackground="#025BB7", activeforeground="white", cursor="hand2")
btn_login.grid(row=7, column=1, sticky="sew", padx=round(100*ratio), pady=(round(70*ratio),round(40*ratio)))
lbl_reg = Label(root, text="Don't have account? Please contact company's Admin", font=("Lato", round(12*ratio)), bg="#2b2f3b", fg="white")
lbl_reg.grid(row=8, column=1, sticky="w", padx=round(100*ratio))


#==============================================================================================#
#                                    System Theme Styling                                      #
#==============================================================================================#
style = ttk.Style()
# Create custom styling for management page
mngstyle = ttk.Style()
mngstyle.theme_create('mngstyle', parent='clam', settings = 
        {
        'TCombobox': 
            {'configure': {'selectbackground': 'white',
                           'fieldbackground': 'white',
                           'background': 'white',
                           'bordercolor':'#c4cbd2',
                           'selectforeground': 'black',
                           'padding': (round(5*ratio),round(5*ratio),round(5*ratio),round(5*ratio))}},
        'Treeview': 
            {'configure': {'background': 'white',
                           'foreground': 'black',
                           'rowheight': round(30*ratio),
                           'fieldbackground':'white',
                           'font': ("Lato", round(10*ratio))}},
        'Treeview.Heading': 
            {'configure': {'background': '#01987a',
                           'foreground': 'white',
                           'fieldbackground':'white',
                           'font': ("Franklin Gothic Medium Cond", round(12*ratio))}}
        }
    )


#==============================================================================================#
#                                         Main Page                                            #
#==============================================================================================#
## Main Page Interface
def forgetpassPage():
    global forgetpassWindow
    
    # Configure window attribute
    root.attributes('-disabled', 1)
    forgetpassWindow = Toplevel(root)
    forgetpassWindow.grab_set()
    forgetpassWindow.overrideredirect(True)
    height = round(450*ratio)
    width = round(1000*ratio)
    x = (cscreen_width/2)-(width/2)
    y = (cscreen_height/2)-(height/2)
    forgetpassWindow.geometry(f'{width}x{height}+{round(x)}+{round(y)}')
    style.theme_use('default')
    
    # Configure row column attribute
    forgetpassWindow.grid_rowconfigure(5, weight=round(1*ratio))
    
    # Setup frames
    overall = Frame(forgetpassWindow, highlightbackground="#A9A9A9", highlightthickness=1, relief=RIDGE)
    overall.grid(row=0, column=0, rowspan=6, columnspan=2, sticky="nsew")
    left_frame = Frame(forgetpassWindow, width=round(cscreen_width*0.3125), height=round(cscreen_height*0.417), bg="white")
    left_frame.grid(row=0, column=0, rowspan=6, sticky="nsew", padx=(1,0), pady=1)
    right_frame = Frame(forgetpassWindow, width=round(cscreen_width*0.2083), height=round(cscreen_height*0.417), bg="white")
    right_frame.grid(row=0, column=1, rowspan=6, sticky="nsew", padx=(0,1), pady=1)
    
    # Left banner
    left_banner = Image.open('asset/forgetpass_banner.png')
    left_banner = left_banner.resize((round(600*ratio),round(450*ratio)), Image.ANTIALIAS)
    left_banner = ImageTk.PhotoImage(left_banner)
    leftb_lbl = Label(left_frame, image=left_banner, bg="white", relief=FLAT, bd=0)
    leftb_lbl.image = left_banner
    leftb_lbl.pack(expand=TRUE, fill=BOTH)
    
    # Right component
    forgot_lbl = Label(forgetpassWindow, text="Forgot Password", font=("Arial Rounded MT Bold", round(18*ratio)), bg="white")
    forgot_lbl.grid(row=0, column=1, sticky="nsew", padx=round(40*ratio), pady=(round(80*ratio), 0))
    desc_lbl = Label(forgetpassWindow, text="Enter your email and we'll assist you to reset your password.", font=("Lato", round(10*ratio)), wraplength=round(300*ratio), bg="white", fg="#787a82")
    desc_lbl.grid(row=1, column=1, sticky="nsew", padx=round(40*ratio), pady=round(15*ratio))
    f0 = Frame(forgetpassWindow, highlightbackground="#71c577", highlightthickness=1, highlightcolor="#71c577", bg="#f6fff7")
    f0.grid(row=2, column=1, padx=round(40*ratio), pady=(round(20*ratio),round(10*ratio)), sticky="nsew")
    email_icon = Image.open('asset/email_icon.png')
    email_icon = email_icon.resize((round(30*ratio),round(30*ratio)))
    email_icon = ImageTk.PhotoImage(email_icon)
    emailicon_lbl = Label(f0, image=email_icon, bg="#f6fff7")
    emailicon_lbl.image = email_icon
    emailicon_lbl.pack(side=LEFT, fill=BOTH, padx=(round(5*ratio),0))
    eml_text = Entry(f0, bd=round(14*ratio), relief=FLAT, font=("Lato", round(11*ratio)), bg="#f6fff7")
    eml_text.pack(side=RIGHT, expand=TRUE, fill=BOTH)
    error_lbl = Label(forgetpassWindow, text="", font=("Lato bold", round(10*ratio)), bg="white", fg="red")
    error_lbl.grid(row=3, column=1, padx=round(40*ratio), sticky="nsw")
    f1 = Frame(forgetpassWindow, bd=round(8*ratio), bg="#71c577")
    f1.grid(row=4, column=1, padx=round(40*ratio), pady=(round(25*ratio),round(10*ratio)), sticky="nsew")
    reset_pass = Button(f1, text="Change Password", command=lambda:reset_password(eml_text, error_lbl), font=("Arial Rounded MT Bold", round(12*ratio)), fg="white", bg="#71c577", relief=FLAT, bd=0, activebackground="#71c577", activeforeground="white", cursor="hand2")
    reset_pass.pack(expand=TRUE, fill=BOTH)
    f2 = Frame(forgetpassWindow, bd=round(8*ratio), bg="white")
    f2.grid(row=5, column=1, padx=round(40*ratio), sticky="new")
    back_login = Button(f2, text="Back to Login", command=lambda:backlogin(forgetpassWindow), font=("Arial Rounded MT Bold", round(10*ratio)), fg="#71c577", bg="white", relief=FLAT, bd=0, activebackground="white", activeforeground="#71c577", cursor="hand2")
    back_login.pack(expand=TRUE, fill=BOTH)


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
    style.theme_use('default')
    
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
    video_player.grid(row=0, column=0, rowspan=7, columnspan=3, sticky="nsew", padx=round(25*ratio), pady=(round(30*ratio), round(15*ratio)))
    if(usession.user_role == 1):
        btn_frame1 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame1.grid(row=7, rowspan=2, column=0, sticky="nsew")
        btn_mnguserimg = Image.open('asset/manageuser_btn.png')
        btn_mnguserimg = btn_mnguserimg.resize((round(182*ratio),round(50*ratio)), Image.ANTIALIAS)
        btn_mnguserimg = ImageTk.PhotoImage(btn_mnguserimg)
        btn_mnguser = Button(btn_frame1, cursor="hand2", command=lambda:usermanagementPage(), image=btn_mnguserimg, bg="#EDF1F7", relief=FLAT, bd=0, highlightthickness=0, activebackground="#EDF1F7")
        btn_mnguser.image = btn_mnguserimg
        btn_mnguser.pack(pady=(round(10*ratio),0))
        btn_frame2 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame2.grid(row=7, rowspan=2, column=1, sticky="nsew")
        btn_mngcamimg = Image.open('asset/managecam_btn.png')
        btn_mngcamimg = btn_mngcamimg.resize((round(182*ratio),round(50*ratio)), Image.ANTIALIAS)
        btn_mngcamimg = ImageTk.PhotoImage(btn_mngcamimg)
        btn_mngcamera = Button(btn_frame2, cursor="hand2", image=btn_mngcamimg, bg="#EDF1F7", relief=FLAT, bd=0, highlightthickness=0, activebackground="#EDF1F7")
        btn_mngcamera.image = btn_mngcamimg
        btn_mngcamera.pack(pady=(round(10*ratio),0))
        btn_frame3 = Frame(mainWindow, bg="#EDF1F7")
        btn_frame3.grid(row=7, rowspan=2, column=2, sticky="nsew")
        btn_agncamimg = Image.open('asset/assigncam_btn.png')
        btn_agncamimg = btn_agncamimg.resize((round(182*ratio),round(50*ratio)), Image.ANTIALIAS)
        btn_agncamimg = ImageTk.PhotoImage(btn_agncamimg)
        btn_asscamera = Button(btn_frame3, cursor="hand2", image=btn_agncamimg, bg="#EDF1F7", relief=FLAT, bd=0, highlightthickness=0, activebackground="#EDF1F7")
        btn_asscamera.image = btn_agncamimg
        btn_asscamera.pack(pady=(round(10*ratio),0))
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
    btn_profile = Button(btn_frame4, cursor="hand2", text="Profile", command=lambda:profilePage(), font=("Arial Rounded MT Bold", round(13*ratio)), fg="white", bg="#5869F0", relief=RIDGE, bd=1, activebackground="#414EBB", activeforeground="white")
    btn_profile.pack(fill='x')
    btn_frame5 = Frame(mainWindow, bg="#1D253D")
    btn_frame5.grid(row=1, column=4, sticky="nsew", padx=(round(5*ratio), round(30*ratio)), pady=round(10*ratio))
    btn_logout = Button(btn_frame5, cursor="hand2", text="Logout", command=lambda:logout(), font=("Arial Rounded MT Bold", round(13*ratio)), height=1, width=round(15*ratio), fg="white", bg="#FF0000", relief=RIDGE, bd=1, activebackground="#B50505", activeforeground="white")
    btn_logout.pack(fill='x')
    notebookstyle = ttk.Style()
    notebookstyle.theme_use('default')
    notebookstyle.configure('TNotebook', background="#1D253D", borderwidth=round(1*ratio), relief=FLAT)
    notebookstyle.configure('TNotebook.Tab', font=("Arial Rounded MT Bold", round(11*ratio)), background="#34415B", borderwidth=round(1*ratio), relief=FLAT, foreground="white", padding=(round(30*ratio),round(5*ratio),round(30*ratio),round(5*ratio)))
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
    btn_refresh = Button(btn_frame6, cursor="hand2", text="Refresh Accident List", font=("Arial Rounded MT Bold", round(13*ratio)), height=1, width=round(32*ratio), fg="white", bg="#5869F0", relief=RIDGE, bd=1, activebackground="#414EBB", activeforeground="white")
    btn_refresh.pack(fill='x')
    btn_frame7 = Frame(mainWindow, bg="#1D253D")
    btn_frame7.grid(row=4, column=3, sticky="nsew", padx=(round(30*ratio), round(5*ratio)), pady=(0, round(5*ratio)))
    btn_init = Button(btn_frame7, cursor="hand2", text="Initiate", font=("Arial Rounded MT Bold", round(13*ratio)), height=1, width=round(15*ratio), fg="white", bg="#5869F0", relief=RIDGE, bd=1, activebackground="#414EBB", activeforeground="white")
    btn_init.pack(fill='x')
    btn_frame8 = Frame(mainWindow, bg="#1D253D")
    btn_frame8.grid(row=4, column=4, sticky="nsew", padx=(round(5*ratio), round(30*ratio)), pady=(0, round(5*ratio)))
    btn_stop = Button(btn_frame8, cursor="hand2", text="Stop", font=("Arial Rounded MT Bold", round(13*ratio)), height=1, width=round(15*ratio), fg="white", bg="#5869F0", relief=RIDGE, bd=1, activebackground="#414EBB", activeforeground="white")
    btn_stop.pack(fill='x')
    camera_list = Label(mainWindow, text="Camera List: ", font=("Lato", round(13*ratio)), bg="#1D253D", fg="white")
    camera_list.grid(row=5, column=3, columnspan=2, sticky="w", padx=round(30*ratio), pady=(round(5*ratio),0))
    camera_id = Label(mainWindow, text="Camera ID: ", font=("Lato", round(13*ratio)), bg="#1D253D", fg="white")
    camera_id.grid(row=6, column=3, columnspan=2, sticky="w", padx=round(30*ratio))
    camera_loc = Label(mainWindow, text="Location: ", font=("Lato", round(13*ratio)), bg="#1D253D", fg="white")
    camera_loc.grid(row=7, column=3, columnspan=2, sticky="w", padx=round(30*ratio), pady=(0,round(5*ratio)))
    btn_frame9 = Frame(mainWindow, bg="#1D253D")
    btn_frame9.grid(row=8, column=3, sticky="nsew", padx=(round(30*ratio), round(5*ratio)), pady=(round(5*ratio), round(15*ratio)))
    icon_prev = Image.open('asset/previous_icon.png')
    icon_prev = icon_prev.resize((round(30*ratio),round(30*ratio)), Image.ANTIALIAS)
    icon_prev = ImageTk.PhotoImage(icon_prev)
    btn_prev = Button(btn_frame9, cursor="hand2", image=icon_prev, height=round(30*ratio), width=round(150*ratio), bg="#5869F0", relief=RIDGE, bd=1, activebackground="#414EBB")
    btn_prev.image = icon_prev
    btn_prev.pack(fill='x')
    btn_frame10 = Frame(mainWindow, bg="#1D253D")
    btn_frame10.grid(row=8, column=4, sticky="nsew", padx=(round(5*ratio), round(30*ratio)), pady=(round(5*ratio), round(15*ratio)))
    icon_next = Image.open('asset/next_icon.png')
    icon_next = icon_next.resize((round(30*ratio),round(30*ratio)), Image.ANTIALIAS)
    icon_next = ImageTk.PhotoImage(icon_next)
    btn_next = Button(btn_frame10, cursor="hand2", image=icon_next, height=round(30*ratio), width=round(150*ratio), bg="#5869F0", relief=RIDGE, bd=1, activebackground="#414EBB")
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
        height = round(604*ratio)
        width = round(1004*ratio)
        x = (cscreen_width/2)-(width/2)
        y = (cscreen_height/2)-(height/2)
        wel.geometry(f'{width}x{height}+{round(x)}+{round(y)}')
        # Frame
        overall = Frame(wel, highlightbackground="#A9A9A9", highlightthickness=1, relief=RIDGE)
        overall.grid(row=0, column=0, rowspan=6, columnspan=2, sticky="nsew")
        left_frame = Frame(wel, width=round(cscreen_width*0.2604), height=round(cscreen_height*0.5556), bg="#e0f9ff")
        left_frame.grid(row=0, column=0, rowspan=6, sticky="nsew", padx=(1,0), pady=1)
        right_frame = Frame(wel, width=round(cscreen_width*0.2604), height=round(cscreen_height*0.5556), bg="white")
        right_frame.grid(row=0, column=1, rowspan=6, sticky="nsew", padx=(0,1), pady=1)
        # Left banner
        left_banner = Image.open('asset/welcome_banner.jpg')
        left_banner = left_banner.resize((round(500*ratio),round(600*ratio)), Image.ANTIALIAS)
        left_banner = ImageTk.PhotoImage(left_banner)
        leftb_lbl = Label(left_frame, image=left_banner, bg="#e0f9ff", relief=FLAT, bd=0)
        leftb_lbl.image = left_banner
        leftb_lbl.pack(expand=TRUE, fill=BOTH)
        # Right Component
        wel_lbl = Label(wel, text="Welcome!", font=("Arial Rounded MT Bold", round(20*ratio)), bg="white")
        wel_lbl.grid(row=0, column=1, padx=round(40*ratio), pady=(round(25*ratio), 0), sticky="nsw")
        f1 = Frame(wel, bg="white")
        f1.grid(row=1, column=1, padx=round(40*ratio), sticky="nsew")
        desc_lbl = Text(f1, font=("Lato", round(12*ratio)), bg="white", wrap=WORD, highlightthickness=0, height=round(3*ratio), width=round(45*ratio), relief=FLAT)
        desc_lbl.pack(side=LEFT, fill=BOTH)
        desc_lbl.insert(INSERT, "To make your account secure, please create a new password to replace the temporary password given initially before continue.")
        desc_lbl.configure(state="disabled")
        f2 = Frame(wel, bg="white")
        f2.grid(row=2, column=1, padx=round(40*ratio), sticky="nsew")
        new_lbl = Label(f2, text="New Password", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white")
        new_lbl.pack(side=LEFT)
        f2a = Frame(f2, highlightbackground="black", highlightthickness=1, highlightcolor="black")
        f2a.pack(expand=TRUE, fill=X, side=RIGHT, padx=(round(100*ratio),0))
        fnewpass_val = StringVar()
        fnewpass_val.trace("w", validate_pass2)
        txt_newpas = Entry(f2a, font=("Lato", round(12*ratio)), relief=FLAT, bd=round(5*ratio), show="*", textvariable=fnewpass_val)
        txt_newpas.pack(expand=TRUE, fill=BOTH)
        f3 = Frame(wel, bg="white")
        f3.grid(row=3, column=1, padx=round(40*ratio), sticky="nsew")
        connew_lbl = Label(f3, text="Confirm New Password", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white")
        connew_lbl.pack(side=LEFT)
        f3a = Frame(f3, highlightbackground="black", highlightthickness=1, highlightcolor="black")
        f3a.pack(expand=TRUE, fill=X, side=RIGHT, padx=(round(30*ratio),0))
        fconpass_val = StringVar()
        fconpass_val.trace("w", validate_pass2)
        txt_cpas = Entry(f3a, font=("Lato", round(12*ratio)), relief=FLAT, bd=round(5*ratio), show="*", textvariable=fconpass_val)
        txt_cpas.pack(expand=TRUE, fill=BOTH)
        # Password validation display
        f4 = Frame(wel, bg="white")
        f4.grid(row=4, column=1, padx=round(40*ratio), pady=(round(10*ratio),0), sticky="nsew")
        passpolicy_label = Label(f4, text="Password Policy Requirements (Red Indicated NOT Fulfiled):", wraplength=round(400*ratio), justify=LEFT, font=("Lato", round(10*ratio)), bg="white", fg="black")
        passpolicy_label.pack(anchor="w")
        fone_empty = Label(f4, text="Password can't be empty!", wraplength=round(400*ratio), justify=LEFT, font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
        fone_empty.pack(anchor="w")
        ftwo_length = Label(f4, text="Password must have a minimum of 8 characters in length!", wraplength=round(400*ratio), justify=LEFT, font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
        ftwo_length.pack(anchor="w")
        fthree_lower = Label(f4, text="Password must have at least one lowercase English letter! (e.g. a-z)", wraplength=round(400*ratio), justify=LEFT, font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
        fthree_lower.pack(anchor="w")
        ffour_upper = Label(f4, text="Password must have at least one uppercase English letter! (e.g. A-Z)", wraplength=round(400*ratio), justify=LEFT, font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
        ffour_upper.pack(anchor="w")
        ffive_digit = Label(f4, text="Password must have at least one digit! (e.g. 0-9)", wraplength=round(400*ratio), justify=LEFT, font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
        ffive_digit.pack(anchor="w")
        fsix_specialchar = Label(f4, text="Password must have at least one accepted special character! (e.g. @$!%*?&)", wraplength=round(400*ratio), justify=LEFT, font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
        fsix_specialchar.pack(anchor="w")
        fseven_con = Label(f4, text="Confirm new password does not match new password", wraplength=round(400*ratio), justify=LEFT, font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
        fseven_con.pack(anchor="w")
        f5 = Frame(wel, bd=round(8*ratio), bg="white")
        f5.grid(row=5, column=1, sticky="new", padx=round(40*ratio))
        fbtn_save = Button(f5, cursor="hand2", command=lambda:usession.firstchange(txt_newpas, txt_cpas), text="Save", font=("Arial Rounded MT Bold", round(12*ratio)), fg="white", bg="#438ae6", relief=FLAT, bd=0, activebackground="#2a5996", activeforeground="white")
        fbtn_save.pack(expand=TRUE, fill=BOTH, ipady=round(5*ratio))
        fbtn_save.config(state='disabled', cursor="") 

    
#==============================================================================================#
#                                         Profile Page                                         #
#==============================================================================================#
## Profile Page Interface
def profilePage(): 
    global profileWindow, name_label, addline_con, city_con, zipcode_con, state_con, email_con, phone_con, canvas
    
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
    style.theme_use('default')
    
    # Configure row column attribute
    profileWindow.grid_rowconfigure(6, weight=round(1*ratio))
    profileWindow.grid_rowconfigure(7, weight=round(3*ratio))
    
    # Setup frames
    left_frame = Frame(profileWindow, width=round(cscreen_width*0.17), bg="#141419", relief=RAISED)
    left_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")
    rightup_frame = Frame(profileWindow, width=round(cscreen_width*0.43), bg="#222429")
    rightup_frame.grid(row=0, column=1, rowspan=3, columnspan=2, sticky="nsew")
    rightdown_frame = Frame(profileWindow, width=round(cscreen_width*0.43), bg="#222429")
    rightdown_frame.grid(row=3, column=1, rowspan=5, columnspan=2, sticky="nsew")
    
    # Left components
    btn_frame1 = Frame(profileWindow, bg="#141419")
    btn_frame1.grid(row=0, column=0, sticky="nsw", padx=round(10*ratio), pady=(round(10*ratio),0))
    backmainbtn(btn_frame1, profileWindow, "#141419")
    avatar_path = 'temp/' + usession.user_avatar + '.png'
    img_avatar = Image.open(avatar_path)
    img_avatar = img_avatar.resize((round(180*ratio),round(180*ratio)), Image.ANTIALIAS)
    img_avatar = ImageTk.PhotoImage(img_avatar)
    imgava_label = Label(profileWindow, image=img_avatar, bg="#141419")
    imgava_label.image = img_avatar
    imgava_label.grid(column=0, row=1, rowspan=2, sticky="nsew")
    page_title = Label(profileWindow, text="Personal Info", font=("Arial Rounded MT Bold", round(18*ratio)), bg="#141419", fg="white")
    page_title.grid(row=3, column=0, sticky="nsew", pady=round(10*ratio))
    btn_frameoverall = Frame(profileWindow, bg="#141419", padx=round(60*ratio))
    btn_frameoverall.grid(row=4, column=0, sticky="nsew")
    btn_frame2 = Frame(btn_frameoverall, bg="#7178c5", bd=round(5*ratio))
    btn_frame2.pack(fill=X, pady=(round(10*ratio), round(5*ratio)))
    btn_upload = Button(btn_frame2, cursor="hand2", command=lambda:usession.upload_avatar(imgava_label), text="Upload New Avatar", font=("Arial Rounded MT Bold", round(10*ratio)), fg="white", bg="#7178c5", relief=FLAT, bd=0, activebackground="#7178c5", activeforeground="white", wraplength=round(160*ratio))
    btn_upload.pack(fill=BOTH)
    CreateToolTip(btn_upload, text = 'Best fit image ratio is 50 50\n'
                 'Accept both PNG and JPG format\n'
                 'Max size limit is 20MB')
    btn_frame3 = Frame(btn_frameoverall, bg="#7178c5", bd=round(5*ratio))
    btn_frame3.pack(fill=X, pady=round(5*ratio))
    btn_edit = Button(btn_frame3, cursor="hand2", command=lambda:updateprofilePage(), text="Edit Profile", font=("Arial Rounded MT Bold", round(10*ratio)), fg="white", bg="#7178c5", relief=FLAT, bd=0, activebackground="#7178c5", activeforeground="white")
    btn_edit.pack(fill=BOTH)
    btn_frame4 = Frame(btn_frameoverall, bg="#7178c5", bd=round(5*ratio))
    btn_frame4.pack(fill=X, pady=round(5*ratio))
    btn_chgpas = Button(btn_frame4, cursor="hand2", command=lambda:updatepassPage(), text="Change Password", font=("Arial Rounded MT Bold", round(10*ratio)), fg="white", bg="#7178c5", relief=FLAT, bd=0, activebackground="#7178c5", activeforeground="white")
    btn_chgpas.pack(fill=BOTH)
    
    # Right components
    canvas = Canvas(rightup_frame, width=round(825*ratio), height=round(260*ratio), bd=0, highlightthickness=0)
    canvas.pack(side=TOP)
    banner_img = Image.open('asset/profile_banner.jpg')
    banner_img = banner_img.resize((round(825*ratio),round(260*ratio)), Image.ANTIALIAS)
    banner_img = ImageTk.PhotoImage(banner_img)
    profileWindow.banner_img = banner_img
    banner_back = canvas.create_image(0,0, image=banner_img, anchor=NW)
    sys_label = canvas.create_text(round(800*ratio), round(20*ratio),text="e-Vision", font=("Arial Rounded MT Bold", round(14*ratio)), fill="black", anchor=NE)
    name_label = canvas.create_text(round(65*ratio), round(215*ratio), text="{}".format(usession.user_firstname+" "+usession.user_lastname), font=("Arial Rounded MT Bold", round(32*ratio)), fill="white", anchor=SW)
    if (usession.user_role == 1):
        txt = 'Admin'
    else:
        txt = 'Monitoring Employee'
    role_label = canvas.create_text(round(65*ratio), round(240*ratio), text="{}".format(txt), font=("Lato", round(15*ratio)), fill="white", anchor=SW)
    frame_holder1 = Frame(rightdown_frame, bg="#0c0c12")
    frame_holder1.pack(side=LEFT, padx=(round(40*ratio), round(20*ratio)), pady=round(40*ratio), fill=BOTH)
    frame_holder2 = Frame(rightdown_frame, bg="#0c0c12")
    frame_holder2.pack(side=RIGHT, padx=(round(20*ratio), round(40*ratio)), pady=round(40*ratio), fill=BOTH)
    left_banner = Image.open('asset/profileleft.png')
    left_banner = left_banner.resize((round(350*ratio),round(85*ratio)), Image.ANTIALIAS)
    left_banner = ImageTk.PhotoImage(left_banner)
    left_banner_label = Label(frame_holder1, image=left_banner, bg="white", relief=FLAT, bd=0)
    left_banner_label.image = left_banner
    left_banner_label.pack(side=TOP)
    f0 = Frame(frame_holder1, bg="#0c0c12")
    f0.pack(anchor=W, padx=round(40*ratio), pady=(round(35*ratio), round(15*ratio)))
    uid_icon = Image.open('asset/employeeid1.png')
    uid_icon = uid_icon.resize((round(30*ratio),round(30*ratio)))
    uid_icon = ImageTk.PhotoImage(uid_icon)
    uid_label = Label(f0, image=uid_icon, bg="#0c0c12")
    uid_label.image = uid_icon
    uid_label.pack(side=LEFT, fill=BOTH, padx=(round(10*ratio), round(5*ratio)))
    uid_con = Label(f0, font=("Lato", round(12*ratio)), bg="#0c0c12", fg="white", relief=FLAT, wraplength=round(200*ratio), justify=LEFT)
    uid_con.pack(side=RIGHT, expand=TRUE, fill=BOTH, padx=(round(5*ratio),round(10*ratio)))
    uid_con.configure(text="{}".format(usession.user_id))
    f1 = Frame(frame_holder1, bg="#0c0c12")
    f1.pack(anchor=W, padx=round(40*ratio), pady=round(15*ratio))
    email_icon = Image.open('asset/email1.png')
    email_icon = email_icon.resize((round(30*ratio),round(30*ratio)))
    email_icon = ImageTk.PhotoImage(email_icon)
    email_label = Label(f1, image=email_icon, bg="#0c0c12")
    email_label.image = email_icon
    email_label.pack(side=LEFT, fill=BOTH, padx=(round(10*ratio), round(5*ratio)))
    email_con = Label(f1, font=("Lato", round(12*ratio)), bg="#0c0c12", fg="white", relief=FLAT, wraplength=round(200*ratio), justify=LEFT)
    email_con.pack(side=RIGHT, expand=TRUE, fill=BOTH, padx=(round(5*ratio),round(10*ratio)))
    email_con.configure(text="{}".format(usession.user_email))
    f2 = Frame(frame_holder1, bg="#0c0c12")
    f2.pack(anchor=W, padx=round(40*ratio), pady=round(15*ratio))
    phone_icon = Image.open('asset/phone1.png')
    phone_icon = phone_icon.resize((round(30*ratio),round(30*ratio)))
    phone_icon = ImageTk.PhotoImage(phone_icon)
    phone_label = Label(f2, image=phone_icon, bg="#0c0c12")
    phone_label.image = phone_icon
    phone_label.pack(side=LEFT, fill=BOTH, padx=(round(10*ratio), round(5*ratio)))
    phone_con = Label(f2, font=("Lato", round(12*ratio)), bg="#0c0c12", fg="white", relief=FLAT, wraplength=round(200*ratio), justify=LEFT)
    phone_con.pack(side=RIGHT, expand=TRUE, fill=BOTH, padx=(round(5*ratio),round(10*ratio)))
    phone_con.configure(text="{}".format(usession.user_phone))
    right_banner = Image.open('asset/profileright.png')
    right_banner = right_banner.resize((round(350*ratio),round(85*ratio)), Image.ANTIALIAS)
    right_banner = ImageTk.PhotoImage(right_banner)
    right_banner_label = Label(frame_holder2, image=right_banner, bg="white", relief=FLAT, bd=0)
    right_banner_label.image = right_banner
    right_banner_label.pack(side=TOP)
    f3 = Frame(frame_holder2, bg="#0c0c12")
    f3.pack(anchor=W, padx=round(40*ratio), pady=(round(25*ratio), round(8*ratio)))
    addline_icon = Image.open('asset/addressline1.png')
    addline_icon = addline_icon.resize((round(30*ratio),round(30*ratio)))
    addline_icon = ImageTk.PhotoImage(addline_icon)
    addline_label = Label(f3, image=addline_icon, bg="#0c0c12")
    addline_label.image = addline_icon
    addline_label.pack(side=LEFT, fill=BOTH, padx=(round(10*ratio), round(5*ratio)))
    addline_con = Label(f3, font=("Lato", round(12*ratio)), bg="#0c0c12", fg="white", relief=FLAT, wraplength=round(200*ratio), justify=LEFT)
    addline_con.pack(side=RIGHT, expand=TRUE, fill=BOTH, padx=(round(5*ratio),round(10*ratio)))
    addline_con.configure(text="{}".format(usession.user_addressline))
    f4 = Frame(frame_holder2, bg="#0c0c12")
    f4.pack(anchor=W, padx=round(40*ratio), pady= round(8*ratio))
    city_icon = Image.open('asset/city1.png')
    city_icon = city_icon.resize((round(30*ratio),round(30*ratio)))
    city_icon = ImageTk.PhotoImage(city_icon)
    city_label = Label(f4, image=city_icon, bg="#0c0c12")
    city_label.image = city_icon
    city_label.pack(side=LEFT, fill=BOTH, padx=(round(10*ratio), round(5*ratio)))
    city_con = Label(f4, font=("Lato", round(12*ratio)), bg="#0c0c12", fg="white", relief=FLAT, wraplength=round(200*ratio), justify=LEFT)
    city_con.pack(side=RIGHT, expand=TRUE, fill=BOTH, padx=(round(5*ratio),round(10*ratio)))
    city_con.configure(text="{}".format(usession.user_city))
    f5 = Frame(frame_holder2, bg="#0c0c12")
    f5.pack(anchor=W, padx=round(40*ratio), pady= round(8*ratio))
    zipcode_icon = Image.open('asset/zipcode1.png')
    zipcode_icon = zipcode_icon.resize((round(30*ratio),round(30*ratio)))
    zipcode_icon = ImageTk.PhotoImage(zipcode_icon)
    zipcode_label = Label(f5, image=zipcode_icon, bg="#0c0c12")
    zipcode_label.image = zipcode_icon
    zipcode_label.pack(side=LEFT, fill=BOTH, padx=(round(10*ratio), round(5*ratio)))
    zipcode_con = Label(f5, font=("Lato", round(12*ratio)), bg="#0c0c12", fg="white", relief=FLAT, wraplength=round(200*ratio), justify=LEFT)
    zipcode_con.pack(side=RIGHT, expand=TRUE, fill=BOTH, padx=(round(5*ratio),round(10*ratio)))
    zipcode_con.configure(text="{}".format(usession.user_postcode))
    f6 = Frame(frame_holder2, bg="#0c0c12")
    f6.pack(anchor=W, padx=round(40*ratio), pady= round(8*ratio))
    state_icon = Image.open('asset/state1.png')
    state_icon = state_icon.resize((round(30*ratio),round(30*ratio)))
    state_icon = ImageTk.PhotoImage(state_icon)
    state_label = Label(f6, image=state_icon, bg="#0c0c12")
    state_label.image = state_icon
    state_label.pack(side=LEFT, fill=BOTH, padx=(round(10*ratio), round(5*ratio)))
    state_con = Label(f6, font=("Lato", round(12*ratio)), bg="#0c0c12", fg="white", relief=FLAT, wraplength=round(200*ratio), justify=LEFT)
    state_con.pack(side=RIGHT, expand=TRUE, fill=BOTH, padx=(round(5*ratio),round(10*ratio)))
    state_con.configure(text="{}".format(usession.user_state))
    
    
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
    style.theme_use('mngstyle')
    
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
    uid_label = Label(updprofileWindow, text="User ID", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    uid_label.grid(row=1, column=0, columnspan=2, sticky="sw", padx=round(60*ratio))
    f0 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f0.grid(row=2, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    uid_text = Entry(f0, bd=round(3*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio))
    uid_text.pack(fill=BOTH, expand=True)
    uid_text.insert(INSERT, "{}".format(usession.user_id))
    uid_text.configure(state="disabled")
    ufname_label = Label(updprofileWindow, text="First Name", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    ufname_label.grid(row=3, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    fname_label_error = Label(updprofileWindow, text="Invalid Empty Field!", font=("Arial Rounded MT Bold", round(9*ratio)), bg="white", fg="red")
    f1 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f1.grid(row=4, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    ufname_val = StringVar()
    my_valid3 = updprofileWindow.register(fnamevalidation)
    ufname_text = Entry(f1, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=ufname_val)
    ufname_text.pack(fill=BOTH, expand=True)
    ufname_text.insert(INSERT, "{}".format(usession.user_firstname))
    ufname_text.config(validate="key", validatecommand=(my_valid3, '%P'))
    CreateToolTip(ufname_text, text = 'Max length should only be 30 characters')
    ulname_label = Label(updprofileWindow, text="Last Name", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    ulname_label.grid(row=5, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    lname_label_error = Label(updprofileWindow, text="Invalid Empty Field!", font=("Arial Rounded MT Bold", round(9*ratio)), bg="white", fg="red")
    f2 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f2.grid(row=6, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    ulname_val = StringVar()
    my_valid4 = updprofileWindow.register(lnamevalidation)
    ulname_text = Entry(f2, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=ulname_val)
    ulname_text.pack(fill=BOTH, expand=True)
    ulname_text.insert(INSERT, "{}".format(usession.user_lastname))
    ulname_text.config(validate="key", validatecommand=(my_valid4, '%P'))
    CreateToolTip(ulname_text, text = 'Max length should only be 30 characters')
    add_label = Label(updprofileWindow, text="Address Line", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    add_label.grid(row=7, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    add_label_error = Label(updprofileWindow, text="Invalid Empty Field!", font=("Arial Rounded MT Bold", round(9*ratio)), bg="white", fg="red")
    f3 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f3.grid(row=8, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    add_val = StringVar()
    my_valid5 = updprofileWindow.register(addvalidation)
    add_text = Entry(f3, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=add_val)
    add_text.pack(fill=BOTH, expand=True)
    add_text.insert(INSERT, "{}".format(usession.user_addressline))
    add_text.config(validate="key", validatecommand=(my_valid5, '%P'))
    CreateToolTip(add_text, text = 'Max length should only be 255 characters')
    city_label = Label(updprofileWindow, text="City", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    city_label.grid(row=9, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    city_label_error = Label(updprofileWindow, text="Invalid Empty Field!", font=("Arial Rounded MT Bold", round(9*ratio)), bg="white", fg="red")
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
    post_label = Label(updprofileWindow, text="Postal Code", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
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
    state_label = Label(updprofileWindow, text="State", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    state_label.grid(row=11, column=1, sticky="sw", padx=(round(15*ratio), round(60*ratio)), pady=(round(10*ratio), 0))
    f5 = Frame(updprofileWindow, relief=SUNKEN)
    f5.grid(row=12, column=1, padx=(round(10*ratio), round(60*ratio)), sticky="ne")
    state_val = StringVar()
    state_text = ttk.Combobox(f5, font=("Lato", round(13*ratio)), textvariable=state_val, state='readonly', background="white")
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
    email_label = Label(updprofileWindow, text="Email", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    email_label.grid(row=13, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    email_label_error = Label(updprofileWindow, text="Improper Email Format!", font=("Arial Rounded MT Bold", round(9*ratio)), bg="white", fg="red")
    f6 = Frame(updprofileWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f6.grid(row=14, column=0, columnspan=2, padx=round(60*ratio), sticky="new")
    email_val = StringVar()
    my_valid = updprofileWindow.register(validate_email)
    email_text = Entry(f6, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=email_val)
    email_text.pack(fill=BOTH, expand=True)
    email_text.insert(INSERT, "{}".format(usession.user_email))
    email_text.config(validate="key", validatecommand=(my_valid, '%P'))
    CreateToolTip(email_text, text = 'e.g. dummy@xyz.com')
    phone_label = Label(updprofileWindow, text="Phone Number", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    phone_label.grid(row=15, column=0, columnspan=2, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    phone_label_error = Label(updprofileWindow, text="Improper Phone Number Format!", font=("Arial Rounded MT Bold", round(9*ratio)), bg="white", fg="red")
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
    btn_upd = Button(f8, cursor="hand2", text="Update", command=lambda:usession.updateprofile(ufname_text, ulname_text, add_text, city_text, state_text, post_text, email_text, phone_text), font=("Arial Rounded MT Bold", round(12*ratio)), height=1, width=round(13*ratio), fg="white", bg="#1F5192", relief=RIDGE, bd=1, activebackground="#173B6A", activeforeground="white")
    btn_upd.pack()
    f9 = Frame(updprofileWindow, bg="white")
    f9.grid(row=17, column=1, sticky="nsw", padx=(round(50*ratio),0), pady=round(15*ratio))
    btn_close = Button(f9, cursor="hand2", text="Close", command=lambda:closeupdprofile(), font=("Arial Rounded MT Bold", round(12*ratio)), height=1, width=round(13*ratio), fg="black", bg="white", relief=RIDGE, bd=1, activebackground="#DCDCDC", activeforeground="black")
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
    style.theme_use('default')
    
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
    oldpass_label = Label(f1a, text="Old Password", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    oldpass_label.pack()
    f1 = Frame(updpassWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f1.grid(row=1, column=1, sticky="nse", padx=(0, round(40*ratio)))
    oldpass_val = StringVar()
    oldpass_val.trace("w", validate_pass1)
    oldpass_text = Entry(f1, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(20*ratio), show="*", textvariable=oldpass_val)
    oldpass_text.pack()
    f2a = Frame(updpassWindow, bg="white")
    f2a.grid(row=2, column=0, sticky="nsw", padx=(round(40*ratio), 0), pady=round(20*ratio))
    newpass_label = Label(f2a, text="New Password", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    newpass_label.pack()
    f2 = Frame(updpassWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f2.grid(row=2, column=1, sticky="nse", pady=round(20*ratio), padx=(0, round(40*ratio)))
    newpass_val = StringVar()
    newpass_val.trace("w", validate_pass1)
    newpass_text = Entry(f2, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(20*ratio), show="*", textvariable=newpass_val)
    newpass_text.pack()
    f3a = Frame(updpassWindow, bg="white")
    f3a.grid(row=3, column=0, sticky="nsw", padx=(round(40*ratio), 0))
    connewpass_label = Label(f3a, text="Confirm New Password", font=("Arial Rounded MT Bold", round(13*ratio)), bg="white", fg="black")
    connewpass_label.pack()
    f3 = Frame(updpassWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f3.grid(row=3, column=1, sticky="nse", padx=(0, round(40*ratio)))
    conpass_val = StringVar()
    conpass_val.trace("w", validate_pass1)
    connewpass_text = Entry(f3, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(20*ratio), show="*", textvariable=conpass_val)
    connewpass_text.pack()
    passpolicy_label = Label(updpassWindow, text="Password Policy Requirements (Red Indicated NOT Fulfiled):", font=("Lato", round(10*ratio)), bg="white", fg="black")
    passpolicy_label.grid(row=4, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0), pady=(round(30*ratio), 0))
    one_empty = Label(updpassWindow, text="Password can't be empty!", font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
    one_empty.grid(row=5, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    two_length = Label(updpassWindow, text="Password must have a minimum of 8 characters in length!", font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
    two_length.grid(row=6, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    three_lower = Label(updpassWindow, text="Password must have at least one lowercase English letter! (e.g. a-z)", font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
    three_lower.grid(row=7, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    four_upper = Label(updpassWindow, text="Password must have at least one uppercase English letter! (e.g. A-Z)", font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
    four_upper.grid(row=8, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    five_digit = Label(updpassWindow, text="Password must have at least one digit! (e.g. 0-9)", font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
    five_digit.grid(row=9, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    six_specialchar = Label(updpassWindow, text="Password must have at least one accepted special character! (e.g. @$!%*?&)", wraplength=round(400*ratio), justify="left", font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
    six_specialchar.grid(row=10, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio)))
    seven_con = Label(updpassWindow, text="Confirm new password does not match new password!", font=("Arial Rounded MT Bold", round(10*ratio)), bg="white", fg="red")
    seven_con.grid(row=11, column=0, columnspan=2, sticky="nsw", padx=(round(40*ratio), 0))
    f4 = Frame(updpassWindow ,bg="white")
    f4.grid(row=12, column=0, sticky="nse", pady=round(30*ratio), padx=(0, round(30*ratio)))
    btn_passupd = Button(f4, text="Update", command=lambda:usession.updatepass(oldpass_text, newpass_text, connewpass_text), font=("Arial Rounded MT Bold", round(12*ratio)), height=1, width=round(13*ratio), fg="white", bg="#1F5192", relief=RIDGE, bd=1, activebackground="#173B6A", activeforeground="white")
    btn_passupd.pack()
    btn_passupd.config(state='disabled')
    f5 = Frame(updpassWindow, bg="white")
    f5.grid(row=12, column=1, sticky="nsw", pady=round(30*ratio), padx=(round(45*ratio), 0))
    btn_passclose = Button(f5, cursor="hand2", text="Close", command=lambda:closechgpass(), font=("Arial Rounded MT Bold", round(12*ratio)), height=1, width=round(13*ratio), fg="black", bg="white", relief=RIDGE, bd=1, activebackground="#DCDCDC", activeforeground="black")
    btn_passclose.pack()

#==============================================================================================#
#                                   Admin - Manage User Page                                   #
#==============================================================================================#
## Admin - Manage User Page Interface
def usermanagementPage():
    global usermanageWindow, filterfield_text, filter_opt, usrmng_tree
    
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
    style.theme_use('mngstyle')
    
    # Configure row column attribute
    usermanageWindow.grid_columnconfigure(2, weight=round(1*ratio))
    usermanageWindow.grid_columnconfigure(3, weight=round(2*ratio))
    usermanageWindow.grid_columnconfigure(4, weight=round(2*ratio))
    usermanageWindow.grid_rowconfigure(23, weight=round(1*ratio))
    
    # Setup frames
    left_frame = Frame(usermanageWindow, width=round(cscreen_width*0.28), bg="#EDF1F7")
    left_frame.grid(row=0, column=0, rowspan=24, columnspan=3, sticky="nsew")
    right_frame = Frame(usermanageWindow, width=round(cscreen_width*0.58), bg="#293e50")
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
    usrmngtile_label.grid(column=1, row=0, columnspan=2, rowspan=2, sticky="nsw", pady=(round(30*ratio), round(5*ratio)), padx=(round(20*ratio), 0))
    # User detail fields
    uid_label = Label(usermanageWindow, text="User ID", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    uid_label.grid(row=2, column=0, columnspan=3, sticky="sw", padx=round(60*ratio))
    f0 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f0.grid(row=3, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    uid_text = Entry(f0, bd=round(3*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio))
    uid_text.pack(fill=BOTH, expand=True)
    uid_text.configure(state="disabled")
    CreateToolTip(uid_text, text = 'Add New User: Leave this field blank as system will auto generate the user ID\n'
                  'Update User: Select the user to be updated in the list, user ID field will be automatically filled\n'
                  'Delete User: Select the user to be deleted in the list before pressing on the button')
    ufname_label = Label(usermanageWindow, text="First Name", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    ufname_label.grid(row=4, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    f1 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f1.grid(row=5, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    ufname_val = StringVar()
    # ufname_val.trace('w', fnamevalidation)
    ufname_text = Entry(f1, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=ufname_val)
    ufname_text.pack(fill=BOTH, expand=True)
    CreateToolTip(ufname_text, text = 'Max length should only be 30 characters')
    ulname_label = Label(usermanageWindow, text="Last Name", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    ulname_label.grid(row=6, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    f2 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f2.grid(row=7, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    ulname_val = StringVar()
    # ulname_val.trace('w', lnamevalidation)
    ulname_text = Entry(f2, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=ulname_val)
    ulname_text.pack(fill=BOTH, expand=True)
    CreateToolTip(ulname_text, text = 'Max length should only be 30 characters')
    pas_label = Label(usermanageWindow, text="Password", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    pas_label.grid(row=8, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    fpas = Frame(usermanageWindow, bg="#EDF1F7")
    fpas.grid(row=9, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    resetpas_btn = Button(fpas, cursor="hand2", text="Reset Password", font=("Arial Rounded MT Bold", round(13*ratio)), width=round(20*ratio), relief=RIDGE, bd=1, bg="#6c757d", fg="white", activebackground="#4D5358", activeforeground="white")
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
    add_label = Label(usermanageWindow, text="Address Line", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    add_label.grid(row=10, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    f3 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f3.grid(row=11, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    add_val = StringVar()
    # add_val.trace('w', addvalidation)
    add_text = Entry(f3, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=add_val)
    add_text.pack(fill=BOTH, expand=True)
    CreateToolTip(add_text, text = 'Max length should only be 255 characters')
    city_label = Label(usermanageWindow, text="City", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    city_label.grid(row=12, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    f4 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f4.grid(row=13, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    city_val = StringVar()
    # city_val.trace('w', cityvalidation)
    city_text = Entry(f4, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=city_val)
    city_text.pack(fill=BOTH, expand=True)
    CreateToolTip(city_text, text = 'Max length should only be 30 characters')
    post_label = Label(usermanageWindow, text="Postal Code", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
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
    state_label = Label(usermanageWindow, text="State", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    state_label.grid(row=14, column=2, sticky="sw", padx=(round(15*ratio), round(60*ratio)), pady=(round(10*ratio), 0))
    f5 = Frame(usermanageWindow, relief=SUNKEN)
    f5.grid(row=15, column=2, padx=(round(10*ratio), round(60*ratio)), sticky="ne")
    state_text = ttk.Combobox(f5, font=("Lato", round(13*ratio)), background="white")
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
    state_text['state'] = 'readonly'
    email_label = Label(usermanageWindow, text="Email", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    email_label.grid(row=16, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    um_email_label_error = Label(usermanageWindow, text="Improper Email Format!", font=("Arial Rounded MT Bold", round(9*ratio)), bg="#EDF1F7", fg="red")
    f6 = Frame(usermanageWindow, borderwidth=round(2*ratio), relief=SUNKEN)
    f6.grid(row=17, column=0, columnspan=3, padx=round(60*ratio), sticky="new")
    email_val = StringVar()
    # my_valid = usermanageWindow.register(validate_email)
    email_text = Entry(f6, bd=round(4*ratio), relief=FLAT, font=("Lato", round(13*ratio)), width=round(38*ratio), textvariable=email_val)
    email_text.pack(fill=BOTH, expand=True)
    # email_text.config(validate="key", validatecommand=(my_valid, '%P'))
    CreateToolTip(email_text, text = 'e.g. dummy@xyz.com')
    phone_label = Label(usermanageWindow, text="Phone Number", font=("Arial Rounded MT Bold", round(13*ratio)), bg="#EDF1F7", fg="black")
    phone_label.grid(row=18, column=0, columnspan=3, sticky="sw", padx=round(60*ratio), pady=(round(10*ratio), 0))
    um_phone_label_error = Label(usermanageWindow, text="Improper Phone Number Format!", font=("Arial Rounded MT Bold", round(9*ratio)), bg="white", fg="red")
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
    add_userbtn = Button(f8, cursor="hand2", text="Add New User", font=("Arial Rounded MT Bold", round(13*ratio)), width=round(43*ratio), bg="#f2c40e", fg="white", relief=RIDGE, bd=1, activebackground="#C19C0C", activeforeground="white")
    add_userbtn.pack()
    f9 = Frame(usermanageWindow, bg="#EDF1F7")
    f9.grid(row=21, column=0, columnspan=3, sticky="nsew", padx=round(60*ratio), pady= round(5*ratio))
    upd_userbtn = Button(f9, cursor="hand2", text="Update User Info", font=("Arial Rounded MT Bold", round(13*ratio)), width=round(43*ratio), bg="#18bc9b", fg="white", relief=RIDGE, bd=1, activebackground="#17856F", activeforeground="white")
    upd_userbtn.pack()
    f10 = Frame(usermanageWindow, bg="#EDF1F7")
    f10.grid(row=22, column=0, columnspan=3, sticky="nsew", padx=round(60*ratio), pady=round(5*ratio))
    del_userbtn = Button(f10, cursor="hand2", text="Delete User", font=("Arial Rounded MT Bold", round(13*ratio)), width=round(43*ratio), bg="#dc3545", fg="white", relief=RIDGE, bd=1, activebackground="#A72A36", activeforeground="white")
    del_userbtn.pack()
    
    # Right components
    sys_label = Label(usermanageWindow, text="e-Vision", font=("Arial Rounded MT Bold", round(14*ratio)), bg="#293e50", fg="white")
    sys_label.grid(row=0, column=4, sticky="ne", padx=round(30*ratio), pady=round(15*ratio))
    # Search components
    f11 = Frame(usermanageWindow, bg="#293e50")
    f11.grid(row=1, column=3, columnspan=2, sticky="nsew", padx=round(60*ratio))
    f11a = Frame(f11, borderwidth=round(2*ratio), relief=SUNKEN)
    f11a.pack(side=LEFT)
    filterfield_text = Entry(f11a, bd=round(4*ratio), relief=FLAT, font=("Lato", round(10*ratio)), width=round(25*ratio), state='disabled')
    filterfield_text.pack(fill=BOTH, expand=True)
    f11b = Frame(f11)
    f11b.pack(side=LEFT,  padx=round(10*ratio))
    filter_opt = ttk.Combobox(f11b, font=("Lato", round(10*ratio)), background="white", width=round(15*ratio))
    filter_opt['values'] = ('All',
                          'User ID', 
                          'First Name',
                          'Last Name',
                          'Email',
                          'Phone Number')
    filter_opt.pack(fill=BOTH, expand=True)
    filter_opt.current(0)
    filter_opt['state'] = 'readonly'
    filter_opt.bind("<<ComboboxSelected>>", usrmngcallback)
    f11c = Frame(f11)
    f11c.pack(side=LEFT)
    search_userbtn = Button(f11c, cursor="hand2", text="Search", command=lambda:searchUserByFilter(filterfield_text.get(), filter_opt.get()), font=("Arial Rounded MT Bold", round(11*ratio)), width=round(12*ratio), bg="#E6E6E6", fg="black", relief=RIDGE, bd=1, activebackground="#B4B1B1", activeforeground="black")
    search_userbtn.pack()
    # Treeview frame
    usrmng_tree_frame = Frame(usermanageWindow)
    usrmng_tree_frame.grid(row=2, column=3, rowspan=20, columnspan=2, padx=round(60*ratio))
    # Treeview components
    usrmng_tree_vscroll = Scrollbar(usrmng_tree_frame)
    usrmng_tree_vscroll.pack(side=RIGHT, fill=Y)
    usrmng_tree_hscroll = Scrollbar(usrmng_tree_frame, orient='horizontal')
    usrmng_tree_hscroll.pack(side=BOTTOM, fill=X)
    column_headerlist = ['user_id', 'user_firstname', 'user_lastname', 'user_addressline', 'user_city', 'user_postcode', 'user_state', 'user_email', 'user_phone', 'user_lastlogin']
    usrmng_tree = ttk.Treeview(usrmng_tree_frame, columns=column_headerlist, show='headings', yscrollcommand=usrmng_tree_vscroll.set, xscrollcommand=usrmng_tree_hscroll.set, selectmode="browse", height=round(22*ratio))
    usrmng_tree.pack(side=TOP)
    style.map('Treeview', background=[('selected', '#04D8AE')])  #selected color
    # Configure scrollbar
    usrmng_tree_vscroll.config(command=usrmng_tree.yview)
    usrmng_tree_hscroll.config(command=usrmng_tree.xview)
    # Define haeder column name
    usrmng_tree.heading('user_id', text='User ID')
    usrmng_tree.heading('user_firstname', text='First Name')
    usrmng_tree.heading('user_lastname', text='Last Name')
    usrmng_tree.heading('user_addressline', text='Address Line')
    usrmng_tree.heading('user_city', text='City')
    usrmng_tree.heading('user_postcode', text='Postcode')
    usrmng_tree.heading('user_state', text='State')
    usrmng_tree.heading('user_email', text='Email')
    usrmng_tree.heading('user_phone', text='Phone Number')
    usrmng_tree.heading('user_lastlogin', text='Last Login Period')
    # Define column width and alignments
    usrmng_tree.column('user_id', width=round(60*ratio), minwidth=round(60*ratio), anchor ='c')
    usrmng_tree.column('user_firstname', width=round(100*ratio), minwidth=round(100*ratio), anchor ='c')
    usrmng_tree.column('user_lastname', width=round(100*ratio), minwidth=round(100*ratio), anchor ='c')
    usrmng_tree.column('user_addressline', width=round(150*ratio), minwidth=round(150*ratio), anchor ='c')
    usrmng_tree.column('user_city', width=round(100*ratio), minwidth=round(100*ratio), anchor ='c')
    usrmng_tree.column('user_postcode', width=round(70*ratio), minwidth=round(70*ratio), anchor ='c')
    usrmng_tree.column('user_state', width=round(100*ratio), minwidth=round(100*ratio), anchor ='c')
    usrmng_tree.column('user_email', width=round(100*ratio), minwidth=round(100*ratio), anchor ='c')
    usrmng_tree.column('user_phone', width=round(100*ratio), minwidth=round(100*ratio), anchor ='c')
    usrmng_tree.column('user_lastlogin', width=round(160*ratio), minwidth=round(160*ratio), anchor ='c')
    # Fetch all users (default)
    usrmng_tree.tag_configure('oddrow', background="white")
    usrmng_tree.tag_configure('evenrow', background="#ecf3fd")
    global usrmng_count
    usrmng_count = 0
    userresult = serachAllUser()
    if userresult is not None:
        for dt in userresult:
            if usrmng_count % 2 == 0:
                usrmng_tree.insert("", 'end', values=(dt[0], dt[1], dt[2], dt[4], dt[5], dt[7], dt[6], dt[8], dt[9], dt[12]), tags=('evenrow',))
            else:
                usrmng_tree.insert("", 'end', values=(dt[0], dt[1], dt[2], dt[4], dt[5], dt[7], dt[6], dt[8], dt[9], dt[12]), tags=('oddrow',))
            usrmng_count +=1
    # Clear selected btn
    f12 = Frame(usermanageWindow, bg="#293e50")
    f12.grid(row=22, column=3, columnspan=2, sticky="nsew", padx=round(60*ratio), pady=round(5*ratio))
    clr_selectedbtn = Button(f12, cursor="hand2", text="Clear Selected User", font=("Arial Rounded MT Bold", round(11*ratio)), width=round(25*ratio), bg="#E6E6E6", fg="black", relief=RIDGE, bd=1, activebackground="#B4B1B1", activeforeground="black")
    clr_selectedbtn.pack(side=LEFT)
    refresh_userbtn = Button(f12, cursor="hand2", text="Refresh User List", font=("Arial Rounded MT Bold", round(11*ratio)), width=round(25*ratio), bg="#E6E6E6", fg="black", relief=RIDGE, bd=1, activebackground="#B4B1B1", activeforeground="black")
    refresh_userbtn.pack(side=RIGHT)

root.mainloop()