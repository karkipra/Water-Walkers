# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 19:47:39 2020

@author: npat
"""

class Event:
    
    # create an event
    def __init__(self, event_id):
        self.id = event_id
        self.attendees = []
        
    # add a student to an event
    def add_student(self, student_id):
        
        if student_id not in self.addendees:
            self.attendees.remove(student_id)
        else:
            # some kind of exception
            return -1
        
    # remove student from an event
    def remove_student(self, student_id):
        self.attendees.remove(student_id)