import tkinter as tk

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
            self.canvas.bind('<Button-1>', self.erase)


    def undo(self):
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

    def redo(self):
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





    def __init__(self):
        self.window = tk.Tk()

        #It will be used to draw line from last registered point to the current one
        self.last_x= None
        self.last_y = None


        self.line_tag_counter = 1
        self.line_tag = 'tag'+str(self.line_tag_counter)


        #Undo and redo stacks used to manage ctrl+z and ctrl+y
        self.undo_stack = []
        self.redo_stack = []

        #Properties to draw line:
        self.line_properties = {'width':20,'capstyle':tk.ROUND}
        self.line_points = []

        #Create canvas and kit to choose tools
        self.canvas = tk.Canvas(self.window,background='gray',scrollregion=(0,0,2500,2500))
        self.tools_kit = tk.LabelFrame(self.window,background='white')

        #Design Layout for tools_kit and canvas
        self.window.columnconfigure(0,weight=1)
        self.window.columnconfigure(1,weight=5)
        self.window.rowconfigure(0,weight=1)
        self.tools_kit.grid(row=0, column=0, sticky="nsew")
        self.canvas.grid(row=0,column=1,sticky="nsew")

        #Setting default mode as drawing (pen)
        self.change_mode("pen")

        self.scrollbar = tk.Scrollbar(orient='vertical',command=self.canvas.yview)
        self.scrollbar.place(relx=1,rely=0,relheight=1,anchor='ne')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind_all("<w>",lambda event:self.canvas.yview_scroll(-1,"units"))
        self.canvas.bind_all("<s>", lambda event: self.canvas.yview_scroll(1, "units"))

        self.test_button = tk.Button(self.tools_kit,text='test',command=self.test)
        self.test_button.grid(row=0,column=0)

        self.pen_button = tk.Button(self.tools_kit,text='Pen',command=lambda:self.change_mode('pen'))
        self.eraser_button = tk.Button(self.tools_kit,text='Eraser',command=lambda:self.change_mode('eraser'))
        self.text_button = tk.Button(self.tools_kit,text='Text')
        self.undo_button = tk.Button(self.tools_kit,text='Undo',command=lambda:self.undo())
        self.redo_button = tk.Button(self.tools_kit, text='Redo',command = lambda:self.redo())

        self.pen_button.grid(row=1,column=0)
        self.eraser_button.grid(row=1,column=1)
        self.text_button.grid(row=1,column=2)
        self.undo_button.grid(row=1,column=3)
        self.redo_button.grid(row=1,column=4)



        self.window.mainloop()

my_whiteboard = Whiteboard()