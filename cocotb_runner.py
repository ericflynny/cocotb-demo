import os
import pytest
import cocotb.runner

class Cocotb_Runner():
    def __init__(self):
        self.ghdl = cocotb.runner.Ghdl()
        # Top level file must be first for build
        cwd = os.getcwd()
        # Dictionary format -> Testbench name: (List of source files, Top level entity name)
        self.Source_Files = {
            # Testbench name
            "spi":  (
                    # Source files
                    [f"{os.path.join(cwd, 'vhdl', 'spi', 'spi_slave.vhd')}",
                    f"{os.path.join(cwd, 'vhdl', 'spi', 'spi_master.vhd')}",
                    f"{os.path.join(cwd, 'vhdl', 'spi', 'spi_top_level.vhd')}"
                    ],
                    # Top level entity name
                    "spi_top_level")
        }

    @staticmethod
    def find_test_files(directory: str):
        """Finds all python files starting with 'test_' in the given directory and its subdirectories."""
        test_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(root, file))
        return test_files

    @staticmethod
    def find_cocotb_tests(file_path: str):
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
    
    def print_available_testbenches(self):
        print("\nTestbenches:")
        for index, testgroup in enumerate(self.Source_Files.keys()):
            print(f"{index+1}: {testgroup}")

    def get_user_choice(self, prompt: str, options: list, allow_all=False, allow_back=False):
        """Gets user choice with input validation and handling for 'q', 'all', and 'b'.

        Args:
            prompt (str): The prompt to display to the user.
            options (list): A list of available options.
            allow_all (bool, optional): Whether to allow 'a' for selecting all options. 
                                        Defaults to False.
            allow_back (bool, optional): Whether to allow 'b' for going back.
                                        Defaults to False.

        Returns:
            Union[int, str, None]: Returns the index of the chosen option, 'q' for quit, 
                                    'a' for all (if allowed), 'b' for back (if allowed), 
                                    or None for invalid input.
        """
        while True:
            choice = input(f"{prompt} (q to quit): ")
            if choice.lower() == 'q':
                return 'q'
            elif allow_all and choice.lower() == 'a':
                return 'a'
            elif allow_back and choice.lower() == 'b':
                return 'b'
            try:
                choice = int(choice) - 1
                if 0 <= choice < len(options):
                    return choice
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")


    def run_tests(self, group: str, test_module: str, selected_testcases: list[str], top_level: str):
        testcase_string = " ".join(selected_testcases)

        try:
            self.ghdl.test(test_module=f"tests.{group}.test_{test_module}",
                            testcase=testcase_string,
                            hdl_toplevel=self.Source_Files[group][1],
                            waves=True,
                            gui=False,
                            plusargs=[f"--wave={group}_wave.ghw"],
                            build_dir=f"{group}_build",
                            log_file=f"{group}_test.log"
                            )
        except Exception as e:
            print(f"Unable to run tests: {e}")

    def build(self, group: str):
        try:
            self.ghdl.build(vhdl_sources=self.Source_Files[group][0],
                            hdl_toplevel=self.Source_Files[group][1],
                            build_dir=f"{group}_build",
                            clean=True,
                            log_file=f"{group}_build.log")
        except Exception as e:
            print(f"Unable to build {group}: {e}")

        print(f"Successfully built {group}\n")

    def main(self):
        """Main function to search for test files and cocotb tests."""
        current_dir = os.getcwd()

        while True:
            # Prompt user to select a testbench
            self.print_available_testbenches()
            testbench_choice = self.get_user_choice("Select a testbench (q to quit)", self.Source_Files.keys())
            try:
                testbench_name = list(self.Source_Files.keys())[testbench_choice]
            except TypeError:
                raise ValueError(f"Invalid choice {testbench_choice}. Please enter a valid number.")
            
            # Exit if desired
            if testbench_name == 'q':
                exit(code=0)

            else:
                # Verify testbench exists
                testbench_path = os.path.join(current_dir, f"testbench_{testbench_name}.py")
                if os.path.exists(testbench_path): 
                    # Verify test files/suites exist for corresponding testbench
                    test_files_dir = os.path.join(current_dir, "tests", testbench_name)
                    test_files = self.find_test_files(test_files_dir)
                    if test_files:
                        # Find available tests within desired test file/suite to verify there are valid tests
                        tests_available = any(self.find_cocotb_tests(file) for file in test_files)
                        if tests_available:
                            while True:
                                # Output available test suites
                                print(f"\nTest suites in {testbench_name}:")
                                for i, file in enumerate(test_files):
                                    test_suite_name = os.path.basename(file).replace("test_", "").replace(".py", "")
                                    cocotb_tests = self.find_cocotb_tests(file)
                                    test_indicator = " (NO TESTS)" if not cocotb_tests else ""
                                    print(f"{i+1}. {test_suite_name}{test_indicator}")

                                # Get desired suite from user
                                suite_choice = self.get_user_choice("Select a test suite (b for back)", 
                                                                    test_files, allow_back=True)
                                if suite_choice == 'q':
                                    return
                                elif suite_choice == 'b':
                                    break

                                elif isinstance(suite_choice, int):
                                    # Setup test file name for cocotb
                                    selected_test_file = test_files[suite_choice]
                                    selected_test_file_name_stripped = os.path.basename(selected_test_file).replace("test_", "").replace(".py", "")

                                    # Find tests within test suite
                                    cocotb_tests = self.find_cocotb_tests(selected_test_file)

                                    while True:
                                        if not cocotb_tests:
                                            print(f"No tests found in {selected_test_file_name_stripped}.")
                                            break
                                        # Prompt user to select tests to run
                                        print(f"\nTests in {selected_test_file_name_stripped}:")
                                        for i, test in enumerate(cocotb_tests):
                                            print(f"{i+1}. {test}")
                                        test_choice = self.get_user_choice("Select a test (a for all, b for back)",
                                                                            cocotb_tests, allow_all=True, allow_back=True)
                                        if test_choice == 'q':
                                            return
                                        elif test_choice == 'b':
                                            break
                                        # Build and run all tests
                                        elif test_choice == 'a':
                                            print(f"Running all tests in {selected_test_file_name_stripped}...")
                                            self.build(testbench_name)
                                            self.run_tests(group=testbench_name, test_module=selected_test_file_name_stripped, selected_testcases=cocotb_tests, top_level=self.Source_Files[testbench_name][0][suite_choice])
                                            print(suite_choice)
                                            break
                                        # Build and run singular test
                                        elif isinstance(test_choice, int):
                                            selected_test = str(cocotb_tests[test_choice])
                                            print(f"Running test: {selected_test}")
                                            self.build(testbench_name)
                                            self.run_tests(group=testbench_name, test_module=selected_test_file_name_stripped, selected_testcases=[selected_test], top_level=self.Source_Files[testbench_name][0][suite_choice])
                                            break
                                        else:
                                            print("Invalid choice. Please enter a valid number.")
                                else:
                                    print("Invalid choice. Please enter a valid number.")
                        else:
                            print(f"\nNo tests found for: {testbench_name}")
                    else:
                        print(f"No test suites found in {test_files_dir}.")
                else:
                    print(f"Testbench {testbench_path} does not exist. Make sure testbenches live in the same directory as this script and are titled 'testbench_<name>.")

if __name__ == "__main__":
    cocotb_runner = Cocotb_Runner()
    cocotb_runner.main()
