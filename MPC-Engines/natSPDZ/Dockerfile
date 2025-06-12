FROM ubuntu:24.04

# run commands in an interactive shell (e.g., for `shopt`)
# SHELL ["/bin/bash", "-c"] 

# ==============================================================================
# <VARIABLES_FOLDERS-n-FILES===================================================>
## From Host
# ARG HOST_DATA_DIR="MP-SPDZ-Docker"
# ARG HOST_DATA_SRC="mpSPDZ_SRC_v0.4.0.zip"
#ARG HOST_DATA_FILE_CONFIG_MINE="$HOST_DATA_DIR/CONFIG.mine"
# TODO: check :: CONFIG.mine?

ARG HOST_DATA_SRC
ARG SRC_ZIP_FOLDER
ARG HOST_SHARE_DIR_LOGS
ARG HOST_SHARE_DIR_DATA

ARG b4M_PATCH_BaseMachine_CPP
ARG b4M_PATCH_BaseMachine_H
ARG BaseMachine_CPP_TARGET
ARG BaseMachine_H_TARGET

ARG FILE_INSTALL_MPSPDZ="mpSPDZ_install.sh"
ARG FILE_INSTALL_DEPENDENCIES="install_dependencies.sh"
ARG FILE_INSTALL_DEPENDENCIES_PROGRAMS="program_dependencies.sh"

## Inside Container
ENV HOME="/home"
WORKDIR $HOME

ENV WORK_DIR="$HOME/MP-SPDZ"
# </VARIABLES_FOLDERS-n-FILES==================================================>
# ==============================================================================

# ==============================================================================
# <GENERAL-DEPENDENCIES-n-PACKAGES=============================================>
RUN apt update && apt upgrade -y && apt autoclean
RUN apt install -y bash
RUN apt install -y vim
RUN apt install -y unzip
RUN apt install -y tree

# ADD $HOST_DATA_DIR/$FILE_INSTALL_DEPENDENCIES .
ADD $FILE_INSTALL_DEPENDENCIES .
RUN bash $FILE_INSTALL_DEPENDENCIES 
# </GENERAL-DEPENDENCIES-n-PACKAGES============================================>
# ==============================================================================

# ==============================================================================
# <MP-SPDZ>====================================================================>
RUN mkdir $WORK_DIR
WORKDIR $WORK_DIR

## add SRC
ADD $HOST_DATA_SRC $HOME
RUN unzip $HOME/$HOST_DATA_SRC -d $WORK_DIR
## make `mv` also move hidden files
RUN /bin/bash -c "shopt -s dotglob && mv $WORK_DIR/$SRC_ZIP_FOLDER/* $WORK_DIR/ && shopt -u dotglob"
RUN rmdir $WORK_DIR/$SRC_ZIP_FOLDER

## patch benchmarking output for b4M (:
ADD $b4M_PATCH_BaseMachine_CPP $WORK_DIR/$BaseMachine_CPP_TARGET
ADD $b4M_PATCH_BaseMachine_H $WORK_DIR/$BaseMachine_H_TARGET

# ADD $HOST_DATA_DIR/$FILE_INSTALL_MPSPDZ .
ADD $FILE_INSTALL_MPSPDZ .
RUN bash $FILE_INSTALL_MPSPDZ 
# RUN make -j 8 shamir
# RUN make -j 8 mascot
# RUN cp *.x /usr/local/bin
# RUN echo 1 2 3 4 > Player-Data/Input-P0-0
# RUN echo 1 2 3 4 > Player-Data/Input-P1-0
# RUN ./Scripts/compile-run.py -E mascot tutorial

# </MP-SPDZ>===================================================================>
# ==============================================================================

# ==============================================================================
# <NETWORK-CONFIG>=============================================================>
RUN apt install -y net-tools iproute2 
# COPY $HOST_DATA_FILE_NETWORK_SETUP_LAN $HOME
# COPY $HOST_DATA_FILE_NETWORK_SETUP_WAN $HOME
# RUN bash setup_network.sh 
# ...run when starting up the container; to have "cap_add=['NET_ADMIN']"
# </NETWORK-CONFIG>============================================================>
# ==============================================================================

# ==============================================================================
# <PROGRAM-DEPENDENCIES-n-PACKAGES=============================================>
ADD $FILE_INSTALL_DEPENDENCIES_PROGRAMS .
RUN bash $FILE_INSTALL_DEPENDENCIES_PROGRAMS
# </PROGRAM-DEPENDENCIES-n-PACKAGES============================================>
# ==============================================================================

# ==============================================================================
# <CONTAINER-CONFIG-n-STARTUP>=================================================>
## Provide log data to the host
RUN mkdir -p $WORK_DIR/$HOST_SHARE_DIR_LOGS
## Share certain (party) data with the host (program, input data, ...)
RUN mkdir -p $WORK_DIR/$HOST_SHARE_DIR_DATA
## Make sure to use "login" shell when running container
ENTRYPOINT ["/usr/bin/env", "bash", "-l", "-c"]
# </CONTAINER-CONFIG-n-STARTUP>================================================>
# ==============================================================================
