import tkinter as tk
import customtkinter as ctk
from tkinter import font
from PIL import Image,ImageTk
from CTkColorPicker import *

class Whiteboard():

    def draw(self,event):
        x1 = self.canvas.canvasx(event.x)
        y1 = self.canvas.canvasy(event.y)

        #If last coords aren't saved we draw a point
        if self.last_x is None and self.last_y is None:
            self.line_id = self.canvas.create_line(x1,y1,x1+1,y1+1,self.line_properties,tags=self.line_tag)
            self.last_x=x1
            self.last_y=y1
            self.line_points.append((x1,y1))

        #If last coords are saved we delete last line and create new one containing previous points
        else:
            #Delete last line
            self.canvas.delete(self.line_id)
            #Append points from deleted line
            self.line_points.append((x1,y1))
            #Create new line including new points
            self.line_id=self.canvas.create_line(self.line_points,self.line_properties,tags=self.line_tag)


    def stop_drawing(self,event):

        flattened = [p for a in self.line_points for p in a]

        self.undo_stack.append({'coords':flattened,'line_properties':self.line_properties,'tag':self.line_tag,'type':'draw'})
        self.line_tag_counter+=1
        self.line_tag="tag"+str(self.line_tag_counter)

        #We set last_x and last_y to None so when we star drawing we will start by drawing a point
        # and if needed we will continue to draw continous line
        self.last_x=None
        self.last_y=None

        #Get rid of points in memory, we will collect new points when we start drawing new line
        self.line_points.clear()
        #If we perform action we reset redo_stack
        self.redo_stack.clear()

    def erase(self,event):
        if self.canvas.find_withtag('current'):
            #We get the tag of the item we just clicked
            clicked_object_tag = self.canvas.gettags('current')[0]

            #We collect information about the line we want to delete
            coords = self.canvas.coords(clicked_object_tag)
            width = self.canvas.itemcget(clicked_object_tag,'width')
            capstyle = self.canvas.itemcget(clicked_object_tag,'capstyle')
            line_properties = {'width':width,'capstyle':capstyle}

            #We collect data about deleted line in undo_stack
            self.undo_stack.append({'coords':coords,'line_properties':line_properties,'tag':clicked_object_tag,'type':'erase'})

            #We create that line
            self.canvas.delete(clicked_object_tag)

            #If we perform any action we want to reset redo_stack
            self.redo_stack.clear()








    def test(self):
        print(f'undo_stack: {self.undo_stack}')
        print(f'redo_stack: {self.redo_stack}')

    def change_mode(self,mode):
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<Button1-Motion>')
        self.canvas.unbind('<ButtonRelease>')
        if mode=="pen":
            self.canvas.bind('<Button-1>', self.draw)
            self.canvas.bind('<Button1-Motion>', self.draw)
            self.canvas.bind('<ButtonRelease>', self.stop_drawing)
            print('Changing mode to pen')
        elif mode=='eraser':
            print('changed mode to eraser')
            self.canvas.bind('<Button-1>', self.erase)


    def undo(self,*args):
        if self.undo_stack:

            last_action = self.undo_stack.pop()
            print(f'last_action={last_action}')
            last_type = last_action['type']
            if last_type=='draw':
                self.canvas.delete(last_action['tag'])
                self.redo_stack.append(last_action)
            elif last_type=='erase':
                coords = last_action['coords']
                line_properties = last_action['line_properties']
                tag = last_action['tag']
                self.canvas.create_line(coords,line_properties,tags=tag)
                self.redo_stack.append(last_action)

    def redo(self,*args):
        if self.redo_stack:
            last_action = self.redo_stack.pop()
            last_type = last_action['type']
            if last_type=='draw':
                coords = last_action['coords']
                line_properties = last_action['line_properties']
                line_tag=last_action['tag']
                self.canvas.create_line(coords,line_properties,tags=line_tag)

                self.undo_stack.append(last_action)
            elif last_type=='erase':
                self.canvas.delete(last_action['tag'])
                self.undo_stack.append(last_action)


    def change_brush_size(self,value):
        print(f'changing to {int(value)}')
        self.line_properties['width']=value
    def change_brush_color(self,value):
        self.line_properties['fill']=value



    def __init__(self):
        self.window = ctk.CTk()
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("blue")

        print(font.families())

        #It will be used to draw line from last registered point to the current one
        self.last_x= None
        self.last_y = None


        self.line_tag_counter = 1
        self.line_tag = 'tag'+str(self.line_tag_counter)


        #Undo and redo stacks used to manage ctrl+z and ctrl+y
        self.undo_stack = []
        self.redo_stack = []



        #Properties to draw line:
        self.line_properties = {'width':20,'capstyle':tk.ROUND,'fill':"black"}
        self.line_points = []

        #Create canvas and kit to choose tools
        self.canvas = ctk.CTkCanvas(self.window,scrollregion=(0,0,0,10000))
        self.tools_kit = ctk.CTkFrame(self.window)

        #Design Layout for tools_kit and canvas
        self.window.columnconfigure(0,weight=1)
        self.window.columnconfigure(1,weight=500)
        self.window.rowconfigure(0,weight=1)

        self.tools_kit.grid(row=0, column=0, sticky="nsew")
        self.canvas.grid(row=0,column=1,sticky="nsew")

        #Setting default mode as drawing (pen)
        self.change_mode("pen")



        self.canvas.bind_all("<w>",lambda event:self.canvas.yview_scroll(-1,"units"))
        self.canvas.bind_all("<s>", lambda event: self.canvas.yview_scroll(1, "units"))

        self.canvas.bind_all("<Control-z>", lambda event: self.undo(event))
        self.canvas.bind_all("<Control-y>", lambda event: self.redo(event))



        button_width = 25

        self.tools = ctk.CTkFrame(master=self.tools_kit)
        self.tools.pack(fill="x",padx=10,pady=50)

        button_image = ctk.CTkImage(Image.open("pen-clip.png"), size=(26, 26))
        pen_button = ctk.CTkButton(master=self.tools,image=button_image,text="",width=button_width,command=lambda:self.change_mode("pen"))

        button_image = ctk.CTkImage(Image.open("eraser.png"), size=(26, 26))
        erase_button = ctk.CTkButton(master=self.tools, image=button_image, text="", width=button_width,command=lambda:self.change_mode("eraser"))

        button_image = ctk.CTkImage(Image.open("text.png"), size=(26, 26))
        text_button = ctk.CTkButton(master=self.tools, image=button_image, text="", width=button_width)

        button_image = ctk.CTkImage(Image.open("undo-alt.png"), size=(26, 26))
        undo_button = ctk.CTkButton(master=self.tools, image=button_image, text="", width=button_width,command=lambda:self.undo())

        button_image = ctk.CTkImage(Image.open("redo-alt.png"), size=(26, 26))
        redo_button = ctk.CTkButton(master=self.tools, image=button_image, text="", width=button_width,command=lambda:self.redo())

        x=10
        y=5

        pen_button.grid(row=0,column=0,padx=x,pady=5)
        erase_button.grid(row=0,column=1,padx=x,pady=5)
        text_button.grid(row=0,column=2,padx=x,pady=5)
        undo_button.grid(row=0,column=3,padx=x,pady=5)
        redo_button.grid(row=0,column=4,padx=x,pady=5)

        brush_size_slider = ctk.CTkSlider(from_=5,to=40,master=self.tools,command=self.change_brush_size)
        brush_size_slider.grid(row=1,columnspan=5,sticky="nsew",pady=(25,15))

        brush_size_label = ctk.CTkLabel(master=self.tools,text='BRUSH SIZE',font=("Arial",20))
        brush_size_label.grid(row=2,column=0,columnspan=5)

        color_picker= CTkColorPicker(master=self.tools,command=lambda chosen_color: self.change_brush_color(chosen_color))
        color_picker.grid(row=3,column=0,columnspan=5,pady=25)





        self.window.mainloop()

my_whiteboard = Whiteboard()