(define (domain liftedtcore_blocksworld-domain)
 (:requirements :strips :typing :negative-preconditions :disjunctive-preconditions :equality :conditional-effects :action-costs)
 (:types block)
 (:constants
   brown_block_2 brown_block_1 red_block_1 blue_block_1 grey_block_1 - block
 )
 (:predicates (clear ?obj - block) (ontable ?obj - block) (handempty) (holding ?obj - block) (on ?obj1 - block ?obj2 - block) (hold_0) (hold_1) (hold_2) (hold_3))
 (:functions (total-cost))
 (:action pickup
  :parameters ( ?obj - block)
  :precondition (and (clear ?obj) (ontable ?obj) (handempty))
  :effect (and (holding ?obj) (not (clear ?obj)) (not (ontable ?obj)) (not (handempty)) (when (or (= ?obj brown_block_2) (holding brown_block_2)) (hold_0)) (when (and (or (= ?obj brown_block_2) (holding brown_block_2)) (not (or (= ?obj blue_block_1) (holding blue_block_1)))) (not (hold_1))) (when (or (= ?obj blue_block_1) (holding blue_block_1)) (hold_1)) (when (and (not (on brown_block_1 grey_block_1)) (not (or (on red_block_1 grey_block_1) (= ?obj red_block_1) (holding red_block_1)))) (not (hold_3))) (when (or (on red_block_1 grey_block_1) (= ?obj red_block_1) (holding red_block_1)) (hold_3)) (increase (total-cost) 1)))
 (:action putdown
  :parameters ( ?obj - block)
  :precondition (and (holding ?obj))
  :effect (and (clear ?obj) (handempty) (ontable ?obj) (not (holding ?obj)) (when (and (holding brown_block_2) (not (= ?obj brown_block_2))) (hold_0)) (when (and (holding brown_block_2) (not (= ?obj brown_block_2)) (not (and (holding blue_block_1) (not (= ?obj blue_block_1))))) (not (hold_1))) (when (and (holding blue_block_1) (not (= ?obj blue_block_1))) (hold_1)) (when (and (not (on brown_block_1 grey_block_1)) (not (or (on red_block_1 grey_block_1) (and (holding red_block_1) (not (= ?obj red_block_1)))))) (not (hold_3))) (when (or (on red_block_1 grey_block_1) (and (holding red_block_1) (not (= ?obj red_block_1)))) (hold_3)) (increase (total-cost) 1)))
 (:action stack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (clear ?underobj) (holding ?obj))
  :effect (and (handempty) (clear ?obj) (on ?obj ?underobj) (not (clear ?underobj)) (not (holding ?obj)) (when (and (holding brown_block_2) (not (= ?obj brown_block_2))) (hold_0)) (when (and (holding brown_block_2) (not (= ?obj brown_block_2)) (not (and (holding blue_block_1) (not (= ?obj blue_block_1))))) (not (hold_1))) (when (and (holding blue_block_1) (not (= ?obj blue_block_1))) (hold_1)) (when (not (or (and (= ?obj brown_block_1) (= ?underobj grey_block_1)) (on brown_block_1 grey_block_1))) (hold_2)) (when (and (not (or (and (= ?obj brown_block_1) (= ?underobj grey_block_1)) (on brown_block_1 grey_block_1))) (not (or (and (= ?obj red_block_1) (= ?underobj grey_block_1)) (on red_block_1 grey_block_1) (and (holding red_block_1) (not (= ?obj red_block_1)))))) (not (hold_3))) (when (or (and (= ?obj red_block_1) (= ?underobj grey_block_1)) (on red_block_1 grey_block_1) (and (holding red_block_1) (not (= ?obj red_block_1)))) (hold_3)) (increase (total-cost) 1)))
 (:action unstack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (on ?obj ?underobj) (clear ?obj) (handempty))
  :effect (and (holding ?obj) (clear ?underobj) (not (on ?obj ?underobj)) (not (clear ?obj)) (not (handempty)) (when (or (= ?obj brown_block_2) (holding brown_block_2)) (hold_0)) (when (and (or (= ?obj brown_block_2) (holding brown_block_2)) (not (or (= ?obj blue_block_1) (holding blue_block_1)))) (not (hold_1))) (when (or (= ?obj blue_block_1) (holding blue_block_1)) (hold_1)) (when (not (and (on brown_block_1 grey_block_1) (not (and (= ?obj brown_block_1) (= ?underobj grey_block_1))))) (hold_2)) (when (and (not (and (on brown_block_1 grey_block_1) (not (and (= ?obj brown_block_1) (= ?underobj grey_block_1))))) (not (or (and (on red_block_1 grey_block_1) (not (and (= ?obj red_block_1) (= ?underobj grey_block_1)))) (= ?obj red_block_1) (holding red_block_1)))) (not (hold_3))) (when (or (and (on red_block_1 grey_block_1) (not (and (= ?obj red_block_1) (= ?underobj grey_block_1)))) (= ?obj red_block_1) (holding red_block_1)) (hold_3)) (increase (total-cost) 1)))
)
