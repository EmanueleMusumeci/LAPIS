(define (problem liftedtcore_minigrid-problem)
 (:domain liftedtcore_minigrid-domain)
 (:objects
   room_3 room_4 - room
   redtype greentype bluetype yellowtype purpletype greytype - color
   purple_door_1 purple_door_2 green_door_1 - door
   purple_ball_1 blue_ball_1 grey_ball_1 - ball
   yellow_box_1 grey_box_1 - box
 )
 (:init (agentinroom room_2) (objectinroom grey_box_1 room_1) (objectinroom yellow_ball_1 room_1) (objectinroom blue_ball_1 room_1) (objectinroom purple_ball_1 room_2) (objectinroom blue_ball_2 room_3) (objectinroom grey_ball_1 room_4) (objectinroom yellow_box_1 room_4) (objectinroom grey_box_2 room_4) (objectcolor grey_box_1 greytype) (objectcolor yellow_ball_1 yellowtype) (objectcolor blue_ball_1 bluetype) (objectcolor purple_ball_1 purpletype) (objectcolor blue_ball_2 bluetype) (objectcolor grey_ball_1 greytype) (objectcolor yellow_box_1 yellowtype) (objectcolor grey_box_2 greytype) (objectcolor purple_door_1 purpletype) (objectcolor grey_door_1 greytype) (objectcolor purple_door_2 purpletype) (objectcolor green_door_1 greentype) (emptyhands) (locked purple_door_1) (locked grey_door_1) (locked purple_door_2) (locked green_door_1) (adjacentrooms room_2 room_1 purple_door_1) (adjacentrooms room_1 room_2 purple_door_1) (adjacentrooms room_3 room_1 grey_door_1) (adjacentrooms room_1 room_3 grey_door_1) (adjacentrooms room_4 room_2 purple_door_2) (adjacentrooms room_2 room_4 purple_door_2) (adjacentrooms room_4 room_3 green_door_1) (adjacentrooms room_3 room_4 green_door_1) (visited room_2) (hold_0) (= (total-cost) 0))
 (:goal (and (exists (?d - door)
 (and (objectcolor ?d greytype) (at_ ?d) (not (locked ?d)))) (hold_0) (hold_1) (hold_2)))
 (:metric minimize (total-cost))
)
