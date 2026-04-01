(define (domain liftedtcore_blocksworld-domain)
 (:requirements :strips :typing :negative-preconditions :disjunctive-preconditions :equality :conditional-effects :action-costs)
 (:types block)
 (:constants
   yellow_block_2 brown_block_1 blue_block_1 yellow_block_1 grey_block_1 - block
 )
 (:predicates (clear ?obj - block) (ontable ?obj - block) (handempty) (holding ?obj - block) (on ?obj1 - block ?obj2 - block) (hold_0) (hold_1) (seen_psi_2) (hold_3) (hold_4) (hold_5))
 (:functions (total-cost))
 (:action pickup
  :parameters ( ?obj - block)
  :precondition (and (clear ?obj) (ontable ?obj) (handempty) (or (not (and (ontable yellow_block_2) (not (= ?obj yellow_block_2)))) (seen_psi_2)) (not (and (ontable grey_block_1) (not (= ?obj grey_block_1)))))
  :effect (and (holding ?obj) (not (clear ?obj)) (not (ontable ?obj)) (not (handempty)) (when (or (on brown_block_1 grey_block_1) (= ?obj yellow_block_1) (holding yellow_block_1)) (hold_0)) (when (and (ontable yellow_block_2) (not (= ?obj yellow_block_2))) (hold_1)) (when (or (= ?obj grey_block_1) (holding grey_block_1)) (seen_psi_2)) (when (or (= ?obj blue_block_1) (holding blue_block_1)) (hold_3)) (when (and (or (= ?obj blue_block_1) (holding blue_block_1)) (not (on yellow_block_2 brown_block_1))) (not (hold_4))) (when (and (not (and (clear yellow_block_1) (not (= ?obj yellow_block_1)))) (ontable blue_block_1) (not (= ?obj blue_block_1))) (hold_5)) (increase (total-cost) 1)))
 (:action putdown
  :parameters ( ?obj - block)
  :precondition (and (holding ?obj) (or (not (or (= ?obj yellow_block_2) (ontable yellow_block_2))) (seen_psi_2)) (not (or (= ?obj grey_block_1) (ontable grey_block_1))))
  :effect (and (clear ?obj) (handempty) (ontable ?obj) (not (holding ?obj)) (when (or (on brown_block_1 grey_block_1) (and (holding yellow_block_1) (not (= ?obj yellow_block_1)))) (hold_0)) (when (or (= ?obj yellow_block_2) (ontable yellow_block_2)) (hold_1)) (when (and (holding grey_block_1) (not (= ?obj grey_block_1))) (seen_psi_2)) (when (and (holding blue_block_1) (not (= ?obj blue_block_1))) (hold_3)) (when (and (holding blue_block_1) (not (= ?obj blue_block_1)) (not (on yellow_block_2 brown_block_1))) (not (hold_4))) (when (and (not (or (= ?obj yellow_block_1) (clear yellow_block_1))) (or (= ?obj blue_block_1) (ontable blue_block_1))) (hold_5)) (increase (total-cost) 1)))
 (:action stack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (clear ?underobj) (holding ?obj))
  :effect (and (handempty) (clear ?obj) (on ?obj ?underobj) (not (clear ?underobj)) (not (holding ?obj)) (when (or (and (= ?obj brown_block_1) (= ?underobj grey_block_1)) (on brown_block_1 grey_block_1) (and (holding yellow_block_1) (not (= ?obj yellow_block_1)))) (hold_0)) (when (and (holding grey_block_1) (not (= ?obj grey_block_1))) (seen_psi_2)) (when (and (holding blue_block_1) (not (= ?obj blue_block_1))) (hold_3)) (when (and (holding blue_block_1) (not (= ?obj blue_block_1)) (not (or (and (= ?obj yellow_block_2) (= ?underobj brown_block_1)) (on yellow_block_2 brown_block_1)))) (not (hold_4))) (when (or (and (= ?obj yellow_block_2) (= ?underobj brown_block_1)) (on yellow_block_2 brown_block_1)) (hold_4)) (when (and (not (or (= ?obj yellow_block_1) (and (clear yellow_block_1) (not (= ?underobj yellow_block_1))))) (ontable blue_block_1)) (hold_5)) (increase (total-cost) 1)))
 (:action unstack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (on ?obj ?underobj) (clear ?obj) (handempty))
  :effect (and (holding ?obj) (clear ?underobj) (not (on ?obj ?underobj)) (not (clear ?obj)) (not (handempty)) (when (or (and (on brown_block_1 grey_block_1) (not (and (= ?obj brown_block_1) (= ?underobj grey_block_1)))) (= ?obj yellow_block_1) (holding yellow_block_1)) (hold_0)) (when (or (= ?obj grey_block_1) (holding grey_block_1)) (seen_psi_2)) (when (or (= ?obj blue_block_1) (holding blue_block_1)) (hold_3)) (when (and (or (= ?obj blue_block_1) (holding blue_block_1)) (not (and (on yellow_block_2 brown_block_1) (not (and (= ?obj yellow_block_2) (= ?underobj brown_block_1)))))) (not (hold_4))) (when (and (on yellow_block_2 brown_block_1) (not (and (= ?obj yellow_block_2) (= ?underobj brown_block_1)))) (hold_4)) (when (and (not (or (= ?underobj yellow_block_1) (and (clear yellow_block_1) (not (= ?obj yellow_block_1))))) (ontable blue_block_1)) (hold_5)) (increase (total-cost) 1)))
)
