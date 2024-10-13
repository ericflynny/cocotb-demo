import os
import pytest
import cocotb.runner

class Cocotb_Runner():

    def __init__(self):
        self.test_groups: list[str] = ["spi"]
        self.ghdl = cocotb.runner.Ghdl()
        # Top level file must be first for build
        self.Source_Files = {
            "spi": ["spi_top_level.vhd", "spi_slave.vhd", "spi_master.vhd"]
        }
        os.environ["COCOTB_PDB_ON_EXCEPTION"] = "1"

    @staticmethod
    def find_test_files(directory: str):
        """Finds all files starting with 'test_' in the given directory and its subdirectories."""
        test_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.startswith("test_") and file.endswith((".py", ".vhd")):
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
    
    def print_available_test_groups(self):
        print("\nTest groups:")
        for i, group in enumerate(self.test_groups):
                print(f"{i+1}: {group}")

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


    def run_tests(self, group: str, test_module: str, selected_testcases: list[str]):
        cwd = os.getcwd()

        os.chdir(os.path.join(cwd, "vhdl", group))

        try:
            self.ghdl.test(test_module=f"tests.{group}.test_{test_module}",
                            testcase=selected_testcases,
                            hdl_toplevel=self.Source_Files[group][0].replace(".vhd", ""),  # Remove .vhd extension
                            waves=True,
                            gui=False,
                            plusargs=[f"--wave={group}_wave.ghw"]
                            )
        except Exception as e:
            print(f"Unable to run tests: {e}")

        os.chdir(cwd)

    def build(self, group: str):
        cwd = os.getcwd()

        os.chdir(os.path.join(cwd, "vhdl", group))

        try:
            self.ghdl.build(vhdl_sources=self.Source_Files[group],
                            hdl_toplevel=self.Source_Files[group][0].replace(".vhd", ""),  # Remove .vhd extension
                            clean=True,
                            log_file=f"{group}.log")
        except Exception as e:
            print(f"Unable to build {group}: {e}")

        print(f"Successfully built {group}\n")

        os.chdir(cwd)

    def main(self):
        """Main function to search for test files and cocotb tests."""
        current_dir = os.getcwd()

        while True:
            self.print_available_test_groups()
            group_choice = self.get_user_choice("Select a test group", self.test_groups)
            if group_choice == 'q':
                exit(code=0)
            elif isinstance(group_choice, int):
                test_group_dir = os.path.join(current_dir, "tests", self.test_groups[group_choice])
                test_group_name = os.path.basename(test_group_dir)
                if os.path.exists(test_group_dir):
                    test_files = self.find_test_files(test_group_dir)
                    if test_files:
                        tests_available = any(self.find_cocotb_tests(file) for file in test_files)
                        if tests_available:
                            while True:
                                print(f"\nTest suites in {test_group_name}:")
                                for i, file in enumerate(test_files):
                                    file_name = os.path.basename(file).replace("test_", "").replace(".py", "")
                                    cocotb_tests = self.find_cocotb_tests(file)
                                    test_indicator = " (NO TESTS)" if not cocotb_tests else ""
                                    print(f"{i+1}. {file_name}{test_indicator}")

                                suite_choice = self.get_user_choice("Select a test suite (b for back)", 
                                                                    test_files, allow_back=True)
                                if suite_choice == 'q':
                                    return
                                elif suite_choice == 'b':
                                    break 
                                elif isinstance(suite_choice, int):
                                    selected_file = test_files[suite_choice]
                                    selected_file_name = os.path.basename(selected_file).replace("test_", "").replace(".py", "")
                                    cocotb_tests = self.find_cocotb_tests(selected_file)

                                    while True:
                                        if not cocotb_tests:
                                            print(f"No tests found in {selected_file_name}.")
                                            break
                                        print(f"\nTests in {selected_file_name}:")
                                        for i, test in enumerate(cocotb_tests):
                                            print(f"{i+1}. {test}")
                                        test_choice = self.get_user_choice("Select a test (a for all, b for back)",
                                                                            cocotb_tests, allow_all=True, allow_back=True)
                                        if test_choice == 'q':
                                            return
                                        elif test_choice == 'b':
                                            break
                                        elif test_choice == 'a':
                                            print(f"Running all tests in {selected_file_name}...")
                                            self.build(test_group_name)
                                            self.run_tests(group=test_group_name, test_module=selected_file_name, selected_testcases=cocotb_tests)
                                            break
                                        elif isinstance(test_choice, int):
                                            selected_test = cocotb_tests[test_choice]
                                            print(f"Running test: {selected_test}")
                                            self.build(test_group_name)
                                            self.run_tests(group=test_group_name, test_module=selected_file_name, selected_testcases=[selected_test])
                                            break
                                        else:
                                            print("Invalid choice. Please enter a valid number.")
                                else:
                                    print("Invalid choice. Please enter a valid number.")
                        else:
                            print(f"\nNo tests found in: {test_group_name}")
                    else:
                        print(f"No test suites found in {test_group_dir}.")
                else:
                    print(f"Test group directory {test_group_dir} does not exist.")
            else:
                print("Invalid choice. Please enter a valid number.")

if __name__ == "__main__":
    cocotb_runner = Cocotb_Runner()
    cocotb_runner.main()
