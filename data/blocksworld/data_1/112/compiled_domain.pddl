(define (domain liftedtcore_blocksworld-domain)
 (:requirements :strips :typing :negative-preconditions :disjunctive-preconditions :equality :conditional-effects :action-costs)
 (:types block)
 (:constants
   brown_block_2 black_block_2 black_block_1 brown_block_1 - block
 )
 (:predicates (clear ?obj - block) (ontable ?obj - block) (handempty) (holding ?obj - block) (on ?obj1 - block ?obj2 - block) (hold_0) (seen_psi_1))
 (:functions (total-cost))
 (:action pickup
  :parameters ( ?obj - block)
  :precondition (and (clear ?obj) (ontable ?obj) (handempty) (or (and (clear black_block_2) (not (= ?obj black_block_2))) (seen_psi_1)))
  :effect (and (holding ?obj) (not (clear ?obj)) (not (ontable ?obj)) (not (handempty)) (when (not (and (clear black_block_2) (not (= ?obj black_block_2)))) (hold_0)) (when (or (on brown_block_1 brown_block_2) (and (clear black_block_1) (not (= ?obj black_block_1)))) (seen_psi_1)) (increase (total-cost) 1)))
 (:action putdown
  :parameters ( ?obj - block)
  :precondition (and (holding ?obj) (or (= ?obj black_block_2) (clear black_block_2) (seen_psi_1)))
  :effect (and (clear ?obj) (handempty) (ontable ?obj) (not (holding ?obj)) (when (not (or (= ?obj black_block_2) (clear black_block_2))) (hold_0)) (when (or (on brown_block_1 brown_block_2) (= ?obj black_block_1) (clear black_block_1)) (seen_psi_1)) (increase (total-cost) 1)))
 (:action stack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (clear ?underobj) (holding ?obj) (or (= ?obj black_block_2) (and (clear black_block_2) (not (= ?underobj black_block_2))) (seen_psi_1)))
  :effect (and (handempty) (clear ?obj) (on ?obj ?underobj) (not (clear ?underobj)) (not (holding ?obj)) (when (not (or (= ?obj black_block_2) (and (clear black_block_2) (not (= ?underobj black_block_2))))) (hold_0)) (when (or (and (= ?obj brown_block_1) (= ?underobj brown_block_2)) (on brown_block_1 brown_block_2) (= ?obj black_block_1) (and (clear black_block_1) (not (= ?underobj black_block_1)))) (seen_psi_1)) (increase (total-cost) 1)))
 (:action unstack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (on ?obj ?underobj) (clear ?obj) (handempty) (or (= ?underobj black_block_2) (and (clear black_block_2) (not (= ?obj black_block_2))) (seen_psi_1)))
  :effect (and (holding ?obj) (clear ?underobj) (not (on ?obj ?underobj)) (not (clear ?obj)) (not (handempty)) (when (not (or (= ?underobj black_block_2) (and (clear black_block_2) (not (= ?obj black_block_2))))) (hold_0)) (when (or (and (on brown_block_1 brown_block_2) (not (and (= ?obj brown_block_1) (= ?underobj brown_block_2)))) (= ?underobj black_block_1) (and (clear black_block_1) (not (= ?obj black_block_1)))) (seen_psi_1)) (increase (total-cost) 1)))
)
