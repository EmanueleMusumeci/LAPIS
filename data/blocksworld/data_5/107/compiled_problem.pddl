(define (problem liftedtcore_blocksworld-problem)
 (:domain liftedtcore_blocksworld-domain)
 (:objects
 )
 (:init (ontable yellow_block_1) (ontable brown_block_1) (on brown_block_2 yellow_block_1) (on purple_block_1 brown_block_2) (ontable black_block_1) (clear brown_block_1) (clear purple_block_1) (clear black_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (on yellow_block_1 brown_block_2) (hold_0) (hold_1) (hold_2) (hold_4)))
 (:metric minimize (total-cost))
)
