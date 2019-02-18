#!/usr/bin/env bash

SRV_FILE=hhk_jlcalc.service
sudo \cp -f ${SRV_FILE} /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ${SRV_FILE}
sudo systemctl restart ${SRV_FILE}
sudo systemctl status ${SRV_FILE}

