#Kody Mitchell
#12/3/2020
#To Do List Final Project II - A GUI program that helps you keep track of your to-do list

#Import all the things
import pygame, sys, datetime, calendar, os

#A generic button class. From this class all clickables shall be derived.
class Button:
    #The initialization method. 
    def __init__(self, parent_object, surface, writer, label, background_color, label_color, x, y, action):
        #A parent object that contains the surface this object will be drawn onto.
        self.parent_object = parent_object

        #The surface that this object will draw onto.
        self.surface = surface

        #The font renderer that this button will use.
        self.writer = writer

        #The title of this button
        self.label = label

        #The background color of this button.
        self.background_color = background_color

        #The color that will show when the mouse is over the button.
        self.highlight_color = background_color + pygame.Color(25, 25, 25)

        #The color of the text.
        self.label_color = label_color

        #The action the button will call when it is clicked.
        self.action = action
        
        #The surface containing the label of the button
        self.label_surface = self.writer.render(label, True, label_color)

        #The rectangle object containing how large the button is and where it is
        self.rect = self.label_surface.get_rect().inflate(10,4)
        self.move_to(x, y)


    def draw(self):
        #Draw the rectangle with the background_color or the highlight_color
        pygame.draw.rect(self.surface, self.background_color if not self.mouse_over() else self.highlight_color, self.rect)
        #Draw the label surface onto the button surface.
        self.surface.blit(self.label_surface, self.rect.move(5,2))


    #Returns the absolute coordinates of this object. Needed for mouse comparisons.
    def get_abs_coords(self):
        #Get the absolute coordinates of the parent object, then add this object's relative coordinates.
        temp = self.parent_object.get_abs_coords()
        temp[0] += self.rect.x
        temp[1] += self.rect.y
        return temp


    #returns if the mouse is hovering over the button
    def mouse_over(self):
        coords = self.get_abs_coords()
        #Create a bounding box with the same size as the object at the absolute coordinates of the object. Then check if the mouse position is within those bounds.
        return pygame.Rect(coords[0], coords[1], self.rect.width, self.rect.height).collidepoint(pygame.mouse.get_pos())


    #Invoke the button's action
    def invoke_action(self):
        self.action()


    #Translate the button a given amount
    def move(self, x, y):
        self.rect = self.rect.move(x, y)


    #Move the button to an exact position
    def move_to(self, x, y):
        self.rect.x, self.rect.y = x, y


    #Child classes must override this if they want to change it.
    def is_focusable(self):
        return False


#The class for all checkboxes
class CheckBox(Button):
    def __init__(self, parent_object, writer, x, y, checked = False, check_mark = 'X', extra_action = None):
        #A parent object that contains the surface this object will be drawn onto.
        self.parent_object = parent_object

        #The font renderer.
        self.writer = writer

        #Tells whether or not the box is checked.
        self.checked = checked

        #The char to use for the checkmark.
        self.check_mark = check_mark

        #A new surface for the checkbox to be drawn onto.
        self.surface = pygame.Surface([15, 15])

        #The rectangle containing the coords and box of this object.
        self.rect = self.surface.get_rect().move(x, y)

        #This 'button's' action will be to toggle the checked flag.
        self.action = self.clicked

        #If the checkbox needs to do something in addition to that, extra_action will be called.
        self.extra_action = extra_action

        #The surface containing the checkmark char.
        self.check_surface = self.writer.render(self.check_mark, True, Color.WHITE)


    def draw(self):
        #Draw the checkbox background
        pygame.draw.rect(self.surface, Color.BLACK, self.surface.get_rect(), border_radius = 4)
        pygame.draw.rect(self.surface, Color.WHITE, self.surface.get_rect(), width = 1, border_radius = 4)

        #Draw the checkmark if necessary
        if self.checked:
            self.surface.blit(self.check_surface, [self.rect.width/2-self.check_surface.get_rect().width/2, self.rect.height/2-self.check_surface.get_rect().height/2])

        #Return this surface to be drawn onto the parent_object
        return self.surface


    #If the check box was clicked, call this method.
    def clicked(self):
        self.checked = not self.checked


    #Add extra action to action invokation.
    def invoke_action(self):
        super().invoke_action()
        if self.extra_action != None:
            self.extra_action()


#This class will asynchronously get input from the keyboard and save the data it receives.
class InputBox(Button):
    def __init__(self, parent_object, writer, placeholder, x, y, width = 300, data = ""):
        #A parent object that contains the surface this object will be drawn onto.
        self.parent_object = parent_object

        #The font renderer
        self.writer = writer

        #The placeholder string to display when there is no internal data.
        self.placeholder = placeholder

        #The internal data
        self.data = data

        #This is true when the data variable has been changed and the data_surface has not been updated.
        self.data_changed = True

        #The position of the cursor
        self.cursor_pos = len(data)

        #The InputBox will call the get focus method when clicked.
        self.action = self.get_focus

        #Internal way of seeing if this object has the focus.
        self.focused = False

        #Internal clock to flash the cursor at the appropriate intervals
        self.start_time = pygame.time.get_ticks()

        #The placeholder surface
        self.placeholder_surface = self.writer.render(placeholder, True, pygame.Color(75, 75, 75))

        self.rect = self.placeholder_surface.get_rect().inflate(10, 6)
        self.rect.width = width

        self.surface = pygame.Surface(self.rect.size)
        self.move_to(x, y)


    #Returns its surface after drawing.
    def draw(self):
        #Draw the InputBox background
        pygame.draw.rect(self.surface, pygame.Color(10, 10, 10), self.surface.get_rect())

        #Draw the text in the box
        #If data is empty, then draw the placeholder string to the input box and set the cursor_offsetx to zero.
        if self.data == "":
            self.surface.blit(self.placeholder_surface, self.surface.get_rect().inflate(-10, -6))
            self.cursor_offsetx = 0
        else:
            #If the data is not empty and it has changed then render a new data_surface and calculate a new cursor_offsetx.
            if self.data_changed:
                self.data_surface = self.writer.render(self.data, True, Color.WHITE)
                self.cursor_offsetx = self.writer.render(self.data[:self.cursor_pos], True, Color.WHITE).get_rect().width

                #Since we just updated the data_surface we can set the flag to false.
                self.data_changed = False
            #If data is longer than the width of the input box then start scrolling the beginning of the text off the left of the box.
            offset = 0
            if self.data_surface.get_width()>self.surface.get_width()-10:
                offset = self.surface.get_width()-10 - self.data_surface.get_width()

            #Draw the data onto the InputBox.
            self.surface.blit(self.data_surface, self.surface.get_rect().inflate(-10, -6).move(offset, 0))

        #Draw the cursor
        if self.focused:
            #Use pygame timing to draw the cursor for .5 a second every second.
            if (pygame.time.get_ticks() - self.start_time) % 1000 < 500:
                #calculate starting coordinates based on location of where data_surface is initially drawn.
                temp_rect = self.surface.get_rect().inflate(-10, -6)
                coords = [temp_rect.x, temp_rect.y]

                #Add the cursor_offsetx to the x coordinate
                coords[0] += self.cursor_offsetx

                #Draw a line at the appropriate location within the data_surface with the height of the data string that has been drawn.
                pygame.draw.line(self.surface, Color.WHITE, coords, [coords[0], coords[1]+temp_rect.height])

        #Draw the background outline
        pygame.draw.rect(self.surface, Color.GRAY, self.surface.get_rect(), width = 1)

        #Return this surface to be drawn onto the parent_object
        return self.surface


    #Override to True for all input boxes.
    def is_focusable(self):
        return True


    #Tells the program to have this object lose the focus
    def lose_focus(self):
        ToDoList.get_todo_list().focused = None
        self.focused = False


    #Tells the program to have this object take the focus
    def get_focus(self):
        todo_list = ToDoList.get_todo_list()
        #If an object is focused, tell it to lose the focus
        if todo_list.focused != None:
            todo_list.focused.lose_focus()
        
        #Set this object to be the focused object.
        todo_list.focused = self
        self.focused = True

        #Set cursor position to the end of the data string and calculate the x offset
        self.cursor_pos = len(self.data)        #IF TIME IS AVAILABLE: Add the ability to select text within the input box based on mouse clicks and position.
        self.cursor_offsetx = self.writer.render(self.data[:self.cursor_pos], True, Color.WHITE).get_rect().width
        #Reset the cursor clock.
        self.start_time = pygame.time.get_ticks()


    #Processes the event if a key was pressed and this object is focused.
    def process_event(self, event):
        #If a key we care about was pressed, then insert the appropriate code, otherwise put a "pass" so that an unknown char isn't added to the data.
        if event.key == pygame.K_BACKSPACE:
            #We don't want to go out of index here
            if self.cursor_pos == 0:
                return
            #Remove the character one index to the left of the cursor, flag the data_changed variable, move the cursor to the left one, and reset the clock.
            self.data = self.data[:self.cursor_pos-1] + self.data[self.cursor_pos:]
            self.data_changed = True
            self.cursor_pos -= 1
            self.start_time = pygame.time.get_ticks()
        elif event.key == pygame.K_DELETE:
            #We don't want to go out of index here
            if len(self.data) == self.cursor_pos:
                return
            #Remove the character at the current index, flag the data_changed variable, and reset the clock.
            self.data = self.data[:self.cursor_pos] + self.data[self.cursor_pos+1:]
            self.data_changed = True
            self.start_time = pygame.time.get_ticks()
        elif event.key == pygame.K_RETURN:
            #If return is pressed, then tell the To do list to put the next focusable object in focus.
            ToDoList.get_todo_list().next_focusable(True)
        elif event.key == pygame.K_ESCAPE:
            pass
        elif event.key == pygame.K_PAUSE:
            pass
        elif event.key == pygame.K_TAB:
            #Use the bitwise AND to determine if a shift key is being pressed from the bitwise mask 'mod'. If so, then pass False to the method to find the previous focusable.
            #Otherwise it will find the next focusable.
            ToDoList.get_todo_list().next_focusable(not event.mod & pygame.KMOD_SHIFT)
        elif event.key == pygame.K_UP:
            pass
        elif event.key == pygame.K_DOWN:
            pass
        elif event.key == pygame.K_LEFT:
            if self.cursor_pos == 0:
                return
            #Simply move the cursor to the left by one, reset the clock, and recalculate the cursor_offsetx
            self.cursor_pos -= 1
            self.start_time = pygame.time.get_ticks()
            self.cursor_offsetx = self.writer.render(self.data[:self.cursor_pos], True, Color.WHITE).get_rect().width
        elif event.key == pygame.K_RIGHT:
            if len(self.data) == self.cursor_pos:
                return
            #Simply move the cursor to the right by one, reset the clock, and recalculate the cursor_offsetx
            self.cursor_pos += 1
            self.start_time = pygame.time.get_ticks()
            self.cursor_offsetx = self.writer.render(self.data[:self.cursor_pos], True, Color.WHITE).get_rect().width
        elif event.key == pygame.K_INSERT:
            pass
        elif event.key == pygame.K_HOME:
            pass
        elif event.key == pygame.K_END:
            pass
        elif event.key == pygame.K_PAGEUP:
            pass
        elif event.key == pygame.K_PAGEDOWN:
            pass
        elif event.key == pygame.K_F1 or event.key == pygame.K_F2 or event.key == pygame.K_F3 or event.key == pygame.K_F4 or event.key == pygame.K_F5 or event.key == pygame.K_F6 or event.key == pygame.K_F7 or event.key == pygame.K_F8 or event.key == pygame.K_F9 or event.key == pygame.K_F10 or event.key == pygame.K_F11 or event.key == pygame.K_F12 or event.key == pygame.K_F13 or event.key == pygame.K_F14 or event.key == pygame.K_F15:
            pass
        elif event.key == pygame.K_NUMLOCK or event.key == pygame.K_CAPSLOCK or event.key == pygame.K_SCROLLOCK or event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT or event.key == pygame.K_RCTRL or event.key == pygame.K_LCTRL or event.key == pygame.K_RALT or event.key == pygame.K_LALT or event.key == pygame.K_RMETA or event.key == pygame.K_LMETA or event.key == pygame.K_LSUPER or event.key == pygame.K_RSUPER or event.key == pygame.K_MODE or event.key == pygame.K_HELP or event.key == pygame.K_PRINT or event.key == pygame.K_SYSREQ or event.key == pygame.K_BREAK or event.key == pygame.K_CLEAR or event.key == pygame.K_MENU or event.key == pygame.K_POWER or event.key == pygame.K_EURO:
            pass
        else:
            #If no other key was pressed, then what remains must be a normal character that can be printed onto the screen. 
            #Add it to the data, flag the data_changed variable, add one to the cursor position, and reset the clock.
            self.data = self.data[:self.cursor_pos] + event.unicode + self.data[self.cursor_pos:]
            self.data_changed = True
            self.cursor_pos += 1
            self.start_time = pygame.time.get_ticks()


#The class for the slider input bars
class Slider(Button):
    def __init__(self, parent_object, surface, writer, label, x, y, max, min = 0, value = -1, width = 100):
        self.parent_object = parent_object
        self.surface = surface
        self.writer = writer
        self.label = label
        self.label_surface = self.writer.render(label, True, Color.WHITE)
        #The max and minimum values allowed in this slider.
        self.max, self.min = max, min
        #The default value is the mean of the max and min unless otherwise specified.
        if value == -1:
            self.value = int((max + min)/2)
        else:
            self.value = value
        #When clicked, the slider checks what value it should be set to based on the mouse position.
        self.action = self.get_selection
        #The mouse is not currently being pressed. This is set to true when a MOUSEBUTTONDOWN event is received while hovering over this object. And it is set to false when MOUSEBUTTONUP is received.
        self.mouse_down = False
        
        #The colors of the slider.
        self.background_color = Color.LIGHT_BLUE
        self.slider_color = Color.LIGHT_BLUE + pygame.Color(50, 50, 250)

        #The surfaces of the slider.
        self.max_label, self.min_label = self.writer.render(str(max), True, Color.WHITE), self.writer.render(str(min), True, Color.WHITE)

        #The rects of the slider.
        self.rect = pygame.rect.Rect(x, y, width, self.max_label.get_rect().height)
        self.indicator_rect = pygame.rect.Rect(x, y, width / (self.max - self.min + 1), self.max_label.get_rect().height)

        #This initialization is only needed if the starting value is equal to the minimum value. I put it here to make me feel better.
        self.value_surface = self.writer.render(str(self.value), True, Color.WHITE)


    #Call this if you need to set the value of this slider.
    def set_value(self, value):
        self.value = value
        self.value_surface = self.writer.render(str(self.value), True, Color.WHITE)


    def draw(self):
        #Draw the background of the slider.
        pygame.draw.rect(self.surface, self.background_color, self.rect)

        #Draw the max, min, and title labels at the appropriate spots.
        self.surface.blit(self.min_label, self.rect.move(-self.min_label.get_rect().width-5, 0))
        self.surface.blit(self.max_label, self.rect.move(self.rect.width+5, 0))
        self.surface.blit(self.label_surface, self.rect.move(self.rect.width/2-self.label_surface.get_rect().width/2, -self.label_surface.get_rect().height-2))

        #If the mouse button is being held down on the slider, then continually check where the mouse is.
        if self.mouse_down:
            self.get_selection()

        #Calculate from value where to draw the value label and the indicator_rect
        new_position = self.rect.x + self.indicator_rect.width * (self.value - self.min)

        #To prevent some weird positioning with odd numbers, set the new_position to the far right if it is for the maximum value.
        if self.value == self.max:
            new_position = self.rect.x + self.rect.width - self.indicator_rect.width

        #if the current position does not match the new position, then overwrite it and re-render the value_surface
        if self.indicator_rect.x != new_position:
            self.indicator_rect.x = new_position
            self.value_surface = self.writer.render(str(self.value), True, Color.WHITE)

        #Draw the indicator rectangle onto the slider.
        pygame.draw.rect(self.surface, self.slider_color, self.indicator_rect)

        #Draw value label
        self.surface.blit(self.value_surface, self.indicator_rect.move(self.indicator_rect.width/2-self.value_surface.get_rect().width/2, 20))


    #When the slider is clicked on, this method calculates the new value the slider should be given based on the mouse position.
    def get_selection(self):
        #Since this has been clicked on, flip this flag.
        self.mouse_down = True
        #calculate the position of the mouse relative to the slider.
        pos = pygame.mouse.get_pos()[0] - self.rect.x - self.parent_object.get_abs_coords()[0]

        #Refine this position to a number between the minimum and the maximum values.
        pos = int(pos / ((self.rect.width - self.indicator_rect.width) / (self.max - self.min)))
        #set the value to this number.
        self.value = pos + self.min
        #To prevent the setting of out-of-bounds numbers, these if statements will cap the slider at its max and min.
        if self.value > self.max:
            self.value = self.max
        elif self.value < self.min:
            self.value = self.min


    #Call this when a mouseup event is fired.
    def mouse_up(self):
        self.mouse_down = False


#The slider bar class. For sliding things and not getting a value.
#class SliderBar(Slider):


#The main class for this program.
class ToDoList:
    #A static reference to the only object that this class will produce. Do not try to reference this before the object has been initialized.
    todo_list = None

    #A static method to return the todo list object. This way each object does not need to save a reference to this object, this method can simply be called when needed.
    @staticmethod
    def get_todo_list():
        return ToDoList.todo_list

    #A static method to return the current_datetime object. This object is always being renewed to the current time.
    @staticmethod
    def get_current_datetime():
        return ToDoList.todo_list.current_datetime


    def __init__(self, screen, writer):
        #Set the static variable to this object. This method will only be called once.
        ToDoList.todo_list = self

        #The main screen surface.
        self.screen = screen
        #A font renderer with big letters
        self.title_writer = writer
        #A font renderer with little letters.
        self.text_writer = pygame.font.SysFont("arial", 16)
        #Tells whether or not the program is in task creation mode.
        self.creating_task = False
        #Holds the object that is currently focused.
        self.focused = None
        #Holds the Task that is currently being edited.
        self.editing = None
        #Holds the current datetime.
        self.current_datetime = datetime.datetime.now()
        #Holds all post_draw calls.
        self.post_draws = []

        #Holds the checkbox and its description.
        self.checkbox = CheckBox(self, self.text_writer, 5, 5, checked = True, extra_action = self.reorder_clickables)
        self.checkbox_desc = self.text_writer.render("Show all tasks", True, Color.WHITE)

        #Surface indicating which task showing mode we are in.
        self.tasks_showing_surfaces = [self.text_writer.render("Showing tasks within 7 days of today", True, Color.WHITE), self.text_writer.render("Showing all tasks", True, Color.WHITE)]

        #Holds all tasks
        self.tasks = []
        #Holds all clickables in this object. (Besides the above checkbox.)
        self.clickables = []

        #If the tasks file exists, then read all the tasks that are in it and initialize the program with them.
        if os.path.exists("tasks.dat"):
            loadfile = open("tasks.dat", "r")
            #Load what task showing mode we are in.
            self.checkbox.checked = bool(int(loadfile.readline()[:-1]))
            #Load the number of tasks to load.
            task_number = int(loadfile.readline()[:-1])
            for i in range(0, task_number):
                #Load the tasks themselves. Each "[:-1]" simply strips the trailing newline character.
                self.tasks.append(Task(self.screen, self.text_writer, loadfile.readline()[:-1], self.date_and_time_to_datetime(loadfile.readline()[:-1], loadfile.readline()[:-1]), int(loadfile.readline()[:-1]), 0, 0))
                self.tasks[-1].checkbox.checked = bool(int(loadfile.readline()[:-1]))
            loadfile.close()

        #Get which tasks should actually be shown.
        temp = self.generate_showing_tasks()
        #Add them to the clickables list.
        self.clickables.extend(temp)
        #Add the add task button to the clickables list.
        self.clickables.append(Button(self, self.screen, self.title_writer, '+', Color.LIGHT_BLUE, Color.WHITE, 10, self.clickables[-1].rect.y+35, self.new_task))


    #This method gets all tasks that are overdue or within 7 days of the current timestamp and puts them in a list to display should the user request it.
    def generate_showing_tasks(self):
        #Holds all tasks that have datetimes within 7 days of the current timestamp.
        self.showing_tasks = []
        #Add the appropriate tasks to this list.
        for task in self.tasks:
            if task.duedatetime < self.current_datetime and not task.checkbox.checked:
                self.showing_tasks.append(task)
            elif task.duedatetime >= self.current_datetime - datetime.timedelta(weeks = 1) and task.duedatetime <= self.current_datetime + datetime.timedelta(weeks = 1):
                self.showing_tasks.append(task)

        #Determine which tasks should be showing if 7 day filter is active.
        temp_task_list = None
        if self.checkbox.checked:
            temp_task_list = self.tasks
        else:
            temp_task_list = self.showing_tasks

        #Move the visible tasks to the appropriate position on the screen.
        y = 25
        for task in temp_task_list:
            task.move_to(0, y)
            y += 25

        #If the add button has been added already, then position the button as well. Otherwise ignore this.
        if len(self.clickables) > 0:
            self.clickables[-1].move_to(0, y+10)

        #Resest the clickables to be empty.
        self.clickables = []

        #Return the visible task list.
        return temp_task_list


    #PRIVATE METHOD!! DO NOT CALL!
    #This takes a date string with format MM/DD/YYYY and time string with format HH:MM and combines them into one datetime object.
    def date_and_time_to_datetime(self, date_string, time_string):
        return datetime.datetime(int(date_string[6:]), int(date_string[:2]), int(date_string[3:5]), int(time_string[:time_string.find(":")])%24, int(time_string[time_string.find(":")+1:]))


    def draw(self):
        #Update program clock before any draw calls.
        self.current_datetime = datetime.datetime.now()

        #Draw the checkbox and its description.
        self.screen.blit(self.checkbox.draw(), self.checkbox.rect)
        self.screen.blit(self.checkbox_desc, [25, 2])
        #Draw the appropriate task showing mode title.
        temp_rect = self.tasks_showing_surfaces[self.checkbox.checked].get_rect()
        self.screen.blit(self.tasks_showing_surfaces[self.checkbox.checked], temp_rect.move(300-temp_rect.width/2, 2))

        #Draw all the clickables
        for c in self.clickables:
            surface = c.draw()
            if surface != None:
                self.screen.blit(surface, c.rect)

        #Draw everything in the post draw buffer. These have to be drawn over top of everything else on this surface. First come, first draw.
        while len(self.post_draws) > 0:
            self.post_draws.pop(0)()

        #Must draw task window last so it appears on top of everything in the surface below it.
        if self.creating_task:
            self.task_window.draw()


    #Returns the absolute coordinates of this object. Needed for mouse comparisons.
    def get_abs_coords(self):
        return [0, 0]


    #Add a post draw call to the buffer.
    def add_post_draw(self, callable):
        self.post_draws.append(callable)


    #Create the new task window
    def new_task(self):
        if self.creating_task:
            return
        self.creating_task = True
        self.task_window = TaskWindow(self.screen, self.title_writer)


    #Add the task from the task window to a new task object.
    def add_task(self):
        i = 0
        title = None
        duedatetime = None
        priority = 0
        #Take the data in the task window and save them. Then create a task with these pieces of data.
        for c in self.task_window.clickables:
            if isinstance(c, InputBox):
                if i==0:
                    title = c.data
                elif i==1:
                    duedatetime = datetime.datetime(int(c.data[6:]), int(c.data[:2]), int(c.data[3:5]))
                elif i==2:
                    hour = int(c.data[:c.data.find(":")])%24
                    minute = int(c.data[c.data.find(":")+1:])
                    duedatetime = datetime.datetime(duedatetime.year, duedatetime.month, duedatetime.day, hour, minute)
                i += 1
            elif isinstance(c, Slider):
                priority = c.value

        #Insert new task at the top of the task list. We will sort all the tasks based on due date and time later.
        self.tasks.insert(0, Task(self.screen, self.text_writer, title, duedatetime, priority, 0, 0))
        
        #If we are editing a task, destroy the old task.
        if self.editing != None:
            self.tasks.pop(self.tasks.index(self.editing))

        #Sort everything except the button at the end.
        self.tasks = sorted(self.tasks, key = Task.get_duedatetime)

        #Reorder the clickables list.
        self.reorder_clickables()


    #Properly reorders the clickables list
    def reorder_clickables(self):
        #Save the add button so it doesn't get deleted in the reorder process.
        button_temp = self.clickables[-1]

        #Reorder clickables
        temp = self.generate_showing_tasks()
        self.clickables.extend(temp)

        #Re-add the add button.
        self.clickables.append(button_temp)


    #Checks if a mouse click was on a clickable in this object.
    def mouse_click(self):
        #Check if the checkbox was clicked.
        if self.checkbox.mouse_over():
            self.checkbox.invoke_action()
        #Check the clickables if they have been clicked.
        for clickable in self.clickables:
            if isinstance(clickable, Task):
                clickable.mouse_click()
            else:
                if clickable.mouse_over():
                    clickable.invoke_action()


    #Focuses the next object that can be focused. If 'next' is false, then it focuses the previous object that can be focused.
    def next_focusable(self, next):
        #If shift + tab is pressed, then we want to go backwards, not forwards.
        crement = 1 if next else -1

        #Gets a list of clickables from either the task window or the main screen depending on which is active.
        clickables = None
        if self.creating_task:
            clickables = self.task_window.clickables
        else:
            clickables = self.clickables

        #Also gets the index of the focused object.
        index = clickables.index(self.focused)

        #Loop till we find the next/previous focusable object.
        while True:
            index += crement
            #If the index matches the length of the clickables list, then return the index to zero.
            index %= len(clickables)
            if clickables[index].is_focusable():
                #Internal logic handles unfocusing previously focused object.
                clickables[index].get_focus()
                return


    #Save all the tasks that are in program memory
    def save(self):
        savefile = open("tasks.dat", "w")
        savefile.write(str(int(self.checkbox.checked))+'\n')
        savefile.write(str(len(self.clickables)-1)+'\n')
        for task in self.clickables[:-1]:
            #Save title
            savefile.write(task.title+'\n')

            #Save due date
            savefile.write(task.get_full_date_string()+ '\n')

            #Save due time
            savefile.write(task.duetime_string+'\n')

            #Save priority
            savefile.write(str(task.priority)+'\n')

            #Save checked state
            savefile.write(str(int(task.checkbox.checked))+'\n')
        savefile.close()


class TaskWindow:
    def __init__(self, screen, writer):
        self.screen = screen
        self.title_writer = writer
        self.text_writer = pygame.font.SysFont("arial", 16)
        self.surface = pygame.Surface([500, 360])
        #The coordinates of this object.
        self.coords = [50, 50]
        #Holds the surfaces of any errors that generate later.
        self.error_surfaces = []

        #A list holding all the clickable objects.
        self.clickables = []

        self.clickables.append(Button(self, self.surface, self.title_writer, "X", Color.RED, Color.WHITE, 450, 20, self.close))
        self.clickables.append(Button(self, self.surface, self.title_writer, "Done", Color.GREEN, Color.WHITE, 425, 320, self.done))

        self.clickables.append(InputBox(self, self.text_writer, "Title", 20, 20))
        self.clickables.append(InputBox(self, self.text_writer, "Due date (MM/DD/YYYY)", 20, 52))
        self.clickables.append(InputBox(self, self.text_writer, "Time due (1:00-24:59)", 20, 84))

        self.clickables.append(Slider(self, self.surface, self.text_writer, "Priority", 20, 150, 5))


    def draw(self):
        #Dimming effect on the background
        dark_glass = pygame.Surface(self.screen.get_size())
        dark_glass.fill(Color.BLACK)
        dark_glass.set_alpha(175)
        self.screen.blit(dark_glass, [0,0])

        #Draw task creation window background
        pygame.draw.rect(self.surface, pygame.Color(25, 25, 25), self.surface.get_rect())
        pygame.draw.rect(self.surface, Color.GRAY, self.surface.get_rect(), width = 1)

        #Draw all the clickables
        for c in self.clickables:
            surface = c.draw()
            #If a blit is needed after drawing, then the draw method will return a surface to be blitted, otherwise it will return None.
            if surface != None:
                self.surface.blit(surface, c.rect)

        #Display the errors at the bottom of the task window if necessary.
        y = 330
        for e in self.error_surfaces:
            self.surface.blit(e, [20, y])
            y -= e.get_rect().height + 5

        self.screen.blit(self.surface, self.coords)


    #Returns the absolute coordinates of this object. Needed for mouse comparisons.
    def get_abs_coords(self):
        return self.coords.copy()


    #Check if a mouse click was on an something in this object.
    def mouse_click(self):
        for clickable in self.clickables:
            if clickable.mouse_over():
                clickable.invoke_action()


    #Call when a mouse up event is fired.
    def mouse_up(self):
        for c in self.clickables:
            if isinstance(c, Slider):
                c.mouse_up()


    #Call this if the X button has been pressed. Close the task window.
    def close(self):
        todo = ToDoList.get_todo_list()
        if todo.focused != None:
            todo.focused.lose_focus()
        todo.creating_task = False
        todo.task_window = None
        todo.editing = None


    #Call this if the Done button is pressed. 
    #Check if the task is valid, then if so, save it and close the task window.
    #If not, then tell the user what is wrong.
    def done(self):
        errors = []
        i = 0
        for c in self.clickables:
            if isinstance(c, InputBox):
                #Error handling
                #If the title is blank, we have problems
                if i==0:
                    #Do not allow an empty title.
                    if c.data == "":
                        errors.append("Task must have a title")
                #If the date string doesn't match the format, then we have problems.
                elif i==1:
                    #If the date is not the right length, add an error.
                    if len(c.data) != 10:
                        errors.append("Due date does not match given format: MM/DD/YYYY")
                        i += 1
                        continue
                    fail = False
                    for x in range(0, 10):
                        #If slashes are not in the right place, add an error.
                        if x == 2 or x == 5:
                            if c.data[x] != '/':
                                errors.append("Due date does not match given format: MM/DD/YYYY")
                                fail = True
                                break
                        #If the rest of the chars are not numbers, add an error.
                        elif c.data[x] < '0' or c.data[x] > '9':
                            errors.append("Due date does not match given format: MM/DD/YYYY")
                            fail = True
                            break
                    if fail:
                        i += 1
                        continue
                    m = int(c.data[:2])
                    #If the month is outside the range of 1-12, add an error.
                    if m<1 or m>12:
                        errors.append("Month must be within range 1-12")
                        i += 1
                        continue
                    d = int(c.data[3:5])
                    year = int(c.data[6:])
                    #If the given day is below 1 or above the number of days in the given month of the given year, then add an error.
                    if d > get_days_in_month(m, year) or d < 1:
                        errors.append(f"{d} is not a valid day for {calendar.month_name[m]} in {year}")
                        i += 1
                        continue
                #If the time string doesn't match the format, then we have problems.
                elif i==2:
                    #If the time string is not an acceptable length or a ':' cannot be found, add an error.
                    if len(c.data) > 5 or len(c.data) < 4 or c.data.find(":") == -1:
                        errors.append("Invalid time format")
                        i += 1
                        continue
                    colon_seen = False
                    fail = False
                    for char in c.data:
                        if char == ':':
                            #If multiple colons are seen, then add an error.
                            if colon_seen:
                                errors.append("Too many colons")
                                fail = True
                                break
                            colon_seen = True
                        #If any chars are not numbers or colons, add an error.
                        if char < '0' or char > '9' and not char == ':':
                            errors.append("Invalid time format")
                            fail = True
                            break
                    if fail:
                        i += 1
                        continue
                    #See if given numbers actually make sense
                    #Get the hour from the time string and convert it to an int.
                    h = int(c.data[:c.data.find(":")])
                    #If the hour is not between 1-24, add an error.
                    if h < 1 or h > 24:
                        errors.append("Hours must be in military time between 1-24")
                    #Get the minute from the time string and convert it to an int.
                    minute = int(c.data[c.data.find(":")+1:])
                    #If the minute is not between 0-59, add an error.
                    if minute < 0 or minute > 59:
                        errors.append("Minutes must be between 0-59")
                #Increment i for the next input box
                i += 1

        #If there are errors, render surfaces for them and exit this method. The task is not acceptable.
        if len(errors) > 0:
            self.error_surfaces = []
            for e in errors:
                self.error_surfaces.append(self.text_writer.render(e, True, Color.RED))
            return

        #If the program has made it past here, congrats! You have a valid task! Let's save it and close this window.
        ToDoList.get_todo_list().add_task()

        self.close()


class Task(Button):
    def __init__(self, screen, writer, title, duedatetime, priority, x, y):
        self.screen = screen
        self.writer = writer
        self.title = title
        #The due date and time of the task.
        self.duedatetime = duedatetime
        #When clicked, this task will pull up its editing window.
        self.action = self.edit
        self.priority = priority
        self.surface = pygame.Surface([600, 25])
        self.rect = self.surface.get_rect().move(x, y)

        self.checkbox = CheckBox(self, self.writer, 2, 2)

        #Render the title of the task in the appropriate color for the priority it was given.
        self.title_color = Color.get_color_gradient(Color.YELLOW, Color.RED, 4, priority-1) if priority > 0 else Color.GREEN
        self.title_surface = self.writer.render(self.title, True, self.title_color)
        self.title_done_surface = self.writer.render(self.title, True, Color.GRAY)
        self.title_overdue_surface = self.writer.render(self.title, True, Color.BRIGHT_RED)

        #Render the due date and time.
        self.duedate_string = calendar.month_name[duedatetime.month][:3] + " " + str(duedatetime.day) + ("" if duedatetime.year == ToDoList.get_todo_list().current_datetime.year else (", " + str(duedatetime.year)))
        self.duedate_surface = self.writer.render(self.duedate_string, True, Color.WHITE)
        self.duedate_done_surface = self.writer.render(self.duedate_string, True, Color.GRAY)
        self.duedate_overdue_surface = self.writer.render(self.duedate_string, True, Color.BRIGHT_RED)

        self.duetime_string = str(24 if self.duedatetime.hour==0 else self.duedatetime.hour) + f":{self.duedatetime.minute:02d}"
        self.duetime_surface = self.writer.render(self.duetime_string, True, Color.WHITE)
        self.duetime_done_surface = self.writer.render(self.duetime_string, True, Color.GRAY)
        self.duetime_overdue_surface = self.writer.render(self.duetime_string, True, Color.BRIGHT_RED)

        self.delete_button = Button(ToDoList.get_todo_list(), self.screen, self.writer, "Delete", Color.RED, Color.WHITE, 550, y+3, self.delete)


    def draw(self):
        #If the mouse is not over the delete button, but it is over the task, then draw the highlighted color instead of black. Or just draw black.
        if not self.delete_button.mouse_over():
            if self.mouse_over():
                self.surface.fill(pygame.Color(25, 25, 25))
            else:
                self.surface.fill(Color.BLACK)
        else:
            self.surface.fill(Color.BLACK)
        
        self.surface.blit(self.checkbox.draw(), self.surface.get_rect().move(5, 5))

        #If the task is complete, render the completed task surfaces and draw a line through it.
        if self.checkbox.checked:
            self.surface.blit(self.title_done_surface, self.surface.get_rect().move(25, 5))
            self.surface.blit(self.duedate_done_surface, self.surface.get_rect().move(170, 5))
            self.surface.blit(self.duetime_done_surface, self.surface.get_rect().move(370, 5))
            pygame.draw.line(self.surface, Color.GRAY, [26, 13], [500, 13])
        else:
            #If the task is overdue, draw the overdue surfaces.
            if ToDoList.get_current_datetime() >= self.duedatetime:
                self.surface.blit(self.title_overdue_surface, self.surface.get_rect().move(25, 5))
                self.surface.blit(self.duedate_overdue_surface, self.surface.get_rect().move(170, 5))
                self.surface.blit(self.duetime_overdue_surface, self.surface.get_rect().move(370, 5))
            #Otherwise draw the normal surfaces.
            else:
                self.surface.blit(self.title_surface, self.surface.get_rect().move(25, 5))
                self.surface.blit(self.duedate_surface, self.surface.get_rect().move(170, 5))
                self.surface.blit(self.duetime_surface, self.surface.get_rect().move(370, 5))

        #Add the delete button to the post draw list. 
        ToDoList.get_todo_list().add_post_draw(self.delete_button.draw)

        #Return this surface to be drawn onto.
        return self.surface


    #Returns the due date as a formatted string.
    def get_full_date_string(self):
        return f"{self.duedatetime.month:02d}/{self.duedatetime.day:02d}/{self.duedatetime.year:04d}"


    #Returns the absolute coordinates of this object. Needed for mouse comparisons.
    def get_abs_coords(self):
        return [self.rect.x, self.rect.y]


    #Call this method to see if something in this object was clicked.
    def mouse_click(self):
        if self.checkbox.mouse_over():
            self.checkbox.invoke_action()
        elif self.delete_button.mouse_over():
            self.delete_button.invoke_action()
        elif self.mouse_over():
            self.invoke_action()


    #Call this method to see if the mouse is hovering over something in this object other than the delete button.
    def mouse_over(self):
        if self.checkbox.mouse_over():
            return True
        elif self.delete_button.mouse_over():
            return False
        return super().mouse_over()


    #Return the due datetime object for comparison to sort the tasks.
    def get_duedatetime(self):
        return self.duedatetime


    #Delete this task from memory
    def delete(self):
        todo = ToDoList.get_todo_list()
        #Move the add button up 25
        todo.clickables[-1].move(0, -25)
        temp = todo.clickables[-1]

        #Delete this task from all lists it is in.
        todo.clickables.pop(todo.clickables.index(self))
        todo.tasks.pop(todo.tasks.index(self))
        if not todo.checkbox.checked:
            todo.showing_tasks.pop(todo.showing_tasks.index(self))
        
        #Resorting is not necessary for removing objects, but they still must be moved to the correct position.
        todo.clickables = todo.clickables[:-1]
        y = 25
        for task in todo.clickables:
            task.move_to(0, y)
            y += 25

        todo.clickables.append(temp)
        

    #Override move_to to add code for additional buttons
    def move_to(self, x, y):
        self.delete_button.move(0, y+3 - self.delete_button.rect.y)
        super().move_to(x, y)


    #Edit the task
    def edit(self):
        todo = ToDoList.get_todo_list()
        todo.new_task()
        todo.editing = self
        i = 0
        #Take this task's data and input it into the task window.
        for c in todo.task_window.clickables:
            if isinstance(c, InputBox):
                if i==0:
                    c.data = self.title
                elif i==1:
                    c.data = self.get_full_date_string()
                elif i==2:
                    c.data = self.duetime_string
                i += 1
            elif isinstance(c, Slider):
                c.set_value(self.priority)

#A static class to hold all the color data so I don't have to write out the correct RGB values every time.
class Color:
    WHITE = pygame.Color(255,255,255)
    BLACK = pygame.Color(0,0,0)
    LIGHT_BLUE = pygame.Color(0, 125, 200)
    RED = pygame.Color(225, 50, 50)
    GREEN = pygame.Color(25, 200, 50)
    BRIGHT_RED = pygame.Color(255, 0, 0)
    YELLOW = pygame.Color(255, 255, 0)
    GRAY = pygame.Color(130, 130, 130)

    @staticmethod
    #This method returns a color that is on the gradient between the two given colors based on the amount of steps (or divisions) to produce and which division to return (the multiplier).
    def get_color_gradient(c1, c2, divisions, multiplier):
        if multiplier == 0:
            return c1
        elif multiplier == divisions:
            return c2
        color1 = [c1.r, c1.g, c1.b]
        color2 = [c2.r, c2.g, c2.b]
        #Take the difference of each color value and divide it by the number of steps the user wanted between the target colors.
        difference = [int((color2[0] - color1[0])/divisions), int((color2[1] - color1[1])/divisions), int((color2[2] - color1[2])/divisions)]

        #Then multiply the difference by how far from the first color the user wanted and add it to the first color's values.
        return pygame.Color(color1[0] + difference[0] * multiplier, color1[1] + difference[1] * multiplier, color1[2] + difference[2] * multiplier)


#Loops through the last week of the given month in the given year and determines how many days are in that month.
def get_days_in_month(month, year):
    last_week = calendar.monthcalendar(year, month)[-1]
    total_days = 0
    for day in last_week:
        if day == 0:
            return total_days
        total_days = day
    return total_days


def main():
    #Initialize pygame GUI
    pygame.init()
    #Initialize size and black background color
    size = width, height = 600, 460

    #Create display and save the Surface object as screen
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("To-Do List")

    #Create font renderer with the consolas system font.
    writer = pygame.font.SysFont('consolas', 22)

    #Tells the program to dispatch repeat keydown events if the button is held for half a second, and then to keep dispatching every 100 millisecs until the key is not pressed.
    pygame.key.set_repeat(500, 50)

    #Sets calendar to American. Europeans and their weird Monday calendars.
    calendar.setfirstweekday(calendar.SUNDAY)

    #Create the todo list object
    todo_list = ToDoList(screen, writer)

    # Start the GUI loop
    while True:
        #Grab any events that have fired from the pygame GUI
        for event in pygame.event.get():
            #If the event is QUIT, then exit the program.
            if event.type == pygame.QUIT:
                todo_list.save()
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #If the mouse has been clicked and the task window is open, then only check the task window for click events.
                if todo_list.creating_task:
                    todo_list.task_window.mouse_click()
                #otherwise check if the main screen for click events.
                else:
                    todo_list.mouse_click()
            #If the mouse button has been unclicked, then check if the task window needs to do anything about it.
            elif event.type == pygame.MOUSEBUTTONUP:
                if todo_list.creating_task:
                    todo_list.task_window.mouse_up()
            #If an object is focused, (an input box) then process which key was pressed.
            elif todo_list.focused != None:
                if event.type == pygame.KEYDOWN:
                    todo_list.focused.process_event(event)
        
        #Fill the screen with black
        screen.fill(Color.BLACK)

        #Draw the todo list.
        todo_list.draw()

        #Flip the buffer to the screen.
        pygame.display.flip()


if __name__ == "__main__":
    main()