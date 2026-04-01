(define (problem minigrid-problem)
 (:domain minigrid-domain)
 (:objects
   room_1 room_2 room_3 room_4 - room
   redtype greentype bluetype yellowtype purpletype greytype - color
   green_door_1 yellow_door_1 green_door_2 red_door_1 - door
   purple_box_2 green_box_1 purple_box_1 grey_box_1 - box
   blue_ball_3 blue_ball_1 blue_ball_2 red_ball_1 - ball
 )
 (:init (agentinroom room_4) (objectinroom purple_box_1 room_1) (objectinroom blue_ball_1 room_1) (objectinroom purple_box_2 room_1) (objectinroom blue_ball_2 room_2) (objectinroom red_ball_1 room_2) (objectinroom green_box_1 room_2) (objectinroom blue_ball_3 room_3) (objectinroom grey_box_1 room_4) (objectcolor purple_box_1 purpletype) (objectcolor blue_ball_1 bluetype) (objectcolor purple_box_2 purpletype) (objectcolor blue_ball_2 bluetype) (objectcolor red_ball_1 redtype) (objectcolor green_box_1 greentype) (objectcolor blue_ball_3 bluetype) (objectcolor grey_box_1 greytype) (objectcolor green_door_1 greentype) (objectcolor yellow_door_1 yellowtype) (objectcolor green_door_2 greentype) (objectcolor red_door_1 redtype) (emptyhands) (locked green_door_1) (locked yellow_door_1) (locked green_door_2) (locked red_door_1) (adjacentrooms room_2 room_1 green_door_1) (adjacentrooms room_1 room_2 green_door_1) (adjacentrooms room_3 room_1 yellow_door_1) (adjacentrooms room_1 room_3 yellow_door_1) (adjacentrooms room_4 room_2 green_door_2) (adjacentrooms room_2 room_4 green_door_2) (adjacentrooms room_4 room_3 red_door_1) (adjacentrooms room_3 room_4 red_door_1) (visited room_4) (= (total-cost) 0))
 (:goal (and (exists (?v - box)
 (and (objectcolor ?v purpletype) (objectinroom ?v room_1) (agentinroom room_1) (at_ ?v)))))
 (:metric minimize (total-cost))
)
