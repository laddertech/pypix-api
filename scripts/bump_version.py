import argparse
import re
from pathlib import Path


def get_current_version(file_path: str) -> str | None:
    """Extrai a versão atual do arquivo"""
    content = file_path.read_text()
    match = None

    if file_path.name == 'pyproject.toml':
        match = re.search(r'version\s*=\s*["\']([\d.]+)["\']', content)

    return match.group(1) if match else None


def update_version(file_path: str, new_version: str) -> None:
    """Atualiza a versão no arquivo"""
    content = file_path.read_text()
    new_content = content  # Default to original content if no match

    if file_path.name == 'pyproject.toml':
        new_content = re.sub(
            r'(version\s*=\s*["\'])[\d.]+(["\'])', rf'\g<1>{new_version}\g<2>', content
        )

    file_path.write_text(new_content)


def bump_version(version: str, part: str = 'patch') -> str:
    """Incrementa a versão de acordo com semantic versioning"""
    major, minor, patch = map(int, version.split('.'))

    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    return f'{major}.{minor}.{patch}'


def main() -> None:
    parser = argparse.ArgumentParser(description='Bump version in project files')
    parser.add_argument(
        'part',
        type=str,
        choices=['major', 'minor', 'patch'],
        help='Which part of version to bump',
    )
    args = parser.parse_args()

    # Arquivos que contém a versão
    files = [Path('pyproject.toml')]

    # Verifica se todos os arquivos existem
    for file in files:
        if not file.exists():
            print(f'Error: {file} not found')
            return

    # Pega a versão atual (usando setup.py como referência)
    current_version = get_current_version(files[0])
    if not current_version:
        print('Error: Could not determine current version')
        return

    # Calcula nova versão
    new_version = bump_version(current_version, args.part)
    print(f'Bumping version from {current_version} to {new_version}')

    # Atualiza todos os arquivos
    for file in files:
        update_version(file, new_version)
        print(f'Updated {file}')


if __name__ == '__main__':
    main()
