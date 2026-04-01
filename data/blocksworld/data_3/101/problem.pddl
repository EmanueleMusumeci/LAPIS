(define (problem blocksworld-problem)
 (:domain blocksworld-domain)
 (:objects
   brown_block_1 yellow_block_1 white_block_1 grey_block_1 black_block_1 - block
 )
 (:init (ontable brown_block_1) (ontable yellow_block_1) (on white_block_1 yellow_block_1) (ontable grey_block_1) (on black_block_1 white_block_1) (clear brown_block_1) (clear grey_block_1) (clear black_block_1) (handempty) (= (total-cost) 0))
 (:goal (and (holding yellow_block_1)))
 (:constraints (sometime (not (on yellow_block_1 grey_block_1))) (sometime-after (not (on yellow_block_1 grey_block_1)) (or (not (clear black_block_1)) (not (clear white_block_1)))) (sometime (not (ontable yellow_block_1))) (sometime-before (not (ontable yellow_block_1)) (or (not (clear brown_block_1)) (not (ontable grey_block_1)))) (sometime (not (ontable grey_block_1))))
 (:metric minimize (total-cost))
)
