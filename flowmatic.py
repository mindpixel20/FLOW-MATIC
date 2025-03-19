import re
import time
import sys

class FileHandler:
    def __init__(self):
        self.files = {}  # Store files by their letter identifier
        self.current_items = {}  # Current item for each file
        self.output_files = {}  # Track which files are for output
        self.file_pointers = {}  # Track current position in file
        self.end_of_data = {}  # Track end of data status for each file
        self.file_names = {}  # Store the name associated with each file letter
    
    def register_file(self, letter, file_name, is_output=False):
        """Register a file with the handler"""
        self.files[letter] = []  # Initialize as empty list of records
        self.current_items[letter] = None
        self.file_pointers[letter] = 0
        self.end_of_data[letter] = False
        self.file_names[letter] = file_name  # Store the file name
        
        if is_output:
            self.output_files[letter] = []
    
    def read_item(self, file_letter):
        """Read the next item from a file"""
        if file_letter not in self.files:
            print(f"ERROR: File {file_letter} not registered")
            return False
            
        if self.file_pointers[file_letter] < len(self.files[file_letter]):
            self.current_items[file_letter] = self.files[file_letter][self.file_pointers[file_letter]]
            self.file_pointers[file_letter] += 1
            print(f"Read item from file {file_letter}: {self.current_items[file_letter]}")
            return True
        else:
            self.end_of_data[file_letter] = True
            print(f"End of data in file {file_letter}")
            return False  # End of data
    
    def get_field(self, file_letter, field_name):
        """Get a field value from the current item"""
        # Remove parentheses from the file letter if present
        file_letter = file_letter.strip('()')
        
        if file_letter not in self.current_items or self.current_items[file_letter] is None:
            print(f"ERROR: No current item for file {file_letter}")
            return None
            
        item = self.current_items[file_letter]
        if field_name not in item:
            print(f"ERROR: Field {field_name} not in current item of file {file_letter}")
            return None
            
        return item[field_name]
    
    def set_field(self, file_letter, field_name, value):
        """Set a field value in the current item"""
        # Remove parentheses from the file letter if present
        file_letter = file_letter.strip('()')
        
        if file_letter not in self.current_items or self.current_items[file_letter] is None:
            # Create a new item if one doesn't exist
            self.current_items[file_letter] = {}
            
        self.current_items[file_letter][field_name] = value
    
    def transfer_item(self, from_letter, to_letter):
        """Copy entire record from one file to another"""
        # Remove parentheses if present
        from_letter = from_letter.strip('()')
        to_letter = to_letter.strip('()')
        
        if from_letter not in self.current_items or self.current_items[from_letter] is None:
            print(f"ERROR: No current item for file {from_letter}")
            return False
            
        # Create a deep copy of the item
        self.current_items[to_letter] = self.current_items[from_letter].copy()
        print(f"Transferred item from {from_letter} to {to_letter}: {self.current_items[to_letter]}")
        return True
    
    def write_item(self, file_letter):
        """Write the current item to an output file"""
        if file_letter not in self.output_files:
            print(f"ERROR: File {file_letter} not registered as output")
            return False
            
        if file_letter not in self.current_items or self.current_items[file_letter] is None:
            print(f"ERROR: No current item for file {file_letter}")
            return False
            
        # Add the current item to the output file
        self.output_files[file_letter].append(self.current_items[file_letter].copy())
        print(f"Wrote item to file {file_letter}: {self.current_items[file_letter]}")
        return True
    
    def rewind(self, file_letter):
        """Rewind a file to the beginning"""
        if file_letter not in self.files:
            print(f"ERROR: File {file_letter} not registered")
            return False
            
        self.file_pointers[file_letter] = 0
        self.end_of_data[file_letter] = False
        self.current_items[file_letter] = None
        print(f"Rewound file {file_letter}")
        return True
    
    def close_out(self, file_letters):
        """Close output files and finalize them by writing to disk"""
        for letter in file_letters:
            letter = letter.strip()  # Remove any spaces from the letter
            
            if letter in self.output_files:
                record_count = len(self.output_files[letter])
                print(f"Closing file {letter} with {record_count} records")
                
                if letter in self.file_names:
                    # Use the file name specified in the FLOW-MATIC program
                    file_name = f"{self.file_names[letter].lower()}.dat"
                    
                    try:
                        with open(file_name, 'w') as f:
                            for record in self.output_files[letter]:
                                # Format each record as comma-separated key-value pairs
                                record_str = ', '.join([f"{key}: {value}" for key, value in record.items()])
                                f.write(record_str + '\n')
                        print(f"Wrote output file: {file_name}")
                    except Exception as e:
                        print(f"ERROR writing output file {file_name}: {e}")
                else:
                    print(f"WARNING: No file name found for letter {letter}")
    
    def load_file(self, file_letter, filename):
        """Load data from a file"""
        self.files[file_letter] = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    # Parse line into a dictionary of fields
                    record = {}
                    fields = line.strip().split(', ')
                    for field in fields:
                        if ': ' in field:
                            name, value = field.split(': ', 1)
                            record[name] = value
                        else:
                            print(f"WARNING: Malformed field in {filename}: {field}")
                    
                    # Add record to the file
                    self.files[file_letter].append(record)
            
            print(f"Loaded {len(self.files[file_letter])} records from {filename}")
            return True
        except Exception as e:
            print(f"ERROR loading file {filename}: {e}")
            return True


class FlowmaticInterpreter:
    def __init__(self):
        self.operations = {}
        self.operation_pointers = {}  # Map from operation number to target operation number
        self.current_operation_number = "0"
        self.file_handler = FileHandler()
        self.working_storage = {}  # W-storage for temporary values
        self.compare_status = "EQUAL"  # Result of the last comparison
        self.running = True
        self.debug = True  # Enable/disable debug output
        
    def debug_print(self, message):
        """Print debug messages if debugging is enabled"""
        if self.debug:
            print(message)
        
    def is_operation_number(self, token):
        """Check if a token is an operation number"""
        return bool(re.match(r'^\(\d+\)$', token))

    def parse_program(self, program_text):
        """Parse a complete FLOW-MATIC program"""
        lines = program_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                self.parse_line(line)
        
        # Initialize operation pointers
        for op_num in self.operations.keys():
            next_op = str(int(op_num) + 1)
            if next_op in self.operations:
                self.operation_pointers[op_num] = next_op
            else:
                self.operation_pointers[op_num] = None
                
        return True

    def parse_line(self, line):
        """Parse a line of FLOW-MATIC code"""
        tokens = line.split(" ")
        if not tokens:
            return None
            
        if "." not in line:
            print(f"SYNTAX ERROR - END NOT IN LINE: {line}")
            return None
            
        if not self.is_operation_number(tokens[0]):
            print(f"SYNTAX ERROR - LINE MUST BEGIN WITH OPERATION NUMBER: {line}")
            return None
            
        op_num = tokens[0].strip('()')
        self.operations[op_num] = tokens[1:]
        return True

    def extract_commands(self, tokens):
        """Extract primary commands from tokenized operation"""
        # In FLOW-MATIC, semicolons separate the main command from conditional parts
        # that should all be processed together. We need to extract the primary commands
        # but keep the conditional parts together with them.
        
        # First, join all tokens into a single string with spaces
        full_text = ' '.join(tokens)
        
        # Remove the trailing period
        if full_text.endswith('.'):
            full_text = full_text[:-1].strip()
        
        # For COMPARE and TEST operations, keep the entire string as one command
        # since we want to process all the conditional parts together
        if full_text.startswith('COMPARE') or full_text.startswith('TEST'):
            return [full_text]
        
        # For other operations, split on semicolons to get separate commands
        commands = []
        
        # Split on semicolons and keep the parts
        parts = full_text.split(';')
        for part in parts:
            part = part.strip()
            if part:  # Skip empty parts
                # Check if this is a standalone IF or OTHERWISE - these should be kept separate
                if part.startswith('IF') or part.startswith('OTHERWISE'):
                    commands.append(part)
                else:
                    commands.append(part)
        
        return commands

    def execute(self):
        """Execute the program"""
        if "0" not in self.operations:
            print("ERROR: Program must start with operation 0")
            return False
            
        self.current_operation_number = "0"
        self.running = True
        
        while self.running:
            if self.current_operation_number not in self.operations:
                print(f"ERROR: Operation {self.current_operation_number} not found")
                return False
                
            self.debug_print(f"Executing operation {self.current_operation_number}")
            tokens = self.operations[self.current_operation_number]
            commands = self.extract_commands(tokens)
            
            # Save the operation number before processing commands
            # This helps detect if a branch or jump has occurred
            original_op_num = self.current_operation_number
            
            for command in commands:
                print(f"Executing: {command}")
                result = self.process_command(command)
                if result < 0:
                    print(f"ERROR in operation ({original_op_num}): {command}")
                    return False
                
                # If the operation number changed, a branch or jump occurred
                # So don't continue processing commands from this operation
                if self.current_operation_number != original_op_num:
                    self.debug_print(f"Branched from operation {original_op_num} to {self.current_operation_number}")
                    break
                        
            # Move to next operation if not redirected (i.e., if no branch/jump occurred)
            if self.running and self.current_operation_number == original_op_num:
                if self.current_operation_number in self.operation_pointers:
                    next_op = self.operation_pointers[self.current_operation_number]
                    if next_op is None:
                        print(f"End of program reached after operation {self.current_operation_number}")
                        self.running = False
                    else:
                        self.current_operation_number = next_op
                else:
                    print(f"No next operation defined after {self.current_operation_number}")
                    self.running = False
            time.sleep(0.01) # VERY rough estimation of UNIVAC II speeds 
        return True

    def process_command(self, command):
        """Process a FLOW-MATIC command"""
        if not command:
            return 0
            
        # Split the command into words for processing
        words = command.split()
        if not words:
            return 0
            
        # Get the primary command type (first word)
        command_type = words[0]
        
        # Handle each command type
        if command_type == "INPUT":
            return self.input_file(command)
        elif command_type == "OUTPUT":
            return self.output_file(command)
        elif command_type == "COMPARE":
            return self.compare(command)
        elif command_type == "READ-ITEM":
            return self.read_item(command)
        elif command_type == "WRITE-ITEM":
            return self.write_item(command)
        elif command_type == "TRANSFER":
            return self.transfer(command)
        elif command_type == "MOVE":
            return self.move(command)
        elif command_type == "JUMP":
            return self.jump(command)
        elif command_type == "STOP":
            return self.stop(command)
        elif command_type == "TEST":
            return self.test(command)
        elif command_type == "SET":
            return self.set(command)
        elif command_type == "REWIND":
            return self.rewind(command)
        elif command_type == "CLOSE-OUT":
            return self.close_out(command)
        elif command_type == "ADD":
            return self.add(command)
        elif command_type == "SUBTRACT":
            return self.subtract(command)
        elif command_type == "MULTIPLY":
            return self.multiply(command)
        elif command_type == "DIVIDE":
            return self.divide(command)
        elif command_type == "IF":
            return self.process_conditional(command)
        # This is the important part: ignore "OTHERWISE" as it should be
        # handled within the COMPARE or TEST operations
        elif command_type == "OTHERWISE":
            self.debug_print(f"Ignoring standalone 'OTHERWISE' - it should be handled by COMPARE/TEST: {command}")
            return 0
        else:
            print(f"UNKNOWN COMMAND: {command} --- HALTED.")
            self.running = False
            return -1

    def process_conditional(self, command):
        """Process standalone conditional statements"""
        # This handles IF statements that are their own commands (not part of COMPARE/TEST)
        if "END OF DATA" in command:
            # Example: IF END OF DATA GO TO OPERATION 14
            match = re.search(r'GO TO OPERATION (\d+)', command)
            if match:
                for file_letter in self.file_handler.end_of_data:
                    if self.file_handler.end_of_data[file_letter]:
                        target_op = match.group(1)
                        self.debug_print(f"Conditional branch to operation {target_op} (END OF DATA)")
                        self.current_operation_number = target_op
                        return 0
            return 0
            
        elif "GREATER" in command:
            # Example: IF GREATER GO TO OPERATION 10
            match = re.search(r'GO TO OPERATION (\d+)', command)
            if match and self.compare_status == "GREATER":
                target_op = match.group(1)
                self.debug_print(f"Conditional branch to operation {target_op} (GREATER)")
                self.current_operation_number = target_op
            return 0
            
        elif "EQUAL" in command:
            # Example: IF EQUAL GO TO OPERATION 5
            match = re.search(r'GO TO OPERATION (\d+)', command)
            if match and self.compare_status == "EQUAL":
                target_op = match.group(1)
                self.debug_print(f"Conditional branch to operation {target_op} (EQUAL)")
                self.current_operation_number = target_op
            return 0
            
        elif "LESS" in command or "OTHERWISE" in command:
            # Example: OTHERWISE GO TO OPERATION 2
            match = re.search(r'GO TO OPERATION (\d+)', command)
            if match:
                if "OTHERWISE" in command or self.compare_status == "LESS":
                    target_op = match.group(1)
                    self.debug_print(f"Conditional branch to operation {target_op} (OTHERWISE/LESS)")
                    self.current_operation_number = target_op
            return 0
            
        print(f"MALFORMED CONDITIONAL: {command}")
        return -1

    def jump(self, command):
        """Handle JUMP operation"""
        # Example: JUMP TO OPERATION 8
        match = re.search(r'JUMP TO OPERATION (\d+)', command)
        if not match:
            print(f"SYNTAX ERROR in JUMP: {command}")
            return -1
            
        jump_op = match.group(1)
        if jump_op not in self.operations:
            print(f"ERROR: OPERATION {jump_op} NOT IN OPERATIONS.")
            return -1 
            
        self.debug_print(f"Jumping to operation {jump_op}")
        self.current_operation_number = jump_op
        return 0

    def input_file(self, command):
        """Handle INPUT operation"""
        # Example: INPUT INVENTORY FILE-A PRICE FILE-B
        parts = command.split()
        i = 1  # Skip "INPUT"
        
        while i < len(parts) and parts[i] != ";":
            if i >= len(parts):
                break
                
            file_name = parts[i]
            i += 1
            
            if i >= len(parts) or parts[i] == ";":
                print(f"SYNTAX ERROR in INPUT: Missing FILE- specification")
                return -1
                
            file_spec = parts[i]
            i += 1
            
            if not file_spec.startswith("FILE-"):
                print(f"SYNTAX ERROR in INPUT: Expected FILE- but got {file_spec}")
                return -1
                
            file_letter = file_spec[5:]
            self.file_handler.register_file(file_letter, file_name)
            
            # In a real implementation, load data from a file
            data_file = f"{file_name.lower()}.dat"
            self.file_handler.load_file(file_letter, data_file)
            
        return 0

    def output_file(self, command):
        """Handle OUTPUT portion of INPUT operation"""
        # Example: OUTPUT PRICED-INV FILE-C UNPRICED-INV FILE-D ; HSP D .
        parts = command.split()
        i = 1  # Skip "OUTPUT"
        
        while i < len(parts) and parts[i] != ";" and parts[i] != ".":
            if i >= len(parts):
                break
                
            file_name = parts[i]
            i += 1
            
            if i >= len(parts) or parts[i] == ";" or parts[i] == ".":
                print(f"SYNTAX ERROR in OUTPUT: Missing FILE- specification")
                return -1
                
            file_spec = parts[i]
            i += 1
            
            if not file_spec.startswith("FILE-"):
                print(f"SYNTAX ERROR in OUTPUT: Expected FILE- but got {file_spec}")
                return -1
                
            file_letter = file_spec[5:]
            self.file_handler.register_file(file_letter, file_name, is_output=True)
            
        # Check for HSP (High Speed Printer) specification
        if i < len(parts) and parts[i] == ";":
            i += 1
            if i < len(parts) and parts[i] == "HSP":
                i += 1
                if i < len(parts):
                    printer_file = parts[i]
                    self.debug_print(f"File {printer_file} marked for High Speed Printer output")
                    
        return 0

    def transfer(self, command):
        """Handle TRANSFER operation"""
        # Example: TRANSFER A TO D
        match = re.search(r'TRANSFER (\w+) TO (\w+)', command)
        if not match:
            print(f"SYNTAX ERROR in TRANSFER: {command}")
            return -1
            
        from_file = match.group(1)
        to_file = match.group(2)
        
        if not self.file_handler.transfer_item(from_file, to_file):
            return -1
            
        return 0

    def compare(self, command):
        """Handle COMPARE operation"""
        # Example: COMPARE PRODUCT-NO (A) WITH PRODUCT-NO (B) ; IF GREATER GO TO OPERATION 10 ; IF EQUAL GO TO OPERATION 5 ; OTHERWISE GO TO OPERATION 2
        
        # First, extract the field comparison part
        match = re.search(r'COMPARE (\S+) \((\w+)\) WITH (\S+) \((\w+)\)', command)
        if not match:
            print(f"SYNTAX ERROR in COMPARE: {command}")
            return -1
            
        field1 = match.group(1)
        file1 = match.group(2)
        field2 = match.group(3)
        file2 = match.group(4)
        
        val1 = self.file_handler.get_field(file1, field1)
        val2 = self.file_handler.get_field(file2, field2)
        
        if val1 is None or val2 is None:
            return -1
            
        self.debug_print(f"Comparing {val1} with {val2}")
        
        if val1 > val2:
            self.compare_status = "GREATER"
        elif val1 == val2:
            self.compare_status = "EQUAL"
        else:
            self.compare_status = "LESS"
            
        # Now process the conditional branching parts
        if "IF GREATER GO TO OPERATION" in command:
            match = re.search(r'IF GREATER GO TO OPERATION (\d+)', command)
            if match and self.compare_status == "GREATER":
                target_op = match.group(1)
                self.debug_print(f"Branching to operation {target_op} (GREATER)")
                self.current_operation_number = target_op
                return 0
                
        if "IF EQUAL GO TO OPERATION" in command:
            match = re.search(r'IF EQUAL GO TO OPERATION (\d+)', command)
            if match and self.compare_status == "EQUAL":
                target_op = match.group(1)
                self.debug_print(f"Branching to operation {target_op} (EQUAL)")
                self.current_operation_number = target_op
                return 0
                
        if "OTHERWISE GO TO OPERATION" in command:
            match = re.search(r'OTHERWISE GO TO OPERATION (\d+)', command)
            if match:
                target_op = match.group(1)
                self.debug_print(f"Branching to operation {target_op} (OTHERWISE)")
                self.current_operation_number = target_op
                return 0
                
        return 0

    def read_item(self, command):
        """Handle READ-ITEM operation"""
        # Example: READ-ITEM A ; IF END OF DATA GO TO OPERATION 14
        match = re.search(r'READ-ITEM (\w+)', command)
        if not match:
            print(f"SYNTAX ERROR in READ-ITEM: {command}")
            return -1
            
        file_letter = match.group(1)
        success = self.file_handler.read_item(file_letter)
        
        # Process END OF DATA condition if present in command
        if not success and "END OF DATA" in command:
            match = re.search(r'IF END OF DATA GO TO OPERATION (\d+)', command)
            if match:
                target_op = match.group(1)
                self.debug_print(f"End of data, branching to operation {target_op}")
                self.current_operation_number = target_op
                
        return 0

    def write_item(self, command):
        """Handle WRITE-ITEM operation"""
        # Example: WRITE-ITEM D
        match = re.search(r'WRITE-ITEM (\w+)', command)
        if not match:
            print(f"SYNTAX ERROR in WRITE-ITEM: {command}")
            return -1
            
        file_letter = match.group(1)
        if not self.file_handler.write_item(file_letter):
            return -1
            
        return 0

    def stop(self, command):
        """Handle STOP operation"""
        # Example: STOP . (END)
        self.running = False
        print("Program execution stopped")
        return 0

    def test(self, command):
        """Handle TEST operation"""
        # Example: TEST PRODUCT-NO (B) AGAINST ZZZZZZZZZZZZ ; IF EQUAL GO TO OPERATION 16 ; OTHERWISE GO TO OPERATION 15
        
        # Extract the field and test value
        match = re.search(r'TEST (\S+) \((\w+)\) AGAINST (\S+)', command)
        if not match:
            print(f"SYNTAX ERROR in TEST: {command}")
            return -1
            
        field = match.group(1)
        file_letter = match.group(2)
        test_value = match.group(3)
        
        field_value = self.file_handler.get_field(file_letter, field)
        if field_value is None:
            return -1
            
        self.debug_print(f"Testing {field_value} against {test_value}")
        
        # Process conditions and branch accordingly
        if "IF EQUAL GO TO OPERATION" in command and field_value == test_value:
            match = re.search(r'IF EQUAL GO TO OPERATION (\d+)', command)
            if match:
                target_op = match.group(1)
                self.debug_print(f"Test equal, branching to operation {target_op}")
                self.current_operation_number = target_op
                return 0
                
        if "IF GREATER GO TO OPERATION" in command and field_value > test_value:
            match = re.search(r'IF GREATER GO TO OPERATION (\d+)', command)
            if match:
                target_op = match.group(1)
                self.debug_print(f"Test greater, branching to operation {target_op}")
                self.current_operation_number = target_op
                return 0
                
        if "IF LESS GO TO OPERATION" in command and field_value < test_value:
            match = re.search(r'IF LESS GO TO OPERATION (\d+)', command)
            if match:
                target_op = match.group(1)
                self.debug_print(f"Test less, branching to operation {target_op}")
                self.current_operation_number = target_op
                return 0
                
        if "OTHERWISE GO TO OPERATION" in command:
            match = re.search(r'OTHERWISE GO TO OPERATION (\d+)', command)
            if match:
                target_op = match.group(1)
                self.debug_print(f"Test otherwise, branching to operation {target_op}")
                self.current_operation_number = target_op
                return 0
                
        return 0

    def set(self, command):
        """Handle SET operation"""
        # Example: SET OPERATION 9 TO GO TO OPERATION 2
        match = re.search(r'SET OPERATION (\d+) TO GO TO OPERATION (\d+)', command)
        if not match:
            print(f"SYNTAX ERROR in SET: {command}")
            return -1
            
        from_op = match.group(1)
        to_op = match.group(2)
        
        if from_op not in self.operations:
            print(f"ERROR: OPERATION {from_op} NOT IN OPERATIONS.")
            return -1
            
        if to_op not in self.operations:
            print(f"ERROR: OPERATION {to_op} NOT IN OPERATIONS.")
            return -1
            
        self.debug_print(f"Setting operation {from_op} to go to operation {to_op}")
        self.operation_pointers[from_op] = to_op
        return 0

    def move(self, command):
        """Handle MOVE operation"""
        # Example: MOVE UNIT-PRICE (B) TO UNIT-PRICE (C)
        match = re.search(r'MOVE (\S+) \((\w+)\) TO (\S+) \((\w+)\)', command)
        if not match:
            print(f"SYNTAX ERROR in MOVE: {command}")
            return -1
            
        field1 = match.group(1)
        file1 = match.group(2)
        field2 = match.group(3)
        file2 = match.group(4)
        
        value = self.file_handler.get_field(file1, field1)
        if value is None:
            return -1
            
        self.debug_print(f"Moving value {value} from {field1}({file1}) to {field2}({file2})")
        self.file_handler.set_field(file2, field2, value)
        return 0

    def rewind(self, command):
        """Handle REWIND operation"""
        # Example: REWIND B
        match = re.search(r'REWIND (\w+)', command)
        if not match:
            print(f"SYNTAX ERROR in REWIND: {command}")
            return -1
            
        file_letter = match.group(1)
        if not self.file_handler.rewind(file_letter):
            return -1
            
        return 0

    def close_out(self, command):
        """Handle CLOSE-OUT operation"""
        # Example: CLOSE-OUT FILES C , D
        match = re.search(r'CLOSE-OUT FILES? ([\w ,]+)', command)
        if not match:
            print(f"SYNTAX ERROR in CLOSE-OUT: {command}")
            return -1
            
        file_list = match.group(1)
        file_letters = [letter.strip() for letter in file_list.split(',')]
        
        self.file_handler.close_out(file_letters)
        return 0

    def add(self, command):
        """Handle ADD operation"""
        # Example: ADD QUANTITY (A) TO STORED QUANTITY (W)
        match = re.search(r'ADD (\S+) \((\w+)\) TO (\S+) \((\w+)\)', command)
        if not match:
            print(f"SYNTAX ERROR in ADD: {command}")
            return -1
            
        field1 = match.group(1)
        file1 = match.group(2)
        field2 = match.group(3)
        file2 = match.group(4)
        
        val1 = self.file_handler.get_field(file1, field1)
        val2 = self.file_handler.get_field(file2, field2)
        
        if val1 is None or val2 is None:
            return -1
            
        # Convert to numbers for addition
        try:
            result = float(val1) + float(val2)
            # Convert back to same format as original
            if '.' not in val2:
                result = int(result)
            self.debug_print(f"Adding {val1} to {val2}, result: {result}")
            self.file_handler.set_field(file2, field2, str(result))
            return 0
        except ValueError:
            print(f"ERROR: Cannot convert values to numbers for addition: {val1}, {val2}")
            return -1

    def subtract(self, command):
        """Handle SUBTRACT operation"""
        # Example: SUBTRACT X (A) FROM Y (B)
        match = re.search(r'SUBTRACT (\S+) \((\w+)\) FROM (\S+) \((\w+)\)', command)
        if not match:
            print(f"SYNTAX ERROR in SUBTRACT: {command}")
            return -1
            
        field1 = match.group(1)
        file1 = match.group(2)
        field2 = match.group(3)
        file2 = match.group(4)
        
        val1 = self.file_handler.get_field(file1, field1)
        val2 = self.file_handler.get_field(file2, field2)
        
        if val1 is None or val2 is None:
            return -1
            
        try:
            result = float(val2) - float(val1)
            if '.' not in val2:
                result = int(result)
            self.debug_print(f"Subtracting {val1} from {val2}, result: {result}")
            self.file_handler.set_field(file2, field2, str(result))
            return 0

        except ValueError:
            print(f"ERROR: Cannot convert values to numbers for multiplication: {val1}, {val2}")
            return -1

    def multiply(self, command):
        """Handle MULTIPLY operation"""
        # Example: MULTIPLY QUANTITY (C) BY UNIT-PRICE (C) GIVING EXTENDED-PRICE (C)
        match = re.search(r'MULTIPLY (\S+) \((\w+)\) BY (\S+) \((\w+)\) GIVING (\S+) \((\w+)\)', command)
        if not match:
            print(f"SYNTAX ERROR in MULTIPLY: {command}")
            return -1
            
        field1 = match.group(1)
        file1 = match.group(2)
        field2 = match.group(3)
        file2 = match.group(4)
        result_field = match.group(5)
        result_file = match.group(6)
        
        val1 = self.file_handler.get_field(file1, field1)
        val2 = self.file_handler.get_field(file2, field2)
        
        if val1 is None or val2 is None:
            return -1
            
        try:
            result = float(val1) * float(val2)
            # Format result based on inputs
            if '.' not in val1 and '.' not in val2:
                result = int(result)
            self.file_handler.set_field(result_file, result_field, str(result))
            return 0
        except ValueError:
            print(f"ERROR: Cannot convert values to numbers for multiplication: {val1}, {val2}")
            return -1

    def divide(self, command):
        """Handle DIVIDE operation"""
        # Example: DIVIDE TOTAL (A) BY COUNT (A) GIVING AVERAGE (A)
        match = re.search(r'DIVIDE (\S+) \((\w+)\) BY (\S+) \((\w+)\) GIVING (\S+) \((\w+)\)', command)
        if not match:
            print(f"SYNTAX ERROR in DIVIDE: {command}")
            return -1
            
        field1 = match.group(1)
        file1 = match.group(2)
        field2 = match.group(3)
        file2 = match.group(4)
        result_field = match.group(5)
        result_file = match.group(6)
        
        val1 = self.file_handler.get_field(file1, field1)
        val2 = self.file_handler.get_field(file2, field2)
        
        if val1 is None or val2 is None:
            return -1
            
        try:
            divisor = float(val2)
            if divisor == 0:
                print("ERROR: Division by zero")
                return -1
                
            result = float(val1) / divisor
            self.file_handler.set_field(result_file, result_field, str(result))
            return 0
        except ValueError:
            print(f"ERROR: Cannot convert values to numbers for division: {val1}, {val2}")
            return -1

if __name__ == "__main__":
    # Check if file path was provided
    if len(sys.argv) < 2:
        print("Usage: python flowmatic.py <program_file>")
        sys.exit(1)
    
    # Get program file path
    program_file = sys.argv[1]
    
    # Load program from file
    try:
        with open(program_file, 'r') as f:
            program_text = f.read()
        print(f"Loaded program from {program_file}")
    except Exception as e:
        print(f"Error loading program: {e}")
        sys.exit(1)
    
    # Create interpreter and run program
    interpreter = FlowmaticInterpreter()
    interpreter.parse_program(program_text)
    interpreter.execute()
