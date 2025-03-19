# FLOW-MATIC
Python interpreter for the historic FLOW-MATIC programming language

## What is this? 

This is a simple python interpreter for the historic [FLOW-MATIC](https://en.wikipedia.org/wiki/FLOW-MATIC) programming language. It looks like this:


```
(0) INPUT INVENTORY FILE-A PRICE FILE-B ; OUTPUT PRICED-INV FILE-C UNPRICED-INV FILE-D .
(1) READ-ITEM A ; IF END OF DATA GO TO OPERATION 17 .
(2) READ-ITEM B ; IF END OF DATA GO TO OPERATION 17 .
(3) COMPARE PRODUCT-NO (A) WITH PRODUCT-NO (B) ; IF GREATER GO TO OPERATION 12 ; IF EQUAL GO TO OPERATION 7 ; OTHERWISE GO TO OPERATION 4 .
(4) TRANSFER A TO D .
(5) WRITE-ITEM D .
(6) JUMP TO OPERATION 10 .
(7) TRANSFER A TO C .
(8) MOVE UNIT-PRICE (B) TO UNIT-PRICE (C) .
(9) WRITE-ITEM C .
(10) READ-ITEM A ; IF END OF DATA GO TO OPERATION 16 .
(11) JUMP TO OPERATION 3 .
(12) READ-ITEM B ; IF END OF DATA GO TO OPERATION 14 .
(13) JUMP TO OPERATION 3 .
(14) SET OPERATION 11 TO GO TO OPERATION 4 .
(15) JUMP TO OPERATION 4 .
(16) TEST PRODUCT-NO (B) AGAINST ZZZZZZZZZZZZ ; IF EQUAL GO TO OPERATION 18 ; OTHERWISE GO TO OPERATION 17 .
(17) REWIND B .
(18) CLOSE-OUT FILES C , D .
(19) STOP . (END)
```

Most of the language defintion and functions used were gleaned from [here](http://www.bitsavers.org/pdf/univac/flow-matic/U1518_FLOW-MATIC_Programming_System_1958.pdf) - It's quite a fascinating read! 

Take a look at the reference file in this repo if you'd like to run the interpreter. Warning: ancient programming techniques lie ahead! 

What's currently missing is UNISERVO tape emulation, data definitions, and X-1 coding; And a few operations like ADD, SUBTRACT, MULTIPLY, and DIVIDE were added that were not mentioned in the manual. Perhaps this is the world's first "dialect" of FLOW-MATIC? 
