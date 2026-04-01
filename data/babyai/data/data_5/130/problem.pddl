(define (problem minigrid-problem)
 (:domain minigrid-domain)
 (:objects
   room_1 room_2 room_3 room_4 - room
   redtype greentype bluetype yellowtype purpletype greytype - color
   grey_door_1 purple_door_1 yellow_door_1 red_door_1 - door
   red_ball_1 green_ball_1 blue_ball_1 yellow_ball_1 yellow_ball_2 green_ball_2 - ball
   blue_box_1 green_box_1 - box
 )
 (:init (agentinroom room_1) (objectinroom yellow_ball_1 room_1) (objectinroom green_box_1 room_1) (objectinroom blue_ball_1 room_1) (objectinroom green_ball_1 room_2) (objectinroom blue_box_1 room_2) (objectinroom green_ball_2 room_3) (objectinroom red_ball_1 room_3) (objectinroom yellow_ball_2 room_3) (objectcolor yellow_ball_1 yellowtype) (objectcolor green_box_1 greentype) (objectcolor blue_ball_1 bluetype) (objectcolor green_ball_1 greentype) (objectcolor blue_box_1 bluetype) (objectcolor green_ball_2 greentype) (objectcolor red_ball_1 redtype) (objectcolor yellow_ball_2 yellowtype) (objectcolor grey_door_1 greytype) (objectcolor purple_door_1 purpletype) (objectcolor yellow_door_1 yellowtype) (objectcolor red_door_1 redtype) (emptyhands) (locked grey_door_1) (locked purple_door_1) (locked yellow_door_1) (locked red_door_1) (adjacentrooms room_2 room_1 grey_door_1) (adjacentrooms room_1 room_2 grey_door_1) (adjacentrooms room_3 room_1 purple_door_1) (adjacentrooms room_1 room_3 purple_door_1) (adjacentrooms room_4 room_2 yellow_door_1) (adjacentrooms room_2 room_4 yellow_door_1) (adjacentrooms room_4 room_3 red_door_1) (adjacentrooms room_3 room_4 red_door_1) (visited room_1) (= (total-cost) 0))
 (:goal (and (exists (?d - door)
 (and (objectcolor ?d yellowtype) (at_ ?d) (not (locked ?d))))))
 (:constraints (sometime (at_ grey_door_1)) (sometime-after (at_ grey_door_1) (or (locked grey_door_1) (at_ green_ball_1))) (always (not (agentinroom room_2))) (sometime (not (locked grey_door_1))) (sometime-before (not (locked grey_door_1)) (or (agentinroom room_4) (not (locked red_door_1)))) (sometime (or (carrying yellow_ball_2) (objectinroom red_ball_1 room_2))) (sometime (and (not (emptyhands)) (carrying blue_ball_1))))
 (:metric minimize (total-cost))
)
