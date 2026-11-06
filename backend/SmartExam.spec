from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ["desktop.py"],
    pathex=["."],
    datas=[("../frontend/dist", "frontend_dist")],
    hiddenimports=collect_submodules("uvicorn"),
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="SmartExam", console=False)
coll = COLLECT(exe, a.binaries, a.datas, name="SmartExam")