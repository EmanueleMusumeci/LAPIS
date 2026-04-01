(define (problem liftedtcore_minigrid-problem)
 (:domain liftedtcore_minigrid-domain)
 (:objects
   room_1 room_2 room_4 - room
   redtype greentype bluetype yellowtype purpletype greytype - color
   red_door_1 blue_door_1 blue_door_2 - door
   red_box_1 purple_box_1 yellow_box_1 - box
   grey_ball_2 purple_ball_1 grey_ball_1 green_ball_1 blue_ball_1 - ball
 )
 (:init (agentinroom room_4) (objectinroom blue_ball_1 room_1) (objectinroom grey_ball_1 room_1) (objectinroom purple_box_1 room_1) (objectinroom purple_ball_1 room_2) (objectinroom green_ball_1 room_2) (objectinroom red_box_1 room_2) (objectinroom grey_ball_2 room_3) (objectinroom yellow_box_1 room_4) (objectcolor blue_ball_1 bluetype) (objectcolor grey_ball_1 greytype) (objectcolor purple_box_1 purpletype) (objectcolor purple_ball_1 purpletype) (objectcolor green_ball_1 greentype) (objectcolor red_box_1 redtype) (objectcolor grey_ball_2 greytype) (objectcolor yellow_box_1 yellowtype) (objectcolor red_door_1 redtype) (objectcolor blue_door_1 bluetype) (objectcolor grey_door_1 greytype) (objectcolor blue_door_2 bluetype) (emptyhands) (locked red_door_1) (locked blue_door_1) (locked grey_door_1) (locked blue_door_2) (adjacentrooms room_2 room_1 red_door_1) (adjacentrooms room_1 room_2 red_door_1) (adjacentrooms room_3 room_1 blue_door_1) (adjacentrooms room_1 room_3 blue_door_1) (adjacentrooms room_4 room_2 grey_door_1) (adjacentrooms room_2 room_4 grey_door_1) (adjacentrooms room_4 room_3 blue_door_2) (adjacentrooms room_3 room_4 blue_door_2) (visited room_4) (= (total-cost) 0))
 (:goal (and (exists (?d - door)
 (and (objectcolor ?d greytype) (at_ ?d) (not (locked ?d)))) (hold_0)))
 (:metric minimize (total-cost))
)
