# FLOW-MATIC Language Reference Guide

## Key Concepts

### Data Structure
- **File**: A collection of related records (e.g., inventory file, price file)
- **Record/Item**: A single entry in a file, containing multiple fields (e.g., a product entry)
- **Field**: A specific piece of data in a record (e.g., product number, quantity)

### File Organization
- Each file is assigned a single letter (A, B, C, etc.) in the program
- The current item from each file is available for processing
- Reading a file advances to the next item
- W is a special file letter reserved for working storage (temporary values)

## Running a FLOW-MATIC Program

```bash
python flowmatic.py your_program.flm
```

## Data File Format

Input/output data files should follow this format:
```
FIELD-NAME: VALUE, FIELD-NAME: VALUE, ...
```

Example:
```
PRODUCT-NO: 00009073A101, QUANTITY: 000000002543
```
- Field names must match exactly in your program and data files
- Each record is on its own line
- Fields are separated by commas
- Field names and values are separated by colons

## FLOW-MATIC Program Structure

- Programs consist of numbered operations starting with (0)
- Each operation must end with a period
- Multiple clauses can be separated by semicolons
- Operations execute sequentially unless redirected

```
(0) INPUT INVENTORY FILE-A PRICE FILE-B ; OUTPUT RESULTS FILE-C .
(1) READ-ITEM A ; IF END OF DATA GO TO OPERATION 5 .
...
(5) STOP . (END)
```

## Reference of Operations

### File Declarations (always operation 0)

```
(0) INPUT file-name FILE-letter [file-name FILE-letter...] ; 
    OUTPUT file-name FILE-letter [file-name FILE-letter...] .
```

Example:
```
(0) INPUT INVENTORY FILE-A PRICE FILE-B ; OUTPUT PRICED-INV FILE-C UNPRICED-INV FILE-D .
```

### Data Movement Operations

**READ-ITEM**: Read the next record from a file
```
(n) READ-ITEM letter [; IF END OF DATA GO TO OPERATION xx] .
```

**WRITE-ITEM**: Write the current record to an output file
```
(n) WRITE-ITEM letter .
```

**TRANSFER**: Copy an entire record from one file to another
```
(n) TRANSFER letter TO letter .
```

**MOVE**: Copy a field value from one record to another
```
(n) MOVE field-name (letter) TO field-name (letter) .
```

Example:
```
(5) MOVE PRODUCT-NO (A) TO PRODUCT-NO (C) .
(6) MOVE QUANTITY (A) TO QUANTITY (C) .
```

### Flow Control Operations

**JUMP**: Unconditionally go to a different operation
```
(n) JUMP TO OPERATION xx .
```

**COMPARE**: Compare two fields and branch accordingly
```
(n) COMPARE field-name (letter) WITH field-name (letter) ; 
    [IF GREATER GO TO OPERATION xx ;] 
    [IF EQUAL GO TO OPERATION xx ;] 
    [OTHERWISE GO TO OPERATION xx] .
```

**TEST**: Compare a field with a constant value
```
(n) TEST field-name (letter) AGAINST value ; 
    [IF EQUAL GO TO OPERATION xx ;] 
    [IF GREATER GO TO OPERATION xx ;]
    [OTHERWISE GO TO OPERATION xx] .
```

**SET**: Modify the jump destination of another operation
```
(n) SET OPERATION xx TO GO TO OPERATION yy .
```

**STOP**: End program execution (always the last operation)
```
(n) STOP . (END)
```

### File Management Operations

**REWIND**: Rewind a file to the beginning
```
(n) REWIND letter .
```

**CLOSE-OUT**: Close output files
```
(n) CLOSE-OUT FILES letter [, letter...] .
```

### Mathematical Operations

**ADD**: Add a value to a field
```
(n) ADD field-name (letter) TO field-name (letter) .
```

**SUBTRACT**: Subtract a value from a field
```
(n) SUBTRACT field-name (letter) FROM field-name (letter) .
```

**MULTIPLY**: Multiply two fields
```
(n) MULTIPLY field-name (letter) BY field-name (letter) GIVING field-name (letter) .
```

**DIVIDE**: Divide one field by another
```
(n) DIVIDE field-name (letter) BY field-name (letter) GIVING field-name (letter) .
```

## Common Program Patterns

### Initialize Variables in Working Storage
```
(1) MOVE 0 TO COUNTER (W) .
(2) MOVE "N" TO FLAG (W) .
```

### Loop Through a File
```
(3) READ-ITEM A ; IF END OF DATA GO TO OPERATION 8 .
(4) [Process the item]
(5) JUMP TO OPERATION 3 .
```

### Conditional Processing
```
(5) COMPARE STATUS-CODE (A) WITH "ACTIVE" (W) .
(6) IF EQUAL GO TO OPERATION 10 .
(7) OTHERWISE GO TO OPERATION 15 .
```

### Matching Records Between Files
```
(4) COMPARE KEY-FIELD (A) WITH KEY-FIELD (B) .
(5) IF GREATER GO TO OPERATION 12 . 
(6) IF EQUAL GO TO OPERATION 8 .
(7) OTHERWISE GO TO OPERATION 15 .
```

### Accumulating Totals
```
(8) ADD QUANTITY (A) TO TOTAL-QUANTITY (W) .
```

### Conditional End-of-Process
```
(12) TEST COUNTER (W) AGAINST 100 .
(13) IF EQUAL GO TO OPERATION 20 .
(14) OTHERWISE GO TO OPERATION 5 .
```

## Complete Program Example - Match Inventory with Prices

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

## Best Practices

1. Always include END OF DATA handling with all READ operations
2. Use descriptive field names with hyphens for readability
3. Initialize working storage fields at the beginning
4. Include meaningful comments in the original program file
5. Always CLOSE-OUT output files before ending the program
6. Test your program with small data sets first
7. Keep track of which file letters contain valid data at each step
8. Plan your operation numbering to allow for future changes
