import os
import warnings
from pathlib import Path

import pytest
from xprocess import ProcessStarter


def under_uwsgi():
    try:
        import uwsgi  # noqa: F401
    except ImportError:
        return False
    else:
        return True


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionfinish(session, exitstatus):
    if under_uwsgi():
        try:
            script_path = Path(os.environ["TMPDIR"], "return_pytest_exit_code.py")
        except KeyError:
            warnings.warn(
                "Pytest could not find tox 'TMPDIR' in the environment,"
                " make sure the variable is set in the project tox.ini"
                " file if you are running under tox."
            )
        else:
            with open(script_path, mode="w") as f:
                f.write(f"import sys; sys.exit({exitstatus})")
    yield


@pytest.fixture(scope="class")
def redis_server(xprocess):
    package_name = "redis"
    pytest.importorskip(
        modname=package_name, reason=f"could not find python package {package_name}"
    )

    class Starter(ProcessStarter):
        env = {"PYTHONUNBUFFERED": "1"}
        pattern = "[Rr]eady to accept connections"
        args = ["redis-server", "--port 6360"]

    # probably move this to a separate func if it works
    print("GITHUB_ACTIONS: ", os.getenv("GITHUB_ACTIONS"))

    if not os.getenv("GITHUB_ACTIONS"):
        xprocess.ensure(package_name, Starter)
        yield
        xprocess.getinfo(package_name).terminate()
    else:
        print(
            "Running under CI, process instances "
            "redis will not be started by xprocess"
        )


@pytest.fixture(scope="class")
def memcached_server(xprocess):
    package_name = "pylibmc"
    pytest.importorskip(
        modname=package_name, reason=f"could not find python package {package_name}"
    )

    class Starter(ProcessStarter):
        env = {"PYTHONUNBUFFERED": "1"}
        pattern = "server listening"
        args = ["memcached", "-vv"]

    xprocess.ensure(package_name, Starter)
    yield
    xprocess.getinfo(package_name).terminate()


class TestData:
    """This class centralizes all data samples used in tests"""

    sample_numbers = [0, 10, 1024000, 9, 5000000000000, 99, 738, 2000000]
    sample_pairs = {
        "128": False,
        "beef": True,
        "crevettes": {},
        "1024": "spam",
        "bacon": "eggs",
        "sausage": 2048,
        "3072": [],
        "brandy": [{}, "fried eggs"],
        "lobster": ["baked beans", [512]],
        "4096": {"sauce": [], 256: "truffle"},
    }
