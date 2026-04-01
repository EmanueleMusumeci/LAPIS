(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
   yellow_block_1 yellow_block_2 - block
 )
 (:init (ontable red_block_1) (ontable yellow_block_1) (ontable yellow_block_2) (on purple_block_1 red_block_1) (ontable grey_block_1) (clear yellow_block_1) (clear yellow_block_2) (clear purple_block_1) (clear grey_block_1) (handempty) (hold_1) (= (total-cost) 0))
 (:goal (and (on yellow_block_2 purple_block_1) (hold_0) (hold_1) (hold_2)))
 (:metric minimize (total-cost))
)
