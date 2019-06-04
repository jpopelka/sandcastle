# MIT License
#
# Copyright (c) 2018-2019 Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from pathlib import Path

import pytest

from generator.deploy_openshift_pod import OpenshiftDeployer, MappedDir
from tests.conftest import SANDBOX_IMAGE, NAMESPACE, build_now, run_test_within_pod


def test_basic_e2e_inside():
    """ this part is meant to run inside an openshift pod """
    o = OpenshiftDeployer(
        image_reference=SANDBOX_IMAGE, k8s_namespace_name=NAMESPACE, pod_name="lllollz"
    )
    try:
        o.run(command=["ls", "-lha"])
    finally:
        o.delete_pod()


def test_local_path_e2e_inside_w_exec(tmpdir):
    m_dir = MappedDir()
    m_dir.local_dir = str(tmpdir.mkdir("stark"))
    m_dir.path = "/tmp/stark"

    p = Path(m_dir.local_dir)
    p.joinpath("qwe").write_text("Hello, Tony!")

    o = OpenshiftDeployer(
        image_reference=SANDBOX_IMAGE, k8s_namespace_name=NAMESPACE, mapped_dirs=[m_dir]
    )
    o.run()
    try:
        o.exec(command=["ls", "/tmp/stark/qwe"])
    finally:
        o.delete_pod()


@pytest.mark.parametrize(
    "test_name", ("test_basic_e2e_inside", "test_local_path_e2e_inside_w_exec")
)
def test_basic_e2e(test_name):
    """ initiate e2e: spawn a new openshift pod, from which every test case is being run """
    build_now()
    path = f"tests/e2e/test_ironman.py::{test_name}"
    run_test_within_pod(path)
