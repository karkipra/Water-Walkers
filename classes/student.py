# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 19:38:50 2020

@author: npat
"""

class Student:
    
    # create student with id and list of attended events
    def __init__(self, student_id):
        self.id = student_id
        self.events = []
        
    # mark a student present at a given event
    def add_event(self, event_id):
        
        if event_id not in self.events:
            self.events.append(event_id)
        else:
            # some kind of exception
            return -1
        
    # unmark a student from an event
    def remove_event(self, event_id):
        self.events.remove(event_id)
    
    