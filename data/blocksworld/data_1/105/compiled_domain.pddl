(define (domain liftedtcore_blocksworld-domain)
 (:requirements :strips :typing :negative-preconditions :disjunctive-preconditions :equality :conditional-effects :action-costs)
 (:types block)
 (:constants
   brown_block_2 blue_block_1 - block
 )
 (:predicates (clear ?obj - block) (ontable ?obj - block) (handempty) (holding ?obj - block) (on ?obj1 - block ?obj2 - block) (hold_0) (hold_1))
 (:functions (total-cost))
 (:action pickup
  :parameters ( ?obj - block)
  :precondition (and (clear ?obj) (ontable ?obj) (handempty))
  :effect (and (holding ?obj) (not (clear ?obj)) (not (ontable ?obj)) (not (handempty)) (when (or (= ?obj brown_block_2) (holding brown_block_2)) (hold_0)) (when (and (or (= ?obj brown_block_2) (holding brown_block_2)) (not (or (= ?obj blue_block_1) (holding blue_block_1)))) (not (hold_1))) (when (or (= ?obj blue_block_1) (holding blue_block_1)) (hold_1)) (increase (total-cost) 1)))
 (:action putdown
  :parameters ( ?obj - block)
  :precondition (and (holding ?obj))
  :effect (and (clear ?obj) (handempty) (ontable ?obj) (not (holding ?obj)) (when (and (holding brown_block_2) (not (= ?obj brown_block_2))) (hold_0)) (when (and (holding brown_block_2) (not (= ?obj brown_block_2)) (not (and (holding blue_block_1) (not (= ?obj blue_block_1))))) (not (hold_1))) (when (and (holding blue_block_1) (not (= ?obj blue_block_1))) (hold_1)) (increase (total-cost) 1)))
 (:action stack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (clear ?underobj) (holding ?obj))
  :effect (and (handempty) (clear ?obj) (on ?obj ?underobj) (not (clear ?underobj)) (not (holding ?obj)) (when (and (holding brown_block_2) (not (= ?obj brown_block_2))) (hold_0)) (when (and (holding brown_block_2) (not (= ?obj brown_block_2)) (not (and (holding blue_block_1) (not (= ?obj blue_block_1))))) (not (hold_1))) (when (and (holding blue_block_1) (not (= ?obj blue_block_1))) (hold_1)) (increase (total-cost) 1)))
 (:action unstack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (on ?obj ?underobj) (clear ?obj) (handempty))
  :effect (and (holding ?obj) (clear ?underobj) (not (on ?obj ?underobj)) (not (clear ?obj)) (not (handempty)) (when (or (= ?obj brown_block_2) (holding brown_block_2)) (hold_0)) (when (and (or (= ?obj brown_block_2) (holding brown_block_2)) (not (or (= ?obj blue_block_1) (holding blue_block_1)))) (not (hold_1))) (when (or (= ?obj blue_block_1) (holding blue_block_1)) (hold_1)) (increase (total-cost) 1)))
)
