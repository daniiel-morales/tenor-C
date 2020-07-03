from tkinter import Frame, Scrollbar, Canvas, PhotoImage, Toplevel, Label

def showAST():
    window = Toplevel()
    frame = Frame(window, bd=0)

    frame.pack(side="top", expand = True, fill="both")

    xscrollbar = Scrollbar(frame, orient="horizontal")
    xscrollbar.pack(side="bottom", fill="x")

    yscrollbar = Scrollbar(frame)
    yscrollbar.pack(side="right", fill="y")

    canvas = Canvas(frame, bd=0, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, bg = "black")
    canvas.pack(side="left", expand = True, fill="both")
    try:
        img = PhotoImage(file = "./dot/ast.gif")
        canvas.create_image(0, 0, image=img, anchor="n")
        canvas.image = img
        canvas.config(scrollregion=canvas.bbox("all"), highlightbackground="black")

        xscrollbar.config(command=canvas.xview)
        yscrollbar.config(command=canvas.yview)
    except:
        no_img = Label(frame, fg="grey", text="PLEASE MAKE\n AN\n ANALYSIS FIRST", bg="black", height =25, width =50)
        no_img.pack(side="top", expand = True, fill = "both")
        canvas.destroy()
    frame.pack()