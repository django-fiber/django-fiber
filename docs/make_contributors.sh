#!/bin/bash

# regenerate contributors.txt from git contributors
# be sure to remove duplicates
git log --pretty='%aN <%aE>' | sort | uniq > contributors.txt
