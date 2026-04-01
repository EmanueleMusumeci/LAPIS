(define (domain liftedtcore_blocksworld-domain)
 (:requirements :strips :typing :negative-preconditions :disjunctive-preconditions :equality :conditional-effects :action-costs)
 (:types block)
 (:constants
   black_block_2 yellow_block_1 black_block_1 white_block_1 orange_block_1 - block
 )
 (:predicates (clear ?obj - block) (ontable ?obj - block) (handempty) (holding ?obj - block) (on ?obj1 - block ?obj2 - block) (hold_0) (seen_psi_1) (hold_2) (seen_psi_3) (hold_4) (hold_5))
 (:functions (total-cost))
 (:action pickup
  :parameters ( ?obj - block)
  :precondition (and (clear ?obj) (ontable ?obj) (handempty) (or (not (or (= ?obj white_block_1) (holding white_block_1))) (seen_psi_1)) (or (not (and (clear yellow_block_1) (not (= ?obj yellow_block_1)))) (seen_psi_3)))
  :effect (and (holding ?obj) (not (clear ?obj)) (not (ontable ?obj)) (not (handempty)) (when (or (= ?obj white_block_1) (holding white_block_1)) (hold_0)) (when (and (clear black_block_1) (not (= ?obj black_block_1))) (seen_psi_1)) (when (and (clear yellow_block_1) (not (= ?obj yellow_block_1))) (hold_2)) (when (not (and (clear black_block_2) (not (= ?obj black_block_2)))) (hold_4)) (when (not (and (ontable yellow_block_1) (not (= ?obj yellow_block_1)))) (hold_5)) (increase (total-cost) 1)))
 (:action putdown
  :parameters ( ?obj - block)
  :precondition (and (holding ?obj) (or (not (and (holding white_block_1) (not (= ?obj white_block_1)))) (seen_psi_1)) (or (not (or (= ?obj yellow_block_1) (clear yellow_block_1))) (seen_psi_3)))
  :effect (and (clear ?obj) (handempty) (ontable ?obj) (not (holding ?obj)) (when (and (holding white_block_1) (not (= ?obj white_block_1))) (hold_0)) (when (or (= ?obj black_block_1) (clear black_block_1)) (seen_psi_1)) (when (or (= ?obj yellow_block_1) (clear yellow_block_1)) (hold_2)) (when (not (or (= ?obj black_block_2) (clear black_block_2))) (hold_4)) (when (not (or (= ?obj yellow_block_1) (ontable yellow_block_1))) (hold_5)) (increase (total-cost) 1)))
 (:action stack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (clear ?underobj) (holding ?obj) (or (not (and (holding white_block_1) (not (= ?obj white_block_1)))) (seen_psi_1)) (or (not (or (= ?obj yellow_block_1) (and (clear yellow_block_1) (not (= ?underobj yellow_block_1))))) (seen_psi_3)))
  :effect (and (handempty) (clear ?obj) (on ?obj ?underobj) (not (clear ?underobj)) (not (holding ?obj)) (when (and (holding white_block_1) (not (= ?obj white_block_1))) (hold_0)) (when (or (= ?obj black_block_1) (and (clear black_block_1) (not (= ?underobj black_block_1)))) (seen_psi_1)) (when (or (= ?obj yellow_block_1) (and (clear yellow_block_1) (not (= ?underobj yellow_block_1)))) (hold_2)) (when (or (and (= ?obj black_block_1) (= ?underobj orange_block_1)) (on black_block_1 orange_block_1)) (seen_psi_3)) (when (not (or (= ?obj black_block_2) (and (clear black_block_2) (not (= ?underobj black_block_2))))) (hold_4)) (increase (total-cost) 1)))
 (:action unstack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (on ?obj ?underobj) (clear ?obj) (handempty) (or (not (or (= ?obj white_block_1) (holding white_block_1))) (seen_psi_1)) (or (not (or (= ?underobj yellow_block_1) (and (clear yellow_block_1) (not (= ?obj yellow_block_1))))) (seen_psi_3)))
  :effect (and (holding ?obj) (clear ?underobj) (not (on ?obj ?underobj)) (not (clear ?obj)) (not (handempty)) (when (or (= ?obj white_block_1) (holding white_block_1)) (hold_0)) (when (or (= ?underobj black_block_1) (and (clear black_block_1) (not (= ?obj black_block_1)))) (seen_psi_1)) (when (or (= ?underobj yellow_block_1) (and (clear yellow_block_1) (not (= ?obj yellow_block_1)))) (hold_2)) (when (and (on black_block_1 orange_block_1) (not (and (= ?obj black_block_1) (= ?underobj orange_block_1)))) (seen_psi_3)) (when (not (or (= ?underobj black_block_2) (and (clear black_block_2) (not (= ?obj black_block_2))))) (hold_4)) (increase (total-cost) 1)))
)
