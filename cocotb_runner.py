import os
import cocotb.runner


class Cocotb_Runner():
    def __init__(self):
        self.ghdl = cocotb.runner.Ghdl()
        # Top level file must be first for build
        cwd = os.getcwd()
        # Dictionary format -> Testbench name: (List of source files, Top level entity name)
        self.Source_Files = {
            # Testbench name
            "spi": ([
                f"{os.path.join(cwd, 'vhdl', 'spi', 'slave.vhd')}",
                f"{os.path.join(cwd, 'vhdl', 'spi', 'master.vhd')}",
                f"{os.path.join(cwd, 'vhdl', 'spi', 'top_level.vhd')}"],
                # Top level entity name
                "spi_top")
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
            print(f"{index + 1}: {testgroup}")

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
                exit(code=0)
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
        testcase_string = " ".join(selected_testcases)

        try:
            self.ghdl.test(test_module=f"tests.test_{test_module}",
                           testcase=testcase_string,
                           hdl_toplevel=self.Source_Files[group][1],
                           waves=True,
                           gui=False,
                           plusargs=[f"--wave={group}.ghw"],
                           build_dir=f"build_{group}",
                           # TODO: Update this to have a param passed in of whether to log to test file
                           # log_file=f"{group}_test.log"
                           )
        except Exception as e:
            print(f"Unable to run tests: {e}")

    def build(self, group: str):
        try:
            self.ghdl.build(vhdl_sources=self.Source_Files[group][0],
                            hdl_toplevel=self.Source_Files[group][1],
                            build_dir=f"build_{group}",
                            clean=True,
                            log_file=os.path.join(f"build_{group}", "build.log"))
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
                    test_files_dir = os.path.join(current_dir, "tests")
                    test_files = self.find_test_files(test_files_dir)

                    if test_files:
                        #  Assume only one test file for now.  Can expand if multi-file needed
                        test_file_path = test_files[0]
                        test_module_name = os.path.basename(test_file_path).replace("test_", "").replace(".py", "")
                        cocotb_tests = self.find_cocotb_tests(test_file_path)

                        while True:
                            if not cocotb_tests:
                                print(f"No tests found in {test_module_name}.")
                                break

                            print(f"\nTests in {test_module_name}:")
                            for i, test in enumerate(cocotb_tests):
                                print(f"{i + 1}. {test}")

                            test_choice = self.get_user_choice("Select a test (a for all, b for back)", cocotb_tests, allow_all=True)
                            if test_choice == 'q':
                                return
                            elif test_choice == 'a':
                                print(f"Running all tests in {test_module_name}...")
                                self.build(testbench_name)
                                self.run_tests(group=testbench_name, test_module=test_module_name, selected_testcases=cocotb_tests)
                                break
                            elif isinstance(test_choice, int):
                                selected_test = str(cocotb_tests[test_choice])
                                print(f"Running test: {selected_test}")
                                self.build(testbench_name)
                                self.run_tests(group=testbench_name, test_module=test_module_name, selected_testcases=[selected_test])
                                break
                            else:  # Handle 'b' for back implicitly
                                break

                    else:
                        print(f"No test files found in {test_files_dir}.")

                else:
                    print(f"Testbench {testbench_path} does not exist.")


if __name__ == "__main__":
    cocotb_runner = Cocotb_Runner()
    cocotb_runner.main()
