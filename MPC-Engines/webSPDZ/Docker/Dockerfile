FROM ubuntu:24.04

## Inside Container
ENV HOME="/home"
WORKDIR $HOME

ENV WORK_DIR="$HOME/webSPDZ"
# ARG HOST_DATA_DIR="webSPDZ-64-Docker"
# ARG HOST_DATA_DIR_SRC="$HOST_DATA_DIR/src"
ARG HOST_DATA_DIR_SRC="src"

RUN apt update
RUN apt upgrade -y
RUN apt install -y wget
RUN apt install -y bash
RUN apt install -y vim
RUN apt install -y nodejs
RUN apt install -y npm
RUN apt install -y python3
RUN apt install -y ipython3
RUN apt install -y pipenv
# RUN apt install -y python3-pip
# RUN apt install -y python3-selenium
# RUN apt install -y python3-webdriver_manager

RUN npm install websocket

# Network config
RUN apt install -y net-tools iproute2 lsof libasound2t64
RUN apt update --fix-missing

## Install .deb Firefox (due to issues with snap in Docker)
## ..inspired by: 
## ..https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04
## ..and: https://support.mozilla.org/en-US/kb/install-firefox-linux#w_install-firefox-deb-package-for-debian-based-distributions
### 1st, remove current (snap) firefox 
RUN apt remove firefox
### create APT keyring if one doesn't exist
RUN install -d -m 0755 /etc/apt/keyrings
RUN wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc #> /dev/null
RUN gpg -n -q --import --import-options import-show /etc/apt/keyrings/packages.mozilla.org.asc | awk '/pub/{getline; gsub(/^ +| +$/,""); if($0 == "35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3") print "\nThe key fingerprint matches ("$0").\n"; else print "\nVerification failed: the fingerprint ("$0") does not match the expected one.\n"}'
### add Mozilla signing key to sources.list
RUN echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list #> /dev/null
### prioritize .deb Firefox over the default one ('snap')
RUN echo '\n\
Package: *\n\
Pin: origin packages.mozilla.org\n\
Pin-Priority: 1000\n'\
 | tee /etc/apt/preferences.d/mozilla

RUN apt update
RUN apt install -y firefox

## Install .deb Chrome (due to issues with snap in Docker)
RUN mkdir $HOME/Chrome
WORKDIR $HOME/Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install -y ./google-chrome-stable_current_amd64.deb
WORKDIR $HOME

# ==============================================================================
# WORK DIR
RUN mkdir $WORK_DIR
WORKDIR $WORK_DIR

RUN pipenv install selenium
RUN pipenv install webdriver_manager

COPY $HOST_DATA_DIR_SRC "$WORK_DIR/"

ENTRYPOINT ["/usr/bin/env", "bash", "-l", "-c"]
