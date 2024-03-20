import requests
import subprocess
import sys
import os


def search_aur_packages(keyword):
    base_url = 'https://aur.archlinux.org/rpc/v5/search/'
    search_url = base_url + keyword
    response = requests.get(search_url)
    response.raise_for_status()
    data = response.json()
    if data['type'] == 'search':
        return data['results']
    else:
        return None


def get_package_info(package_data):
    return {
        'name': package_data['Name'],
        'description': package_data['Description'],
        'url': f'https://aur.archlinux.org/{package_data["Name"]}.git',
    }


def display_package_info(packages):
    if not packages:
        print('No packages found.')
        return

    for package in packages:
        package_info = get_package_info(package)
        print(f'Name: {package_info["name"]}')
        print(f'Description: {package_info["description"]}')
        print(f'URL: {package_info["url"]}')
        print('-' * 50)


def choose_and_install_package(packages):
    if not packages:
        return

    while True:
        user_choice = input('Enter the package name to install (or "exit" to finish): ')
        if user_choice.lower() == 'exit':
            return

        found = False
        for package in packages:
            if package['Name'] == user_choice:
                package_info = get_package_info(package)
                repository_path = clone_and_install_package(package_info['url'])
                if repository_path:
                    print(f'Repository cloned and package installed: {repository_path}')
                else:
                    print(f'Failed to clone and install package: {package_info["name"]}')
                found = True
                break

        if found:
            break
        else:
            print('Package not found. Please try again.')


def clone_and_install_package(package_url):
    repository_path = f'cloned_packages/{os.path.basename(package_url[:-4])}'
    try:
        # Clone the repository
        subprocess.run(['git', 'clone', package_url, repository_path])

        # Change directory to the cloned repository
        os.chdir(repository_path)

        # Build and install the package
        subprocess.run(['makepkg', '-si'])

        # Remove the cloned directory
        os.chdir('../')
        os.rmdir(repository_path)

        return repository_path
    except Exception as e:
        print(f'Error cloning and installing package: {e}')
        return None


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python search_aur_packages.py <keyword>')
        sys.exit(1)

    package_name = sys.argv[1]
    packages = search_aur_packages(package_name)
    display_package_info(packages)
    choose_and_install_package(packages)
