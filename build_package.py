"""Build clean portable ZIPs; excludes uploads, credentials and generated jobs."""
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
FILES = ['app.py', 'design.py', 'index.html', 'launch.py', 'build_package.py',
         'START_WINDOWS.bat', 'START_MAC_LINUX.command', 'HUONG_DAN.txt',
         'README.md', '.gitignore', 'tests/test_design.py',
         'assets/DejaVuSans.ttf', 'assets/DejaVuSans-Bold.ttf', 'assets/FONT_LICENSE.txt']

if __name__ == '__main__':
    output = ROOT / 'ReviewStudio-v0.2.zip'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as package:
        for name in FILES:
            package.write(ROOT / name, 'ReviewStudio/'+name)
    with zipfile.ZipFile(output) as package:
        assert package.testzip() is None
    shutil.copyfile(output, ROOT / 'ReviewStudio.zip')
    print(f'Created {output.name} and ReviewStudio.zip ({output.stat().st_size} bytes each)')
