# coding=utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Gathers coverage data.
"""

import configparser
import io
import platform
import subprocess

from ..bot import JS_SHELL_DEFAULT_TIMEOUT
from ..js.loop import many_timed_runs
from ..util import create_collector
from ..util.logging_helpers import get_logger

LOG_COV_GATHERER = get_logger(__name__)
RUN_COV_TIME = 85000  # 85,000 seconds is just under a day


def gather_coverage(dirpath):
    """Gathers coverage data.

    Args:
        dirpath (Path): Directory in which build is to be downloaded in.

    Returns:
        Path: Path to the coverage results file
    """
    LOG_COV_GATHERER.info("Coverage build is being run in the following directory: %s", dirpath)
    bin_name = f'js{".exe" if platform.system() == "Windows" else ""}'
    cov_build_bin_path = dirpath / "cov-build" / "dist" / "bin" / bin_name
    assert cov_build_bin_path.is_file()
    loop_args = ["--compare-jit", "--random-flags",
                 str(JS_SHELL_DEFAULT_TIMEOUT), "KNOWNPATH", str(cov_build_bin_path), "--fuzzing-safe"]

    LOG_COV_GATHERER.info("Fuzzing a coverage build for %s seconds...", str(RUN_COV_TIME))
    many_timed_runs(RUN_COV_TIME, dirpath, loop_args, create_collector.make_collector(), True)
    LOG_COV_GATHERER.debug("Finished fuzzing the coverage build")

    fm_conf = configparser.ConfigParser()
    fm_conf.read(str(dirpath / "cov-build" / "dist" / "bin" / "js.fuzzmanagerconf"))
    LOG_COV_GATHERER.info("Generating grcov data...")
    cov_output = subprocess.run([str(dirpath / "grcov-bin" / "grcov"), str(dirpath),
                                 "-t", "coveralls+",
                                 "--commit-sha", fm_conf.get("Main", "product_version"),
                                 "--token", "NONE",
                                 "--guess-directory-when-missing",
                                 "-p", "/srv/jenkins/jobs/coverage-clone-mozilla-central/workspace/"],
                                check=True,
                                stdout=subprocess.PIPE).stdout.decode("utf-8", errors="replace")
    LOG_COV_GATHERER.debug("Finished generating grcov data")

    LOG_COV_GATHERER.info("Writing grcov data to disk...")
    cov_output_file = dirpath / "results_cov.json"
    with io.open(str(cov_output_file), "w", encoding="utf-8", errors="replace") as f:
        f.write(cov_output)
    LOG_COV_GATHERER.debug("Finished writing grcov data to disk")

    return cov_output_file
