import rx
from rx.scheduler import ThreadPoolScheduler
import time
#import tkinter as tk
import snappy

class UI:
   def __init__(self):
      #M = snappy.Manifold() 
      self.root = snappy.Manifold()
      self.pd = None
      self.pool_scheduler = ThreadPoolScheduler(1) # thread pool with 1 worker thread
      #self.button = tk.Button(text="Do Task", command=self.do_task).pack()
      self.do_task()

   def do_task(self):
      rx.empty().subscribe(
         on_completed=self.long_running_task, 
         scheduler=self.pool_scheduler
      )

   def long_running_task(self):
      # your long running task here... eg:
      input( "Draw loop and send to snappy. Press any key when finished." )
      #time.sleep(3)
      # if you want a callback on the main thread:
      print( "hi" )
      print( self.root.getPDcode() )
      self.pd = self.root.getPDcode()
      self.root.after(5, self.on_task_complete)
      
      #print( "hi" )

   def on_task_complete(self):
       return self.root.getPDcode()
       pass
       #pass # runs on main thread

if __name__ == "__main__":
    ui = UI()
    #print( ui.on_task_complete() )
    #ui.root.mainloop()
    #print( ui.pd )
    #print( ui.pd )
