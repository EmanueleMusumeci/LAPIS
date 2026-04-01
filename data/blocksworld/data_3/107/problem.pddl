(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   yellow_block_1 brown_block_1 brown_block_2 purple_block_1 black_block_1 - block
 )
 (:init (ontable yellow_block_1) (ontable brown_block_1) (on brown_block_2 yellow_block_1) (on purple_block_1 brown_block_2) (ontable black_block_1) (clear brown_block_1) (clear purple_block_1) (clear black_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (on yellow_block_1 brown_block_2)))
 (:constraints (sometime (and (not (clear brown_block_1)) (not (clear black_block_1)))) (sometime (or (not (ontable brown_block_1)) (holding brown_block_1))) (always (not (ontable purple_block_1))))
 (:metric minimize (total-cost))
)
