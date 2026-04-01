(define (domain liftedtcore_minigrid-domain)
 (:requirements :strips :typing :negative-preconditions :disjunctive-preconditions :equality :conditional-effects :existential-preconditions :universal-preconditions :action-costs)
 (:types
    room objectordoor color - object
    object_ door - objectordoor
    empty_0 ball box - object_
 )
 (:constants
   grey_ball_3 grey_ball_2 - ball
   red_box_1 blue_box_1 - box
   room_1 room_4 room_3 - room
   empty - empty_0
   grey_door_1 purple_door_1 green_door_1 - door
 )
 (:predicates (agentinroom ?room - room) (objectinroom ?obj - object_ ?room - room) (objectcolor ?objectordoor - objectordoor ?color - color) (at_ ?objectordoor - objectordoor) (carrying ?obj - object_) (locked ?door - door) (adjacentrooms ?room1 - room ?room2 - room ?door - door) (blocked ?door - door ?obj - object_ ?room - room) (visited ?room - room) (emptyhands) (hold_0) (hold_1) (hold_2) (hold_3) (seen_psi_4) (hold_5) (seen_psi_6) (hold_7))
 (:functions (total-cost))
 (:action gotoobject
  :parameters ( ?obj - object_ ?room - room)
  :precondition (and (objectinroom ?obj ?room) (agentinroom ?room) (or (not (= ?obj grey_ball_3)) (seen_psi_4)))
  :effect (and(forall (?o - object_) (when (at_ ?o) (not (at_ ?o))))(forall (?d - door) (when (at_ ?d) (not (at_ ?d)))) (at_ ?obj) (when (and (objectinroom blue_box_1 room_4) (= ?obj red_box_1)) (hold_0)) (when (= ?obj grey_ball_3) (hold_3)) (increase (total-cost) 1)))
 (:action gotoempty
  :parameters ()
  :effect (and(forall (?o - object_) (when (at_ ?o) (not (at_ ?o))))(forall (?d - door) (when (at_ ?d) (not (at_ ?d)))) (at_ empty) (increase (total-cost) 1)))
 (:action gotodoor
  :parameters ( ?door - door ?room1 - room ?room2 - room)
  :precondition (and (adjacentrooms ?room1 ?room2 ?door) (agentinroom ?room1) (forall (?o - object_)
 (not (blocked ?door ?o ?room1))))
  :effect (and(forall (?o - object_) (when (at_ ?o) (not (at_ ?o))))(forall (?d - door) (when (at_ ?d) (not (at_ ?d)))) (at_ ?door) (when (and (= ?door green_door_1) (not (emptyhands))) (hold_7)) (increase (total-cost) 1)))
 (:action gotoroom
  :parameters ( ?room1 - room ?room2 - room ?door - door)
  :precondition (and (agentinroom ?room1) (adjacentrooms ?room1 ?room2 ?door) (not (locked ?door)) (or (not (or (= ?room2 room_4) (and (agentinroom room_4) (not (= ?room1 room_4))))) (seen_psi_6)))
  :effect (and (not (agentinroom ?room1)) (agentinroom ?room2) (visited ?room2)(forall (?o - object_) (when (at_ ?o) (not (at_ ?o))))(forall (?d - door) (when (at_ ?d) (not (at_ ?d)))) (when (and (locked purple_door_1) (not (or (objectinroom blue_box_1 room_1) (= ?room2 room_1) (and (agentinroom room_1) (not (= ?room1 room_1)))))) (not (hold_2))) (when (or (objectinroom blue_box_1 room_1) (= ?room2 room_1) (and (agentinroom room_1) (not (= ?room1 room_1)))) (hold_2)) (when (or (not (locked grey_door_1)) (= ?room2 room_3) (and (agentinroom room_3) (not (= ?room1 room_3)))) (seen_psi_4)) (when (or (= ?room2 room_4) (and (agentinroom room_4) (not (= ?room1 room_4)))) (hold_5)) (increase (total-cost) 1)))
 (:action pick
  :parameters ( ?obj - object_ ?room - room)
  :precondition (and (agentinroom ?room) (objectinroom ?obj ?room) (at_ ?obj) (emptyhands) (or (not (and (at_ grey_ball_3) (not (= ?obj grey_ball_3)))) (seen_psi_4)))
  :effect (and (not (at_ ?obj)) (not (emptyhands)) (carrying ?obj) (not (objectinroom ?obj ?room))(forall (?d - door) (when (blocked ?d ?obj ?room) (not (blocked ?d ?obj ?room)))) (when (and (objectinroom blue_box_1 room_4) (not (and (= ?obj blue_box_1) (= ?room room_4))) (at_ red_box_1) (not (= ?obj red_box_1))) (hold_0)) (when (and (locked purple_door_1) (not (or (and (objectinroom blue_box_1 room_1) (not (and (= ?obj blue_box_1) (= ?room room_1)))) (agentinroom room_1)))) (not (hold_2))) (when (or (and (objectinroom blue_box_1 room_1) (not (and (= ?obj blue_box_1) (= ?room room_1)))) (agentinroom room_1)) (hold_2)) (when (and (at_ grey_ball_3) (not (= ?obj grey_ball_3))) (hold_3)) (when (or (= ?obj grey_ball_2) (carrying grey_ball_2)) (seen_psi_6)) (when (at_ green_door_1) (hold_7)) (increase (total-cost) 1)))
 (:action drop
  :parameters ( ?obj - object_ ?room - room)
  :precondition (and (agentinroom ?room) (carrying ?obj) (not (emptyhands)) (at_ empty) (or (not (or (= ?obj grey_ball_3) (at_ grey_ball_3))) (seen_psi_4)))
  :effect (and (not (carrying ?obj)) (at_ ?obj) (not (at_ empty)) (emptyhands) (objectinroom ?obj ?room) (when (and (or (and (= ?obj blue_box_1) (= ?room room_4)) (objectinroom blue_box_1 room_4)) (or (= ?obj red_box_1) (at_ red_box_1))) (hold_0)) (when (and (locked purple_door_1) (not (or (and (= ?obj blue_box_1) (= ?room room_1)) (objectinroom blue_box_1 room_1) (agentinroom room_1)))) (not (hold_2))) (when (or (and (= ?obj blue_box_1) (= ?room room_1)) (objectinroom blue_box_1 room_1) (agentinroom room_1)) (hold_2)) (when (or (= ?obj grey_ball_3) (at_ grey_ball_3)) (hold_3)) (when (and (carrying grey_ball_2) (not (= ?obj grey_ball_2))) (seen_psi_6)) (increase (total-cost) 1)))
 (:action toggle
  :parameters ( ?door - door)
  :precondition (and (at_ ?door))
  :effect (and (when (not (locked ?door)) (locked ?door)) (when (locked ?door) (not (locked ?door))) (when (or (and (not (locked ?door)) (= ?door purple_door_1)) (and (locked purple_door_1) (not (and (locked ?door) (= ?door purple_door_1))))) (hold_1)) (when (and (or (and (not (locked ?door)) (= ?door purple_door_1)) (and (locked purple_door_1) (not (and (locked ?door) (= ?door purple_door_1))))) (not (or (objectinroom blue_box_1 room_1) (agentinroom room_1)))) (not (hold_2))) (when (or (not (or (and (not (locked ?door)) (= ?door grey_door_1)) (and (locked grey_door_1) (not (and (locked ?door) (= ?door grey_door_1)))))) (agentinroom room_3)) (seen_psi_4)) (increase (total-cost) 1)))
)
