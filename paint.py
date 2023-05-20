from tkinter import*
from tkinter.colorchooser import askcolor

window = Tk()

class Whiteboard:



    class Line:

        def __init__(self,canvas:Canvas,x1,y1,x2,y2,_width,_color,_tag,_capstyle=ROUND):
            self.line_id = canvas.create_line(x1,y1,x2,y2,width=_width,fill=_color,tags=_tag,capstyle=_capstyle)
            self.canvas = canvas

        def get_properties(self):
            x1,y1,x2,y2=self.canvas.coords(self.line_id)
            _width = self.canvas.itemcget(self.line_id,'width')
            _color = self.canvas.itemcget(self.line_id, 'fill')
            _tag = self.canvas.itemcget(self.line_id, 'tags')

            properties = {'x1':x1,'y1':y1,'x2':x2,'y2':y2,'width':_width,'fill':_color,'tag':_tag}
            return properties



    def create_new_tag(self):
        self.current_tag_counter+=1
        self.current_tag=f'item{self.current_tag_counter}'

    def increase_action_and_tag(self,event):
        self.current_action = self.current_action+1
        self.current_tag_counter+=1
        self.current_tag = f'item{self.current_tag_counter}'
        print('incresaing action ')

    def test(self):
        print(f'undo_stack: {self.undo_stack}')
        print(f'redo_stack: {self.redo_stack}')

    def activate_painting(self,event):
        #When we activate painting by pressing mousebutton we also start
        #to track where it goes and start painting continous lines
        self.canvas.bind("<B1-Motion>",self.paint)
        self.canvas.bind("<ButtonRelease-1>",self.increase_action_and_tag)
        x1,y1,x2,y2=self.canvas.canvasx(event.x) ,self.canvas.canvasy(event.y),self.canvas.canvasx(event.x+1),self.canvas.canvasy(event.y+1)
        #Draw line
        my_line = self.Line(self.canvas,x1,y1,x2,y2,self.brush_width,self.color,self.current_tag)

        self.last_x = x1
        self.last_y = y1


        self.redo_stack.clear()

        # Add information to undo_stack to track all actions
        self.undo_stack[self.current_action]= {'properties':[my_line.get_properties()],'operation':'pen'}

    def undo(self,event):
        try:
            last_action_id = list(self.undo_stack)[-1]
            operation_type = self.undo_stack[last_action_id]['operation']

            if operation_type=='pen':
                print(last_action_id)
                self.redo_stack[last_action_id]=self.undo_stack[last_action_id]
                last_line_id = self.undo_stack[last_action_id]['properties'][0]['tag']
                self.canvas.delete(last_line_id)
                del(self.undo_stack[last_action_id])
            elif operation_type=='eraser':

                last_operation = self.undo_stack[last_action_id]['properties']
                self.redo_stack[last_action_id]=self.undo_stack[last_action_id]
                for single_line in last_operation:
                    x1 = single_line['x1']
                    y1 = single_line['y1']
                    x2 = single_line['x2']
                    y2 = single_line['y2']
                    _width = single_line['width']
                    _fill = single_line['fill']
                    _tag = single_line['tags']

                    line = self.Line(self.canvas,x1,y1,x2,y2,_width,_fill,_tag)
                del (self.undo_stack[last_action_id])




        except Exception as e:
            print(e)

    def redo(self,event):
        last_action_id = list(self.redo_stack)[-1]
        operation_type = self.redo_stack[last_action_id]['operation']
        if operation_type=='pen':
            for single_line in self.redo_stack[last_action_id]['properties']:
                print('pls work: ',single_line)
                x1 = single_line['x1']
                y1 = single_line['y1']
                x2 = single_line['x2']
                y2 = single_line['y2']
                _width = single_line['width']
                _fill = single_line['fill']
                _tag = single_line['tag']
                self.canvas.create_line(x1,y1,x2,y2,width=_width,fill = _fill,tags=_tag,capstyle=ROUND)
                self.undo_stack[last_action_id]=self.redo_stack[last_action_id]

            del (self.redo_stack[last_action_id])
        elif operation_type=='eraser':
            last_line_tag = self.redo_stack[last_action_id]['properties'][0]['tags']
            self.canvas.delete(last_line_tag)
            self.undo_stack[last_action_id]=self.redo_stack[last_action_id]

            del(self.redo_stack[last_action_id])
    def paint(self,event):
        #To paint smoothly we use last registered x and y
        x1 = self.last_x
        y1 = self.last_y
        x2 = self.canvas.canvasx(event.x)
        y2 = self.canvas.canvasy( event.y)

        #We save current x and y postion as last
        self.last_x = x2
        self.last_y = y2

        #Draw line
        my_line = self.Line(self.canvas,x1,y1,x2,y2,self.brush_width,self.color,self.current_tag)
        #Add information to undo_stack to track all actions
        self.undo_stack[self.current_action]['properties'].append(my_line.get_properties())


    def erase(self,event):

        click_object_tag = self.canvas.gettags('current')[0]
        object_ids = self.canvas.find_withtag(click_object_tag)


        self.undo_stack[self.current_action]={'properties':[],'operation':'eraser'}


        for x in object_ids:

            x1,y1,x2,y2 = self.canvas.coords(x)
            _width = self.canvas.itemcget(x,'width')
            _fill = self.canvas.itemcget(x,'fill')
            _tag = self.canvas.itemcget(x,'tags')
            _tag =_tag.replace(' current','')
            properties  = {'x1':x1,'y1':y1,'x2':x2,'y2':y2,'width':_width,'fill':_fill,'tags':_tag}
            self.undo_stack[self.current_action]['properties'].append(properties)
            self.canvas.delete(x)




    def change_mode(self,mode_name):

        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<B1-Motion>')

        if mode_name=="pen":
            print("You changed mode to pen")
            self.canvas.bind("<Button-1>",self.activate_painting)


        elif mode_name=="eraser":
            self.canvas.bind("<Button-1>",self.erase)

        elif mode_name=='Pan':
            self.canvas.bind('<ButtonPress-1>', lambda event: self.canvas.scan_mark(event.x, event.y))
            self.canvas.bind("<B1-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))

    def change_color(self,button):
        value = askcolor()[1]
        print(value)
        self.color=value
        button.configure(bg=value)


    def __init__(self):
        #Initializing and placing basic tkinter canvas widgets
        window.rowconfigure(0,weight=1)
        window.columnconfigure(0, weight=1)
        self.action_pointer = 0

        #Default mode of whiteboard is to draw
        self.mode = "pen"
        self.brush_width=15
        self.color='#00f000'
        self.current_tag_counter=1
        self.current_tag='item1'
        self.current_action = 1




        screen = LabelFrame(window,background="green")
        screen.grid(row=0,column=0,sticky="nsew")
        screen.columnconfigure(index=0,weight=1)
        screen.columnconfigure(index=1, weight=5)
        screen.rowconfigure(index=0,weight=1)

        kit = LabelFrame(screen)
        kit.grid(row=0,column=0,sticky="nsew")
        kit.columnconfigure(index=0,weight=1)
        kit.columnconfigure(index=1,weight=50)

        pen_button = Button(kit,text="Pen",command=lambda:self.change_mode("pen"),height=2)
        color_button = Button(kit,height=4,background=self.color,command=lambda: self.change_color(color_button),borderwidth=0)
        erase_button = Button(kit, text="Erase",command=lambda:self.change_mode("eraser"))
        move_button = Button(kit, text="Move",command=lambda:self.change_mode('Pan'))
        redo_button = Button(kit, text="Redo")

        pen_button.grid(row=0,column=0,sticky="nsew")
        color_button.grid(row=1,columnspan=2,sticky='nsew')
        erase_button.grid(row=4, column=0)
        move_button.grid(row=5, column=0)
        redo_button.grid(row=5, column=1)

        test_button = Button(kit,text='test',command=self.test)
        test_button.grid(row=3,column=0,columnspan=2)

        self.canvas=Canvas(screen,background="white",scrollregion=(0,0,2000,5000))
        self.canvas.grid(row=0,column=1,sticky="nsew")
        self.canvas.bind_all('<Control-z>', self.undo)
        self.canvas.bind_all('<Control-y>', self.redo)
        self.canvas.focus_set()


        scrollbar = Scrollbar(window,orient='vertical',command=self.canvas.yview)
        scrollbar.place(relx=1,rely=0,relheight=1,anchor='ne')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.bind("<w>", lambda event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<s>", lambda event: self.canvas.yview_scroll(1, "units"))

        self.undo_stack = {}
        self.redo_stack = {}



my_whiteboard = Whiteboard()




window.mainloop()