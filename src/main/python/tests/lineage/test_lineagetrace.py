# -------------------------------------------------------------
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# -------------------------------------------------------------

import warnings
import unittest
import os
import shutil
import sys
import re

path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../")
sys.path.insert(0, path)
from systemds.context import SystemDSContext

sds = SystemDSContext()

test_dir = os.path.join("tests", "lineage")
temp_dir = os.path.join(test_dir, "temp")

class TestLineageTrace(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning
        )

    def tearDown(self):
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning
        )

    def test_compare_trace1(self):  # test getLineageTrace() on an intermediate
        m = sds.full((10, 10), 1)
        m_res = m + m

        python_trace = [x.strip().split("°") for x in m_res.get_lineage_trace().split("\n")]

        dml_script = (
            "x = matrix(1, rows=10, cols=10);\n" 
            "y = x + x;\n" 
            "print(lineage(y));\n"
        )

        sysds_trace = create_execute_and_trace_dml(dml_script, "trace1")

        # It is not garantied, that the two lists 100% align to be the same.
        # Therefore for now, we only compare if the command is the same, in same order.
        python_trace_commands = [x[:1] for x in python_trace]
        dml_script_commands = [x[:1] for x in sysds_trace]
        self.assertListEqual(python_trace_commands, dml_script_commands)

# TODO add more tests cases.

def create_execute_and_trace_dml(script: str, name: str):
    script_file_name = temp_dir + "/" + name + ".dml"

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    with open(script_file_name, "w") as dml_file:
        dml_file.write(script)

    # Call SYSDS!
    result_file_name = temp_dir + "/" + name + ".txt"
    os.system("systemds.sh " + script_file_name + " > " + result_file_name)

    return parse_trace(result_file_name)

def parse_trace(path: str):
    pointer = 0
    data = []
    with open(path, "r") as log:
        for line in log:
            if pointer == 0:
                print(line)
            else:
                data.append(line.strip().split("°"))
            pointer += 1
    # Remove the last 3 lines of the System output because they are after lintrace.
    return data[:-3]

if __name__ == "__main__":
    unittest.main(exit=False)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Done")
    # sds.close()
