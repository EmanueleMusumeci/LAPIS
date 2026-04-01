(define (domain liftedtcore_minigrid-domain)
 (:requirements :strips :typing :negative-preconditions :disjunctive-preconditions :equality :conditional-effects :existential-preconditions :universal-preconditions :action-costs)
 (:types
    room objectordoor color - object
    object_ door - objectordoor
    empty_0 ball box - object_
 )
 (:constants
   grey_ball_2 grey_ball_1 - ball
   room_4 - room
   empty - empty_0
   green_door_1 - door
   purple_box_1 - box
 )
 (:predicates (agentinroom ?room - room) (objectinroom ?obj - object_ ?room - room) (objectcolor ?objectordoor - objectordoor ?color - color) (at_ ?objectordoor - objectordoor) (carrying ?obj - object_) (locked ?door - door) (adjacentrooms ?room1 - room ?room2 - room ?door - door) (blocked ?door - door ?obj - object_ ?room - room) (visited ?room - room) (emptyhands) (hold_0) (seen_psi_1) (hold_2) (hold_3) (hold_4) (hold_5))
 (:functions (total-cost))
 (:action gotoobject
  :parameters ( ?obj - object_ ?room - room)
  :precondition (and (objectinroom ?obj ?room) (agentinroom ?room))
  :effect (and(forall (?o - object_) (when (at_ ?o) (not (at_ ?o))))(forall (?d - door) (when (at_ ?d) (not (at_ ?d)))) (at_ ?obj) (when (or (= ?obj grey_ball_2) (objectinroom grey_ball_1 room_4)) (hold_4)) (increase (total-cost) 1)))
 (:action gotoempty
  :parameters ()
  :effect (and(forall (?o - object_) (when (at_ ?o) (not (at_ ?o))))(forall (?d - door) (when (at_ ?d) (not (at_ ?d)))) (at_ empty) (when (objectinroom grey_ball_1 room_4) (hold_4)) (increase (total-cost) 1)))
 (:action gotodoor
  :parameters ( ?door - door ?room1 - room ?room2 - room)
  :precondition (and (adjacentrooms ?room1 ?room2 ?door) (agentinroom ?room1) (forall (?o - object_)
 (not (blocked ?door ?o ?room1))))
  :effect (and(forall (?o - object_) (when (at_ ?o) (not (at_ ?o))))(forall (?d - door) (when (at_ ?d) (not (at_ ?d)))) (at_ ?door) (when (objectinroom grey_ball_1 room_4) (hold_4)) (increase (total-cost) 1)))
 (:action gotoroom
  :parameters ( ?room1 - room ?room2 - room ?door - door)
  :precondition (and (agentinroom ?room1) (adjacentrooms ?room1 ?room2 ?door) (not (locked ?door)))
  :effect (and (not (agentinroom ?room1)) (agentinroom ?room2) (visited ?room2)(forall (?o - object_) (when (at_ ?o) (not (at_ ?o))))(forall (?d - door) (when (at_ ?d) (not (at_ ?d)))) (when (objectinroom grey_ball_1 room_4) (hold_4)) (increase (total-cost) 1)))
 (:action pick
  :parameters ( ?obj - object_ ?room - room)
  :precondition (and (agentinroom ?room) (objectinroom ?obj ?room) (at_ ?obj) (emptyhands))
  :effect (and (not (at_ ?obj)) (not (emptyhands)) (carrying ?obj) (not (objectinroom ?obj ?room))(forall (?d - door) (when (blocked ?d ?obj ?room) (not (blocked ?d ?obj ?room)))) (when (or (= ?obj grey_ball_2) (carrying grey_ball_2)) (seen_psi_1)) (when (and (locked green_door_1) (not (or (= ?obj grey_ball_2) (carrying grey_ball_2)))) (not (hold_3))) (when (or (= ?obj grey_ball_2) (carrying grey_ball_2)) (hold_3)) (when (or (and (at_ grey_ball_2) (not (= ?obj grey_ball_2))) (and (objectinroom grey_ball_1 room_4) (not (and (= ?obj grey_ball_1) (= ?room room_4))))) (hold_4)) (when (or (= ?obj purple_box_1) (carrying purple_box_1)) (hold_5)) (increase (total-cost) 1)))
 (:action drop
  :parameters ( ?obj - object_ ?room - room)
  :precondition (and (agentinroom ?room) (carrying ?obj) (not (emptyhands)) (at_ empty))
  :effect (and (not (carrying ?obj)) (at_ ?obj) (not (at_ empty)) (emptyhands) (objectinroom ?obj ?room) (when (and (carrying grey_ball_2) (not (= ?obj grey_ball_2))) (seen_psi_1)) (when (and (locked green_door_1) (not (and (carrying grey_ball_2) (not (= ?obj grey_ball_2))))) (not (hold_3))) (when (and (carrying grey_ball_2) (not (= ?obj grey_ball_2))) (hold_3)) (when (or (= ?obj grey_ball_2) (at_ grey_ball_2) (and (= ?obj grey_ball_1) (= ?room room_4)) (objectinroom grey_ball_1 room_4)) (hold_4)) (when (and (carrying purple_box_1) (not (= ?obj purple_box_1))) (hold_5)) (increase (total-cost) 1)))
 (:action toggle
  :parameters ( ?door - door)
  :precondition (and (at_ ?door) (or (and (not (locked ?door)) (= ?door green_door_1)) (and (locked green_door_1) (not (and (locked ?door) (= ?door green_door_1)))) (seen_psi_1)))
  :effect (and (when (not (locked ?door)) (locked ?door)) (when (locked ?door) (not (locked ?door))) (when (not (or (and (not (locked ?door)) (= ?door green_door_1)) (and (locked green_door_1) (not (and (locked ?door) (= ?door green_door_1)))))) (hold_0)) (when (or (and (not (locked ?door)) (= ?door green_door_1)) (and (locked green_door_1) (not (and (locked ?door) (= ?door green_door_1))))) (hold_2)) (when (and (or (and (not (locked ?door)) (= ?door green_door_1)) (and (locked green_door_1) (not (and (locked ?door) (= ?door green_door_1))))) (not (carrying grey_ball_2))) (not (hold_3))) (increase (total-cost) 1)))
)
