(define (domain liftedtcore_blocksworld-domain)
 (:requirements :strips :typing :negative-preconditions :disjunctive-preconditions :equality :conditional-effects :action-costs)
 (:types block)
 (:constants
   white_block_1 green_block_2 grey_block_1 - block
 )
 (:predicates (clear ?obj - block) (ontable ?obj - block) (handempty) (holding ?obj - block) (on ?obj1 - block ?obj2 - block) (hold_0) (hold_1) (hold_2))
 (:functions (total-cost))
 (:action pickup
  :parameters ( ?obj - block)
  :precondition (and (clear ?obj) (ontable ?obj) (handempty))
  :effect (and (holding ?obj) (not (clear ?obj)) (not (ontable ?obj)) (not (handempty)) (when (and (ontable white_block_1) (not (= ?obj white_block_1))) (hold_1)) (when (and (ontable white_block_1) (not (= ?obj white_block_1)) (not (or (on white_block_1 green_block_2) (not (and (clear green_block_2) (not (= ?obj green_block_2))))))) (not (hold_2))) (when (or (on white_block_1 green_block_2) (not (and (clear green_block_2) (not (= ?obj green_block_2))))) (hold_2)) (increase (total-cost) 1)))
 (:action putdown
  :parameters ( ?obj - block)
  :precondition (and (holding ?obj))
  :effect (and (clear ?obj) (handempty) (ontable ?obj) (not (holding ?obj)) (when (or (= ?obj white_block_1) (ontable white_block_1)) (hold_1)) (when (and (or (= ?obj white_block_1) (ontable white_block_1)) (not (or (on white_block_1 green_block_2) (not (or (= ?obj green_block_2) (clear green_block_2)))))) (not (hold_2))) (when (or (on white_block_1 green_block_2) (not (or (= ?obj green_block_2) (clear green_block_2)))) (hold_2)) (increase (total-cost) 1)))
 (:action stack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (clear ?underobj) (holding ?obj))
  :effect (and (handempty) (clear ?obj) (on ?obj ?underobj) (not (clear ?underobj)) (not (holding ?obj)) (when (or (and (= ?obj grey_block_1) (= ?underobj white_block_1)) (on grey_block_1 white_block_1)) (hold_0)) (when (and (ontable white_block_1) (not (or (and (= ?obj white_block_1) (= ?underobj green_block_2)) (on white_block_1 green_block_2) (not (or (= ?obj green_block_2) (and (clear green_block_2) (not (= ?underobj green_block_2)))))))) (not (hold_2))) (when (or (and (= ?obj white_block_1) (= ?underobj green_block_2)) (on white_block_1 green_block_2) (not (or (= ?obj green_block_2) (and (clear green_block_2) (not (= ?underobj green_block_2)))))) (hold_2)) (increase (total-cost) 1)))
 (:action unstack
  :parameters ( ?obj - block ?underobj - block)
  :precondition (and (on ?obj ?underobj) (clear ?obj) (handempty))
  :effect (and (holding ?obj) (clear ?underobj) (not (on ?obj ?underobj)) (not (clear ?obj)) (not (handempty)) (when (and (on grey_block_1 white_block_1) (not (and (= ?obj grey_block_1) (= ?underobj white_block_1)))) (hold_0)) (when (and (ontable white_block_1) (not (or (and (on white_block_1 green_block_2) (not (and (= ?obj white_block_1) (= ?underobj green_block_2)))) (not (or (= ?underobj green_block_2) (and (clear green_block_2) (not (= ?obj green_block_2)))))))) (not (hold_2))) (when (or (and (on white_block_1 green_block_2) (not (and (= ?obj white_block_1) (= ?underobj green_block_2)))) (not (or (= ?underobj green_block_2) (and (clear green_block_2) (not (= ?obj green_block_2)))))) (hold_2)) (increase (total-cost) 1)))
)
