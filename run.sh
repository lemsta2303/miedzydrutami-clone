#!/bin/bash

set -e

function check_and_stop_docker {
    if docker-compose ps | grep -q 'Up'; then
        echo -e "\033[1;34mrun.sh$ Stopping docker-compose...\033[0m"
        docker-compose down
    fi
}

if ! docker-compose ps | grep -q 'prestashop'; then
    echo -e "\033[1;34mrun.sh$ Starting PrestaShop...\033[0m"
    docker-compose up -d
else
    echo -e "\033[1;34mrun.sh$ PrestaShop is running\033[0m"
fi

if [ -d "./scraper/venv" ]; then
    echo -e "\033[1;34mrun.sh$ Removing existing virtual environment...\033[0m"
    rm -rf ./scraper/venv
fi

echo -e "\033[1;34mrun.sh$ Creating virtual environment...\033[0m"
python3 -m venv ./scraper/venv

source ./scraper/venv/bin/activate

# Ensure tqdm is installed
pip install tqdm > /dev/null 2>&1

missing_packages=$(comm -23 <(sort ./scraper/requirements.txt) <(pip freeze | sort) | tr '\n' ' ' | sed 's/ $//')

if [ -n "$missing_packages" ]; then
    echo -e "\033[1;34mrun.sh$ Missing packages:\033[0m"
    echo -e "\033[1;31mrun.sh$ $missing_packages\033[0m"
    read -p "Install missing packages? (Y/n) " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        IFS=' ' read -ra packages <<< "$missing_packages"
        echo -e "\033[1;34mrun.sh$ Installing packages...\033[0m"
        python - <<EOF
import subprocess
from tqdm import tqdm

packages = "${missing_packages}".split()
success_count = 0
failure_count = 0

for package in tqdm(packages, desc="Installing packages"):
    try:
        subprocess.run(["pip", "install", package], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        success_count += 1
    except subprocess.CalledProcessError:
        failure_count += 1

print(f"\033[1;34mrun.sh$ Packages installed successfully: {success_count}, Failures: {failure_count}\033[0m")
EOF
    else
        echo -e "\033[1;34mrun.sh$ Exiting\033[0m"
        check_and_stop_docker
        deactivate
        exit 1
    fi
fi

echo -e "\033[1;34mrun.sh$ Running data-scraper.py...\033[0m"
if ! python ./scraper/data-scraper.py; then
    echo -e "\033[1;31mrun.sh$ data-scraper.py failed\033[0m"
    check_and_stop_docker
    deactivate
    exit 1
fi

echo -e "\033[1;34mrun.sh$ Running data-import.py...\033[0m"
if ! python ./scraper/data-import.py; then
    echo -e "\033[1;31mrun.sh$ data-import.py failed\033[0m"
    check_and_stop_docker
    deactivate
    exit 1
fi

echo -e "\033[1;34mrun.sh$ Done. To stop PrestaShop, run 'docker-compose down'\033[0m"

deactivate