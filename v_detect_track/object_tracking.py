# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: Building object tracking model
# Date Created: 15/06/2022

class object_tracker:
    def __init__(self):
        # Variable for tracking the current using object indexes
        self.cur_obj_idxes = set()
        # Variable for first initial frame
        self.init_idx = -1
        
    # Initiating object indexes for initial frame
    def acq_init_idx(self):
        # Initializing first index of obejct for first frame
        self.init_idx += 1
        
        return self.init_idx
    
    # Acquring the smallest unused indexes if is not initial frame
    def acq_next_free_idx(self):
        begin = 0
        
        while True:
            if (begin in self.cur_obj_idxes) == True:
                begin += 1
            else:
                return begin
            
    # Acquring the Euclidean distance of object within prev frame and current frame -> d = √[(x2–x1)**2 + (y2– y1)**2]
    def acq_euc_dist(self, prev_pt, cur_pt):
        # x point
        x_power2 = (cur_pt[0] - prev_pt[0])**2
        # y point
        y_power2 = (cur_pt[1] - prev_pt[1])**2
        # Euclidean distance
        d = (x_power2 + y_power2)**0.5
        
        return d
    
    # Track current objects with distinct unique ID
    '''
    Tracking Object Storing Format:
        Index 0: Midpoint of object (tuple structure)
        Index 1: Object ID
        Index 2: Number of consecutive frames detected for
        Index 3: Midpoint of object over previous 5 consecutive frames (double-ended queue structure)
        Index 4: Points to the new obj according to old obj assigned (array structure) -> avoid conflict within tracked objs
        Index 5: Magnitude of object vectore in prev frame
    '''
    def arr_cur_objs(self, prev_objs, cur_objs):
        # Reset all the indexes for multiple time calling of function
        self.cur_obj_idxes = set()
        
        # Loop all objects in current frame vs previous frame to keep track of the objects
        for i in range(0, len(cur_objs)):
            min_eu_dist = 99999 # initiate as 99999 for if first frame
            min_eu_dist_index = None
            
            for j in range(0, len(prev_objs)):
                # Comparing the new distance (if new calculated dist <= prev dist)
                new_calcdist = self.acq_euc_dist(prev_objs[j][0], cur_objs[i][0])
                if (new_calcdist <= min_eu_dist):
                    min_eu_dist = new_calcdist
                    min_eu_dist_index = j
                    
            # If previous obj ady assigned to a current
            if (prev_objs[min_eu_dist_index][4] != -1):
                # Existing distance of prev objs and new objs
                eu_dist1 = self.acq_euc_dist(prev_objs[min_eu_dist_index][0], cur_objs[prev_objs[min_eu_dist_index][4]][0])
                # New distance of prev objs and new objs
                eu_dist2 = self.acq_euc_dist(prev_objs[min_eu_dist_index][0], cur_objs[i][0])
                
                # Check new conflicting objs is actually the prev tracked objs
                if (eu_dist2 <= eu_dist1):
                    # Add the indexs to used indexes variable
                    self.cur_obj_idxes.add(prev_objs[min_eu_dist_index][1])
                    # Update the ID within current obj and prev obj frame
                    cur_objs[i][1] = prev_objs[min_eu_dist_index][1]
                    # Set prevly not participating new obj as unused (for next new detection)
                    cur_objs[prev_objs[min_eu_dist_index][4]][4] = -1
                    # Set the new conflicting obj as used
                    cur_objs[i][4] = min_eu_dist_index
                    # Set the prev point to current conflicting obj point
                    prev_objs[min_eu_dist_index][4] = i
                else:
                    # Set the new obj as unused for later new idx assign (new object)
                    cur_objs[i][4] = -1
                    continue
            # If prev obj havent assigned to a current
            else:
                self.cur_obj_idxes.add(prev_objs[min_eu_dist_index][-1])
                # Set the new object ID
                cur_objs[i][1] = prev_objs[min_eu_dist_index][1]
                # Update prev obj to point of new obj
                prev_objs[min_eu_dist_index][4] = i
                # Set new obj as used
                cur_objs[i][4] = min_eu_dist_index
                
        # Update the magnitude of prev obj for usage of suspected accident detection later
        for i in range(0, len(cur_objs)):
            # Do only for those tracked obj
            if (cur_objs[i][4] != -1):
                tracked_prev_obj = cur_objs[i][4]
                
                # Do only if detected for consecutive 5 frames
                if (prev_objs[tracked_prev_obj][2] < 5):
                    cur_objs[i][3] = prev_objs[tracked_prev_obj][3].copy()
                    cur_objs[i][3].append(cur_objs[i][0])
                else:
                    cur_objs[i][3] = prev_objs[tracked_prev_obj][3].copy()
                    cur_objs[i][3].popleft() # deque structure pop
                    cur_objs[i][3].append(cur_objs[i][0])
                    
                    # Set current object's vector magnitude as previous obj
                    x_mag = prev_objs[tracked_prev_obj][3][-1][0] - prev_objs[tracked_prev_obj][3][0][0]
                    y_mag = prev_objs[tracked_prev_obj][3][-1][1] - prev_objs[tracked_prev_obj][3][0][1]
                    vect = [x_mag, y_mag]
                    vect_mag = (vect[0]**2 + vect[1]**2)**(0.5) # Euclidean distance formula
                    cur_objs[i][5] == vect_mag
                    
                # Update the consecutive frame detection count
                cur_objs[i][2] = prev_objs[tracked_prev_obj][2] + 1
                
        # Handles those newly track objects -> assign to unused index
        for new_obj in cur_objs:
            # Index 4 empty indicate new obj in tracking
            if new_obj[4] == -1:
                # Define the next index number
                new_obj[1] = self.acq_next_free_idx()
                # Set the define number to unused list for next frame tracking
                self.cur_obj_idxes.add(new_obj[1])
            else:
                # Else clear the index 4 of object
                new_obj[4] = -1
                
        return cur_objs
                
        
                
                
            
            