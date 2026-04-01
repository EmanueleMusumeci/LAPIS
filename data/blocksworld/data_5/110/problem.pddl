(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   purple_block_1 brown_block_1 yellow_block_1 purple_block_2 black_block_1 - block
 )
 (:init (ontable purple_block_1) (ontable brown_block_1) (on yellow_block_1 brown_block_1) (on purple_block_2 purple_block_1) (on black_block_1 purple_block_2) (clear yellow_block_1) (clear black_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (clear purple_block_1)))
 (:constraints (sometime (ontable black_block_1)) (sometime-before (ontable black_block_1) (or (not (clear yellow_block_1)) (not (ontable brown_block_1)))) (sometime (on purple_block_2 black_block_1)) (sometime (holding brown_block_1)) (sometime (not (ontable yellow_block_1))) (sometime-after (not (ontable yellow_block_1)) (or (on brown_block_1 purple_block_2) (ontable yellow_block_1))) (sometime (not (on brown_block_1 purple_block_1))) (sometime-after (not (on brown_block_1 purple_block_1)) (holding yellow_block_1)))
 (:metric minimize (total-cost))
)
