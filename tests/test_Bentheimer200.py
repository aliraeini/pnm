"""Regression test of pnextract and pnflow on a 200^3 crop of the Bentheimer sandstone image of the Digital Porous Media
Portal (https://doi.org/10.17612/P77P49, see data/README.md): network extraction, drainage and imbibition at fixed contact
angles (water-wet and oil-wet), compared to the reference values in ref/ (single-phase results and summary values of the
Pc, Krw and Kro curves). The raw output of pnflow of a run (ref/<TITLE>_upscaled.tsv, _pnflow.prt) is kept beside them to look at.

* `python3 test_Bentheimer200.py` (or `pytest -v test_Bentheimer200.py`, or `make test`) runs the tests; needs pytest and pnmkit.
* `python3 test_Bentheimer200.py --update-refs` writes the reference files ref/<TITLE>_summary.txt: the mean of N_UPDATE runs of
  every case (pnflow is not strictly reproducible), and copies the raw output of the last run (ref/<TITLE>_upscaled.tsv, _pnflow.prt).
  For an existing summary file only its lines and tolerances are kept (delete the lines which should not be compared), a new
  file gets all values, with tolerances from the spread of the runs. Review the changes (`git diff ref/`) before committing.

Results are kept in $MS_TEST_DIR/pnm/Bentheimer200 (a temporary folder if MS_TEST_DIR is not set).
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

sys.dont_write_bytecode = True  # no generated files in the source folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
from conftest import HERE, case_dir, require_exe

import pnmkit
from pnmkit.runtime import read_scalar, run_sh

NAME = "Bent200"
VOXEL_SIZE = 3.0035e-6  # m

HEADER = f"""ObjectType = Image
NDims = 3
ElementType = MET_UCHAR
ElementByteOrderMSB = False
CompressedData = True
DimSize = 200 200 200
ElementSize = {VOXEL_SIZE} {VOXEL_SIZE} {VOXEL_SIZE}
Offset = 0 0 0
ElementDataFile = Bentheimer200.raw.gz
"""

# Common pnflow input: every test copies and edits it, sets TITLE (= OutputName, the names of the results) and EQUIL_CON_ANG
PNFLOW_INPUT = {
    "NETWORK": f"F {NAME}",
    "writeStatistics": "true",
    "RAND_SEED": "1002",  # pnflow seeds the random numbers with the time otherwise (the results still vary slightly)
    #            Final Sw   Final Pc   Sw steps   Compute Kr   Compute RI
    "cycle1": "0.00  5.00E+05  0.05  T  T",
    "cycle2": "1.00 -5.00E+05  0.05  T  T",
    #               Inject from  Produce from   Boundary-condition
    "cycle1_BC": "T F T T DP 1.00 2.00",
    "cycle2_BC": "T F T T DP 2.00 1.00",
    "CALC_BOX": "0.1 0.9",
    "INIT_CONT_ANG": "1 0 0 -0.2 -3.0 rand 0.0",  # fixed angle (min==max): reproducible
    "Water": "0.001 1.2 1000.0",
    "Oil": "0.001 1000.0 1000.0",
    "WaterOilInterface": "0.03",
}


def prepare_network(work_dir: Path) -> Path:
    """Image and header in work_dir, extract the pore network (pnextract)."""
    require_exe("pnextract")
    require_exe("pnflow")
    os.chdir(work_dir)
    shutil.copy(HERE / "data" / "Bentheimer200.raw.gz", work_dir)
    Path(f"{NAME}.mhd").write_text(HEADER)
    for f in Path(".").glob(f"{NAME}_*"):
        f.unlink()
    run_sh(".", f"pnextract {NAME}.mhd", logfile=Path("pnextract.log").open("wb"))
    return work_dir


@pytest.fixture(scope="module")
def network(tmp_path_factory):
    """The pore network of the image, in the work folder of the tests."""
    return prepare_network(case_dir("Bentheimer200", tmp_path=tmp_path_factory.mktemp("Bentheimer200")))


def read_blocks(fil: Path) -> list[np.ndarray]:
    """Tables (Sw Pc Krw Kro RI) of a pnflow *_upscaled.tsv file: one per cycle (the first block is the one-line header)."""
    blocks, cur = [], None
    for line in fil.read_text().splitlines():
        if line.startswith("//Sw"):
            cur = []
            blocks.append(cur)
            continue
        parts = line.split()
        if cur is not None and parts and parts[0][0] in "0123456789.-+":
            try:
                cur.append([float(x) for x in parts])
            except ValueError:
                pass
    return [np.array(b) for b in blocks if b]


def at(tab: np.ndarray, col: int, sw: float) -> float:
    """Value of column col (1: Pc, 2: Krw, 3: Kro) interpolated at saturation sw."""
    srt = tab[np.argsort(tab[:, 0])]
    return float(np.interp(sw, srt[:, 0], srt[:, col]))


def curve_values(tsv: Path) -> dict[str, float]:
    """The summary values of the curves (names as in the reference files) from the drainage (cycle 1) and imbibition (cycle 2) tables."""
    drn, imb = read_blocks(tsv)[:2]
    return {
        "Swirr (end of drainage)": drn[:, 0].min(),
        "drn Pc(Sw=0.9)": at(drn, 1, 0.9),
        "drn Pc(Sw=0.7)": at(drn, 1, 0.7),
        "drn Pc(Sw=0.15)": at(drn, 1, 0.15),
        "drn Pc(Sw=0.05)": at(drn, 1, 0.05),
        "drn Krw(Sw=0.9)": at(drn, 2, 0.9),
        "drn Kro(Sw=0.15)": at(drn, 3, 0.15),
        "drn Kro(Sw=0.05)": at(drn, 3, 0.05),
        "Sor (end of imbibition)": 1.0 - imb[:, 0].max(),
        "imb Krw(Sw=0.9)": at(imb, 2, 0.9),
        "imb Pc(Sw=0.4)": at(imb, 1, 0.4),
        "imb Kro(Sw=0.15)": at(imb, 3, 0.15),
        "imb Kro(Sw=0.05)": at(imb, 3, 0.05),
        "imb Pc(Sw=0.15)": at(imb, 1, 0.15),
        "imb Pc(Sw=0.75)": at(imb, 1, 0.75),
        "imb Pc(Sw=0.95)": at(imb, 1, 0.95),
        "imb Krw(Sw=0.75)": at(imb, 2, 0.75),
        "imb Krw(Sw=0.95)": at(imb, 2, 0.95),
        "imb Kro(Sw=0.4)": at(imb, 3, 0.4),
    }


@pytest.mark.regression
def test_pnextract(network):
    """The extracted network: number of pores and throats (and files)."""
    assert Path(f"{NAME}_node1.dat").is_file() and Path(f"{NAME}_link1.dat").is_file()
    assert read_scalar("pnextract.log", "nElems:") == 318  # 127 pores (2 are the inlet and outlet) + 191 throats
    n_throats = len(Path(f"{NAME}_link1.dat").read_text().split("\n")) - 2  # first line: number of throats
    assert n_throats == 191


REF_DIR = HERE / "ref"
DEFAULT_TOL = 0.03  # smallest relative tolerance of a new reference value
N_UPDATE = 12  # runs averaged to update a reference: pnflow is not strictly reproducible (the invasion order of equivalent
# elements changes between runs: the saturation steps and, in the middle of the curves, Krw vary)


def result_values(name: str) -> dict[str, float]:
    """All the values compared with the reference of the case <name>: single-phase results and summary values of the curves."""
    log, tsv = f"{name}_pnflow.log", Path(f"{name}_upscaled.tsv")
    vals = {key.rstrip(":"): read_scalar(log, key) for key in ("Number of pores:", "Number of throats:", "Total porosity:", "Formation factor:")}
    vals["Permeability (m2)"] = read_scalar(tsv, f"{name}_permeability:")
    vals.update(curve_values(tsv))
    return vals


def read_ref(fil: Path) -> dict[str, tuple[float, float]]:
    """Lines `name | value | relative tolerance` of a reference file."""
    ref = {}
    for line in fil.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            name, val, tol = (x.strip() for x in line.split("|"))
            ref[name] = (float(val), float(tol))
    return ref


def write_ref(fil: Path, vals: dict[str, float], tols: dict[str, float], header: str) -> None:
    lines = [f"# {header}", "# name | value | relative tolerance"]
    lines += [f"{name} | {val:.6g} | {tols.get(name, DEFAULT_TOL)}" for name, val in vals.items()]
    fil.parent.mkdir(exist_ok=True)
    fil.write_text("\n".join(lines) + "\n")


def run_pnflow(config: dict) -> dict[str, float]:
    """Runs pnflow with config; TITLE and OutputName set the names of the results, <name>_pnflow.log, <name>_upscaled.tsv ...,
    and of the reference file, ref/<name>_summary.txt, so every case has its own. Returns the values compared with the reference."""
    name = config["OutputName"]
    assert pnmkit.pnflow(dict(config)) in (0, None)
    assert Path(f"{name}_upscaled.tsv").is_file(), f"{name}_upscaled.tsv not written"
    return result_values(name)


def check_ref(config: dict) -> None:
    """Runs a case and compares the results with its reference file."""
    ref_file = REF_DIR / f"{config['OutputName']}_summary.txt"
    assert ref_file.is_file(), f"{ref_file} not found, create it by running `python3 {Path(__file__).name} --update-refs`"
    vals = run_pnflow(config)
    for key, (val, tol) in read_ref(ref_file).items():
        assert vals[key] == pytest.approx(val, rel=tol), f"{key} ({ref_file.name})"


def update_ref(config: dict) -> None:
    """Writes the reference file of a case: mean of N_UPDATE runs."""
    ref_file = REF_DIR / f"{config['OutputName']}_summary.txt"
    old = read_ref(ref_file) if ref_file.is_file() else {}  # lines and tolerances of an existing file are kept
    runs = [run_pnflow(config) for _ in range(N_UPDATE)]
    mean = {k: float(np.mean([r[k] for r in runs])) for k in (old or runs[0])}
    tols = {k: t for k, (_, t) in old.items()}
    for k in mean:  # new lines: twice the spread of the runs (at least DEFAULT_TOL, at most 25%)
        spread = (max(r[k] for r in runs) - min(r[k] for r in runs)) / (abs(mean[k]) + 1e-300)
        tols.setdefault(k, min(max(DEFAULT_TOL, round(2 * spread, 2)), 0.25))
    header = f"{config['OutputName']}: mean of {len(runs)} runs, written by `python3 test_Bentheimer200.py --update-refs`"
    write_ref(ref_file, mean, tols, header)
    name = config["OutputName"]
    for ext in ("_upscaled.tsv", "_pnflow.prt"):  # raw output of the last run, to look at (not compared: it varies between runs)
        shutil.copy(f"{name}{ext}", REF_DIR / f"{name}{ext}")
    print(f"wrote {ref_file}")


# The pnflow input of every case: the common PNFLOW_INPUT edited here (TITLE sets the names of the results and of the reference)
def input_ww() -> dict:
    """Water-wet after drainage (equilibrium contact angle 60)."""
    inp = dict(PNFLOW_INPUT)
    inp["TITLE"] = inp["OutputName"] = NAME + "ww"
    inp["EQUIL_CON_ANG"] = "1 60 60 -0.2 -3.0 rand 0.0"  # fixed angle (min==max): water-wet
    return inp


def input_ow() -> dict:
    """Oil-wet after drainage (equilibrium contact angle 120): water injection needs negative capillary pressures."""
    inp = dict(PNFLOW_INPUT)
    inp["TITLE"] = inp["OutputName"] = NAME + "ow"
    inp["EQUIL_CON_ANG"] = "1 120 120 -0.2 -3.0 rand 0.0"  # fixed angle (min==max): oil-wet
    return inp


@pytest.mark.regression
def test_pnflow_drainage_imbibition(network):
    """Water-wet: porosity, permeability, formation factor, Pc, Krw and Kro of drainage and spontaneous plus forced imbibition."""
    check_ref(input_ww())


@pytest.mark.regression
def test_pnflow_drainage_imbibition_ow(network):
    """Oil-wet: the same for contact angle 120 after drainage."""
    check_ref(input_ow())


if __name__ == "__main__":  # `python3 test_Bentheimer200.py` runs the tests, with --update-refs it writes the reference files
    if "--update-refs" in sys.argv[1:]:
        prepare_network(case_dir("Bentheimer200", tmp_path=Path(tempfile.mkdtemp())))
        for case_input in (input_ww, input_ow):
            update_ref(case_input())
    else:
        sys.exit(pytest.main(["-v", "-m", "regression", "-p", "no:cacheprovider", __file__]))
