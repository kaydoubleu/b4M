
# Install required system packages
apt install -y \
	python3-sklearn \

# apt upgrade -y clang
apt upgrade -y
apt autoclean


# commands for clang-11:
# # Add the LLVM archive key (old key for Ubuntu)
# wget https://apt.llvm.org/llvm-snapshot.gpg.key
# sudo apt-key add llvm-snapshot.gpg.key

# # Add the correct repository manually
# echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal-11 main" | sudo tee /etc/apt/sources.list.d/llvm11.list

# # Update and install
# sudo apt update
# sudo apt install clang-11
