(define (problem minigrid-problem)
 (:domain minigrid-domain)
 (:objects
   room_1 room_2 room_3 room_4 - room
   redtype greentype bluetype yellowtype purpletype greytype - color
   green_door_1 blue_door_1 blue_door_2 red_door_1 - door
   yellow_ball_1 purple_ball_1 red_ball_1 blue_ball_1 - ball
   blue_box_1 grey_box_1 blue_box_2 grey_box_2 - box
 )
 (:init (agentinroom room_4) (objectinroom grey_box_1 room_1) (objectinroom purple_ball_1 room_1) (objectinroom blue_ball_1 room_1) (objectinroom grey_box_2 room_1) (objectinroom yellow_ball_1 room_2) (objectinroom blue_box_1 room_2) (objectinroom red_ball_1 room_2) (objectinroom blue_box_2 room_3) (objectcolor grey_box_1 greytype) (objectcolor purple_ball_1 purpletype) (objectcolor blue_ball_1 bluetype) (objectcolor grey_box_2 greytype) (objectcolor yellow_ball_1 yellowtype) (objectcolor blue_box_1 bluetype) (objectcolor red_ball_1 redtype) (objectcolor blue_box_2 bluetype) (objectcolor green_door_1 greentype) (objectcolor blue_door_1 bluetype) (objectcolor blue_door_2 bluetype) (objectcolor red_door_1 redtype) (emptyhands) (locked green_door_1) (locked blue_door_1) (locked blue_door_2) (locked red_door_1) (adjacentrooms room_2 room_1 green_door_1) (adjacentrooms room_1 room_2 green_door_1) (adjacentrooms room_3 room_1 blue_door_1) (adjacentrooms room_1 room_3 blue_door_1) (adjacentrooms room_4 room_2 blue_door_2) (adjacentrooms room_2 room_4 blue_door_2) (adjacentrooms room_4 room_3 red_door_1) (adjacentrooms room_3 room_4 red_door_1) (visited room_4) (= (total-cost) 0))
 (:goal (and (exists (?d - door)
 (and (objectcolor ?d bluetype) (at_ ?d) (not (locked ?d))))))
 (:constraints (sometime (locked blue_door_2)) (sometime-after (locked blue_door_2) (or (not (emptyhands)) (agentinroom room_2))) (sometime (or (agentinroom room_3) (objectinroom blue_box_1 room_3))))
 (:metric minimize (total-cost))
)
