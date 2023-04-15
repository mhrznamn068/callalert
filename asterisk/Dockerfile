FROM ubuntu:20.04

LABEL maintainer="mhrznamn068@gmail.com"

ENV ASTERISK_VERSION="18"

ENV TZ=Asia/Kathmandu
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /opt/asterisk

RUN apt update && apt install -y software-properties-common \
    && add-apt-repository universe \
    && apt -y install git curl wget libnewt-dev libssl-dev libncurses5-dev subversion \
    libsqlite3-dev build-essential libjansson-dev libxml2-dev uuid-dev

ARG DEBIAN_FRONTEND=noninteractive

RUN apt policy asterisk \
    && wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-${ASTERISK_VERSION}-current.tar.gz \
    && tar xvf asterisk-18-current.tar.gz \
    && cd asterisk-${ASTERISK_VERSION}*/ && contrib/scripts/get_mp3_source.sh && contrib/scripts/install_prereq install \
    && ./configure 1> /dev/null \
    && make -j$(nproc) menuselect.makeopts \
    && menuselect/menuselect \
        --disable BUILD_NATIVE \
        --enable cdr_csv \
        --enable chan_sip \
        --enable res_snmp \
        --enable res_http_websocket \
    menuselect.makeopts \ 
    && make -j$(nproc) 1> /dev/null \
    && make -j$(nproc) install 1> /dev/null \
    && make -j$(nproc) progdocs 1> /dev/null \
    && make -j$(nproc) samples 1> /dev/null \
    && make -j$(nproc) config 1> /dev/null \
    && ldconfig \
    && make -j$(nproc) basic-pbx 1> /dev/null \
    && make -j$(nproc) dist-clean 1> /dev/null

COPY ./asterisk-config/pjsip.conf /etc/asterisk/pjsip.conf
COPY ./asterisk-config/sip.conf /etc/asterisk/sip.conf
COPY ./asterisk-config/modules.conf /etc/asterisk/modules.conf

RUN groupadd asterisk && useradd -r -d /var/lib/asterisk -g asterisk asterisk \
    && usermod -aG audio,dialout asterisk \
    && chown -R asterisk.asterisk /etc/asterisk \
    && chown -R asterisk.asterisk /var/lib/asterisk /var/log/asterisk /var/spool/asterisk /var/run/asterisk \
    && chown -R asterisk.asterisk /usr/lib/asterisk \
    && chmod -R 750 /var/lib/asterisk /var/log/asterisk /var/spool/asterisk \
       /var/run/asterisk /usr/lib/asterisk /etc/asterisk

RUN echo 'AST_USER="asterisk"' >> /etc/default/asterisk \
    && echo 'AST_GROUP="asterisk"' >> /etc/default/asterisk \
    && echo 'runuser = asterisk' >> /etc/asterisk/asterisk.conf \
    && echo 'rungroup = asterisk' >> /etc/asterisk/asterisk.conf

RUN apt install -y net-tools
COPY ./docker-init.sh docker-init.sh
RUN chmod +x docker-init.sh

USER asterisk
CMD ["./docker-init.sh"]
