import os
import pytest
import cocotb.runner

class Cocotb_Runner():
    def __init__(self):
        self.test_groups: list[str] = ["spi"]
        self.ghdl = cocotb.runner.Ghdl()

    @staticmethod
    def find_test_files(directory):
        """Finds all files starting with 'test_' in the given directory and its subdirectories."""
        test_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.startswith("test_") and file.endswith((".py", ".vhd")):
                    test_files.append(os.path.join(root, file))
        return test_files

    @staticmethod
    def find_cocotb_tests(file_path):
        """Finds functions decorated with @cocotb.test() in the given Python file."""
        tests = []
        with open(file_path, "r") as f:
            for line in f:
                # Check if the line contains the decorator, even without parentheses
                if "@cocotb.test" in line:
                    # Find the next line that starts with "async def" for cocotb tests
                    while True:
                        try:
                            next_line = next(f)
                            if next_line.strip().startswith("async def"):
                                function_name = next_line.split("async def")[1].split("(")[0].strip()
                                tests.append(function_name)
                                break
                        except StopIteration:
                            # Reached end of file without finding "async def"
                            break
        return tests
    
    def print_available_test_groups(self):
        print("\nTest groups:")
        for i, group in enumerate(self.test_groups):
                print(f"{i+1}: {group}")

    def get_user_choice(self, prompt, options, allow_all=False, add_q_to_quit=True):
        """Gets user choice with input validation and handling for 'q', 'all', and 'b'.

        Args:
            prompt (str): The prompt to display to the user.
            options (list): A list of available options.
            allow_all (bool, optional): Whether to allow 'a' for selecting all options. 
                                        Defaults to False.
            add_q_to_quit (bool, optional): Whether to add "(q to quit)" to the prompt.
                                            Defaults to True.

        Returns:
            Union[int, str, None]: Returns the index of the chosen option, 'q' for quit, 
                                    'a' for all (if allowed), 'b' for back, or None for invalid input.
        """
        while True:
            choice = input(f"{prompt}{' (q to quit)' if add_q_to_quit else ''} ")
            if choice.lower() == 'q':
                return 'q'
            elif allow_all and choice.lower() == 'a':
                return 'a'
            elif choice.lower() == 'b':  # Handle 'b' for back
                return 'b'
            try:
                choice = int(choice) - 1
                if 0 <= choice < len(options):
                    return choice
                else:
                    print("Invalid input. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def main(self):
        """Main function to search for test files and cocotb tests."""
        current_dir = os.getcwd()

        while True:  # Outer loop for test group selection
            # Selecting test group
            self.print_available_test_groups()
            group_choice = self.get_user_choice("Enter the number corresponding to the desired test group", 
                                                self.test_groups)
            if group_choice == 'q':
                exit(code=0)
            elif isinstance(group_choice, int):
                test_group_dir = os.path.join(current_dir, self.test_groups[group_choice])
                test_group_dir_name = os.path.basename(test_group_dir)
                if os.path.exists(test_group_dir):
                    test_files = self.find_test_files(test_group_dir)
                    if test_files:
                        tests_available = any(self.find_cocotb_tests(file) for file in test_files)
                        if tests_available:
                            # Selecting test suite
                            while True:  # Inner loop for test suite and test selection
                                print(f"\nTest suites in {test_group_dir_name}:")
                                for i, file in enumerate(test_files):
                                    file_name = os.path.basename(file)
                                    file_name = file_name.replace("test_", "").replace(".py", "")
                                    cocotb_tests = self.find_cocotb_tests(file)
                                    test_indicator = "(NO TESTS)" if not cocotb_tests else ""
                                    print(f"{i+1}. {file_name} {test_indicator}")

                                suite_choice = self.get_user_choice("Enter the number corresponding to the desired test suite to run (b for back)",
                                                                    test_files)
                                if suite_choice == 'q':
                                    return
                                elif suite_choice == 'b':
                                    break  # Go back to test group selection
                                elif isinstance(suite_choice, int):
                                    selected_file = test_files[suite_choice]
                                    selected_file_name = os.path.basename(selected_file)
                                    selected_file_name = selected_file_name.replace("test_", "").replace(".py", "")
                                    cocotb_tests = self.find_cocotb_tests(selected_file)

                                    # Selecting test(s) within a suite
                                    while True:
                                        if not cocotb_tests:
                                            print(f"No tests found in {selected_file_name}.")
                                            break  # Go back to test suite selection
                                        print(f"\nTests in {selected_file_name}:")
                                        for i, test in enumerate(cocotb_tests):
                                            print(f"{i+1}. {test}")
                                        test_choice = self.get_user_choice("Enter the number of the test to run (a for all, b for back, q to quit)",
                                                                            cocotb_tests, allow_all=True, add_q_to_quit=False)
                                        if test_choice == 'q':
                                            return
                                        elif test_choice == 'b':
                                            break  # Go back to test list
                                        elif test_choice == 'a':
                                            print(f"Running all tests in {selected_file_name}...")
                                            # TODO: Add logic to run all tests in the selected file
                                            break
                                        elif isinstance(test_choice, int):
                                            selected_test = cocotb_tests[test_choice]
                                            print(f"Running test: {selected_test}")
                                            # TODO: Add logic to run the selected test
                                            break
                                        else:
                                            print("Invalid input. Please enter a valid number.")
                                else:
                                    print("Invalid input. Please enter a valid number.")
                        else:
                            print(f"\nNO TESTS FOUND IN: {test_group_dir_name}")
                    else:
                        print(f"No test suites found in {test_group_dir}.")
                else:
                    print(f"Test group directory {test_group_dir} does not exist.")
            else:
                print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    cocotb_runner = Cocotb_Runner()
    cocotb_runner.main()
