
# Install required system packages
apt install -y \
	automake \
	build-essential \
	clang-14 \
	cmake \
	gcc \
	git \
	libboost-dev \
	libboost-thread-dev \
	libclang-dev \
	libgmp-dev \
	libntl-dev \
	libsodium-dev \
	libssl-dev \
	libtool \
	make \
	python3 \
	texinfo \
	yasm \
	openssl \
	libssl-dev \


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
