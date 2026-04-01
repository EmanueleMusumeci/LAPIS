(define (domain liftedtcore_blocksworld-domain)
 (:requirements :strips :typing :negative-preconditions :disjunctive-preconditions :equality :conditional-effects :action-costs)
 (:types block)
 (:constants
   purple_block_1 yellow_block_1 yellow_block_2 grey_block_1 - block
 )
 (:predicates (clear ?obj - block) (ontable ?obj - block) (handempty) (holding ?obj - block) (on ?obj1 - block ?obj2 - block) (hold_0) (hold_1) (hold_2) (hold_3))
 (:functions (total-cost))
 (:action pickup
  :parameters ( ?obj - block)
  :precondition (and (clear ?obj) (ontable ?obj) (handempty))
  :effect (and (holding ?obj) (not (clear ?obj)) (not (ontable ?obj)) (not (handempty)) (when (and (not (and (ontable yellow_block_2) (not (= ?obj yellow_block_2)))) (not (and (ontable yellow_block_1) (not (= ?obj yellow_block_1))))) (hold_0)) (when (or (not (and (ontable yellow_block_1) (not (= ?obj yellow_block_1)))) (= ?obj yellow_block_1) (holding yellow_block_1)) (hold_1)) (when (and (ontable grey_block_1) (not (= ?obj grey_block_1))) (hold_2)) (when (and (ontable grey_block_1) (not (= ?obj grey_block_1)) (not (or (on purple_block_1 yellow_block_2) (= ?obj yellow_block_2) (holding yellow_block_2)))) (not (hold_3))) (when (or (on purple_block_1 yellow_block_2) (= ?obj yellow_block_2) (holding yellow_block_2)) (hold_3)) (increase (total-cost) 1)))
 (:action putdown
  :parameters ( ?obj - block)
  :precondition (and (holding ?obj))
  :effect (and (clear ?obj) (handempty) (ontable ?obj) (not (holding ?obj)) (when (and (not (or (= ?obj yellow_block_2) (ontable yellow_block_2))) (not (or (= ?obj yellow_block_1) (ontable yellow_block_1)))) (hold_0)) (when (or (not (or (= ?obj yellow_block_1) (ontable yellow_block_1))) (and (holding yellow_block_1) (not (= ?obj yellow_block_1)))) (hold_1)) (when (or (= ?obj grey_block_1) (ontable grey_block_1)) (hold_2)) (when (and (or (= ?obj grey_block_1) (ontable grey_block_1)) (not (or (on purple_block_1 yellow_block_2) (and (holding yellow_block_2) (not (= ?obj yellow_block_2)))))) (not (hold_3))) (when (or (on purple_block_1 yellow_block_2) (and (holding yellow_block_2) (not (= ?obj yellow_block_2)))) (hold_3)) (increase (total-cost) 1)))
 (:action stack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (clear ?underobj) (holding ?obj))
  :effect (and (handempty) (clear ?obj) (on ?obj ?underobj) (not (clear ?underobj)) (not (holding ?obj)) (when (or (not (ontable yellow_block_1)) (and (holding yellow_block_1) (not (= ?obj yellow_block_1)))) (hold_1)) (when (and (ontable grey_block_1) (not (or (and (= ?obj purple_block_1) (= ?underobj yellow_block_2)) (on purple_block_1 yellow_block_2) (and (holding yellow_block_2) (not (= ?obj yellow_block_2)))))) (not (hold_3))) (when (or (and (= ?obj purple_block_1) (= ?underobj yellow_block_2)) (on purple_block_1 yellow_block_2) (and (holding yellow_block_2) (not (= ?obj yellow_block_2)))) (hold_3)) (increase (total-cost) 1)))
 (:action unstack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (on ?obj ?underobj) (clear ?obj) (handempty))
  :effect (and (holding ?obj) (clear ?underobj) (not (on ?obj ?underobj)) (not (clear ?obj)) (not (handempty)) (when (or (not (ontable yellow_block_1)) (= ?obj yellow_block_1) (holding yellow_block_1)) (hold_1)) (when (and (ontable grey_block_1) (not (or (and (on purple_block_1 yellow_block_2) (not (and (= ?obj purple_block_1) (= ?underobj yellow_block_2)))) (= ?obj yellow_block_2) (holding yellow_block_2)))) (not (hold_3))) (when (or (and (on purple_block_1 yellow_block_2) (not (and (= ?obj purple_block_1) (= ?underobj yellow_block_2)))) (= ?obj yellow_block_2) (holding yellow_block_2)) (hold_3)) (increase (total-cost) 1)))
)
