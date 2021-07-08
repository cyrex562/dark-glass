import sys
import subprocess

REQ_MAJ_VERS = 3
REQ_MIN_VERS = 9



def check_if_wg_is_installed():
    subprocess.run("wg show interfaces >/dev/null 2>&1", shell=True, check=True)

def detect_ext_net_if():
    if sys.platform.startswith('freebsd'):
        subprocess.run("route get default | awk '$1 == \"interface:\" { print $2 }'", shell=True, check=True)
    elif sys.platform.startswith('linux'):
        subprocess.run("ip route sh | awk '$1 == \"default\" && $2 == \"via\" { print $5; exit }'", shell=True, check=True)
    elif sys.platform.startswith('win32'):
        raise NotImplementedError("route detection failed")
    else:
        raise RuntimeError("platform not supported")
        
def run() -> int:

    if sys.version_info <= (3,9):
        raise RuntimeError("invalid python version")

    return 0



if __name__ == "__main__":
    sys.exit(run())